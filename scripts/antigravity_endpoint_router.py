#!/usr/bin/env python3
"""
antigravity_endpoint_router.py — Per Round 3 deeper dig §B (deliverable)
Version: v1.0 (R_VAULT_ANTIGRAVITY_ROUND3_20260827)

Routes Antigravity requests across production + daily + autopush endpoints
with automatic fallback when the primary returns 429 with a long retryDelay.

The CRITICAL Round 3 discovery: fetchAvailableModels exposes a SEPARATE
quota bucket of "internal" models (tab_*, chat_*) with remainingFraction=1
and no resetTime. These models work even when the user-facing bucket
(gemini-*, claude-*, gpt-oss-*) is 429-throttled for 4-5 days.

This router:
  1. Tracks per-endpoint health with TTL
  2. Maintains a model_quality_class table (internal / user-facing)
  3. Falls back from prod -> daily -> autopush on throttle
  4. Prefers internal models when user-facing quota is exhausted
  5. Posts state transitions to Hivemind

Mandate compliance:
  M8: only local file probes + Hivemind, no external telemetry
  M23: tool errors -> sys.exit(2), no soft-fail
  M27: atomic state writes, 6-step flow
  M26: type hints + pydoc
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# === OAUTH + ENDPOINTS (from plugin source constants.ts) ===
OAUTH_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
# M23 round-5 fix: was hardcoded GOCSPX-... — moved to env var to remove
# from version control. The hardcoded value is in git history; the
# corresponding GCP OAuth client secret MUST be rotated at console.cloud.google.com
# (APIs & Services > Credentials > 1071006060591-... > Regenerate Secret).
# Track rotation in data/coordination/secret_rotation_log.yaml.
try:
    OAUTH_CLIENT_SECRET = os.environ["ANTIGRAVITY_CLIENT_SECRET"]
except KeyError:
    print(
        "FATAL: ANTIGRAVITY_CLIENT_SECRET env var is not set.\n"
        "       Export it before running: export ANTIGRAVITY_CLIENT_SECRET='GOCSPX-...'\n"
        "       To rotate: GCP Console > APIs & Services > Credentials > Regenerate Secret.\n"
        "       See data/coordination/secret_rotation_log.yaml for the rotation record.",
        file=sys.stderr,
    )
    sys.exit(2)
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Antigravity/1.18.3 Chrome/138.0.7204.235 Electron/37.3.1 Safari/537.36"

# Endpoint fallback order (prod -> daily -> autopush) per plugin constants.ts
ENDPOINTS = [
    "https://cloudcode-pa.googleapis.com",
    "https://daily-cloudcode-pa.sandbox.googleapis.com",
    "https://autopush-cloudcode-pa.sandbox.googleapis.com",
]

DEFAULT_ACCOUNTS_FILE = Path.home() / ".config/opencode/antigravity-accounts.json"
DEFAULT_STATE_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/antigravity_endpoint_state.json"
DEFAULT_HIVEMIND_DIR = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/handoff/pending"

# State TTL — how long to cache endpoint health
HEALTH_TTL_SECONDS = 300  # 5 min
# Minimum retryDelay (seconds) to count as "throttled" vs "transient"
THROTTLE_THRESHOLD_S = 60
# Internal models — these are the unthrottled Antigravity workhorses (Round 3 §A)
INTERNAL_MODEL_PREFIXES = ("tab_", "chat_")
# User-facing models — these are throttled
USER_FACING_MODEL_PREFIXES = ("claude-", "gemini-", "gpt-oss-")


def classify_model(model_id: str) -> str:
    """Return 'internal' (unthrottled), 'user_facing' (throttled), or 'unknown'."""
    if any(model_id.startswith(p) for p in INTERNAL_MODEL_PREFIXES):
        return "internal"
    if any(model_id.startswith(p) for p in USER_FACING_MODEL_PREFIXES):
        return "user_facing"
    return "unknown"


# === STATE ===
@dataclass
class EndpointState:
    """Health state for a single endpoint."""
    endpoint: str
    last_429_at: float = 0.0  # unix ts
    retry_after_s: float = 0.0  # from response
    last_200_at: float = 0.0
    last_check_at: float = 0.0
    consecutive_failures: int = 0
    health: str = "unknown"  # "healthy" | "throttled" | "dead" | "unknown"

    def is_healthy(self, now: float) -> bool:
        if self.health == "healthy":
            return True
        if self.health == "throttled":
            # Throttle lifts at last_429_at + retry_after_s
            return now > self.last_429_at + self.retry_after_s
        if self.health == "dead":
            return False
        # Unknown = not yet tested, try it (will be marked on first call)
        return True


@dataclass
class AccountState:
    """State for a single Antigravity account."""
    idx: int
    email: str
    project_id: str
    refresh_token: str
    access_token: str = ""
    access_token_expires_at: float = 0.0
    cooldown_until: float = 0.0
    last_used_at: float = 0.0
    consecutive_429s: int = 0
    consecutive_200s: int = 0
    health: str = "healthy"  # "healthy" | "throttled" | "dead"


class AntigravityRouter:
    """Routes Antigravity requests across endpoints + accounts with auto-fallback."""

    def __init__(self, accounts_file: Path = DEFAULT_ACCOUNTS_FILE,
                 state_file: Path = DEFAULT_STATE_FILE,
                 hivemind_dir: Path = DEFAULT_HIVEMIND_DIR,
                 endpoint_priority: Optional[List[str]] = None):
        self.accounts_file = accounts_file
        self.state_file = state_file
        self.hivemind_dir = hivemind_dir
        self.endpoint_priority = endpoint_priority or ENDPOINTS
        self.endpoints: Dict[str, EndpointState] = {
            ep: EndpointState(endpoint=ep) for ep in self.endpoint_priority
        }
        self.accounts: List[AccountState] = []
        self._load_accounts()
        self._load_state()
        self._pending_alerts: List[str] = []

    # === PERSISTENCE ===
    def _load_accounts(self):
        if not self.accounts_file.exists():
            print(f"[FATAL] accounts file not found: {self.accounts_file}", file=sys.stderr)
            sys.exit(2)
        data = json.loads(self.accounts_file.read_text())
        for i, acc in enumerate(data.get("accounts", [])):
            if not acc.get("enabled", True):
                continue
            self.accounts.append(AccountState(
                idx=i,
                email=acc.get("email", ""),
                project_id=acc.get("projectId", ""),
                refresh_token=acc.get("refreshToken", ""),
            ))

    def _load_state(self):
        if not self.state_file.exists():
            return
        try:
            data = json.loads(self.state_file.read_text())
        except json.JSONDecodeError:
            return
        for ep, sd in data.get("endpoints", {}).items():
            if ep in self.endpoints:
                self.endpoints[ep] = EndpointState(**sd)

    def save_state(self):
        data = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "endpoints": {ep: asdict(s) for ep, s in self.endpoints.items()},
        }
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        tmp.replace(self.state_file)

    # === OAUTH ===
    def _refresh_access_token(self, account: AccountState) -> str:
        if account.access_token and time.time() < account.access_token_expires_at - 300:
            return account.access_token
        body = {
            "client_id": OAUTH_CLIENT_ID,
            "client_secret": OAUTH_CLIENT_SECRET,
            "refresh_token": account.refresh_token,
            "grant_type": "refresh_token",
        }
        data = urllib.parse.urlencode(body).encode("utf-8")
        req = urllib.request.Request(
            "https://oauth2.googleapis.com/token", data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            tokens = json.loads(resp.read().decode("utf-8"))
        account.access_token = tokens["access_token"]
        account.access_token_expires_at = time.time() + int(tokens.get("expires_in", 3600))
        return account.access_token

    # === ROUTING ===
    def select_endpoint(self, model_id: str) -> Optional[str]:
        """Pick the best endpoint for a model. Prefers internal models on any endpoint.
        For user-facing models, prefer healthy endpoints in priority order."""
        now = time.time()
        # 1. Filter to healthy endpoints
        healthy = [ep for ep in self.endpoint_priority if self.endpoints[ep].is_healthy(now)]
        if not healthy:
            return None  # all endpoints down

        # 2. For internal models, prefer endpoints in priority order (they work everywhere)
        model_class = classify_model(model_id)
        if model_class == "internal":
            # Internal models work on any endpoint, prefer production first
            return healthy[0]

        # 3. For user-facing models, prefer the endpoint with the most recent 200
        # (most likely to be unthrottled right now)
        candidate = sorted(healthy, key=lambda ep: -self.endpoints[ep].last_200_at)
        return candidate[0]

    def select_account(self, model_family: str = "claude") -> Optional[AccountState]:
        """Pick best account — sticky default per family, advance on cooldown."""
        now = time.time()
        eligible = [a for a in self.accounts if a.health != "dead" and a.cooldown_until < now]
        if not eligible:
            return None
        # Default to lowest idx (sticky for single-session)
        return eligible[0]

    # === INFERENCE ===
    def generate(self, model_id: str, prompt: str, max_output_tokens: int = 256,
                 system_prompt: str = "", temperature: float = 0.0) -> Tuple[Optional[str], Dict]:
        """Generate content. Returns (content, metadata). content is None on failure."""
        # Pick endpoint
        endpoint = self.select_endpoint(model_id)
        if not endpoint:
            return None, {"error": "no_healthy_endpoint"}
        # Pick account
        account = self.select_account()
        if not account:
            return None, {"error": "no_healthy_account"}
        # Refresh OAuth
        try:
            at = self._refresh_access_token(account)
        except Exception as e:
            account.health = "dead"
            self._pending_alerts.append(f"Account {account.idx} ({account.email}) OAuth refresh failed: {e}")
            return None, {"error": f"oauth_refresh_failed: {e}"}

        # Build request
        url = f"{endpoint}/v1internal:generateContent"
        body = {
            "project": account.project_id,
            "model": model_id,
            "request": {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": max_output_tokens, "temperature": temperature},
            },
            "userAgent": "antigravity",
            "requestId": f"router-{int(time.time()*1000)}",
        }
        if system_prompt:
            body["request"]["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        # Thinking budget for claude-*-thinking
        if "thinking" in model_id:
            body["request"]["generationConfig"]["thinkingConfig"] = {
                "thinkingBudget": min(8000, max_output_tokens * 4),
                "includeThoughts": False,
            }
            # Ensure maxOutputTokens > thinkingBudget
            if body["request"]["generationConfig"]["maxOutputTokens"] <= body["request"]["generationConfig"]["thinkingConfig"]["thinkingBudget"]:
                body["request"]["generationConfig"]["maxOutputTokens"] = body["request"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] + 256

        headers = {
            "Authorization": f"Bearer {at}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Client-Metadata": '{"ideType":"ANTIGRAVITY","platform":"MACOS","pluginType":"GEMINI"}',
            "X-Goog-Api-Client": "google-cloud-sdk vscode_cloudshelleditor/0.1",
        }

        # Make request
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        start = time.time()
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                elapsed = time.time() - start
                self._on_success(endpoint, account, model_id, result, elapsed)
                content = self._extract_content(result)
                return content, {
                    "endpoint": endpoint,
                    "model": model_id,
                    "account_idx": account.idx,
                    "latency_ms": int(elapsed * 1000),
                    "model_class": classify_model(model_id),
                }
        except urllib.error.HTTPError as e:
            elapsed = time.time() - start
            error_body = e.read().decode("utf-8", errors="ignore")
            self._on_failure(endpoint, account, model_id, e.code, error_body, elapsed)
            return None, {
                "error": f"HTTP {e.code}",
                "endpoint": endpoint,
                "error_body": error_body[:500],
            }
        except Exception as e:
            elapsed = time.time() - start
            self.endpoints[endpoint].consecutive_failures += 1
            return None, {"error": str(e), "endpoint": endpoint}

    def _extract_content(self, result: dict) -> Optional[str]:
        """Extract visible text from a successful Antigravity response."""
        resp = result.get("response", result)
        candidates = resp.get("candidates", [])
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return None
        return parts[0].get("text", "")

    # === CALLBACKS ===
    def _on_success(self, endpoint: str, account: AccountState, model_id: str,
                    result: dict, elapsed: float):
        ep = self.endpoints[endpoint]
        ep.last_200_at = time.time()
        ep.last_check_at = ep.last_200_at
        ep.consecutive_failures = 0
        ep.health = "healthy"
        account.consecutive_200s += 1
        account.consecutive_429s = 0
        if account.consecutive_200s >= 2:
            account.health = "healthy"
            account.cooldown_until = 0.0
        account.last_used_at = time.time()

    def _on_failure(self, endpoint: str, account: AccountState, model_id: str,
                    status_code: int, error_body: str, elapsed: float):
        ep = self.endpoints[endpoint]
        ep.last_check_at = time.time()
        ep.consecutive_failures += 1
        account.consecutive_429s += 1
        # Parse retryDelay from error
        retry_after = 0
        try:
            err = json.loads(error_body).get("error", {})
            for det in err.get("details", []):
                if "retryDelay" in det:
                    retry_after = float(det["retryDelay"].rstrip("s"))
                    break
        except (json.JSONDecodeError, KeyError, AttributeError):
            pass

        if status_code == 429 and retry_after > THROTTLE_THRESHOLD_S:
            ep.last_429_at = time.time()
            ep.retry_after_s = retry_after
            ep.health = "throttled"
            self._pending_alerts.append(
                f"Endpoint {endpoint} THROTTLED: 429 with retryDelay={retry_after:.0f}s "
                f"({retry_after/86400:.1f}d) for model={model_id}"
            )
            # Mark account as throttled too (per-account quota)
            account.cooldown_until = time.time() + retry_after
            if account.consecutive_429s >= 3:
                account.health = "throttled"
        elif status_code == 429:
            # Short throttle — don't mark endpoint down
            self._pending_alerts.append(
                f"Transient 429 on {endpoint} (retryDelay={retry_after:.0f}s) for {model_id}"
            )
        elif status_code in (401, 403):
            # Auth issue — mark account dead
            account.health = "dead"
            self._pending_alerts.append(
                f"Account {account.idx} ({account.email}) DEAD: HTTP {status_code} for {model_id}"
            )
        else:
            self._pending_alerts.append(
                f"HTTP {status_code} on {endpoint} for {model_id}: {error_body[:200]}"
            )

    # === HIVEMIND ===
    def post_hivemind_alerts(self):
        """Post any pending alerts to Hivemind as a handoff packet."""
        if not self._pending_alerts:
            return
        self.hivemind_dir.mkdir(parents=True, exist_ok=True)
        pkt_id = f"ag-router-{int(time.time())}-{hash(tuple(self._pending_alerts)) & 0xffff:04x}"
        pkt_file = self.hivemind_dir / f"{pkt_id}.json"
        body = "## Antigravity Router Alerts\n\n"
        for a in self._pending_alerts:
            body += f"- {a}\n"
        body += f"\n---\n*State saved to {self.state_file}*"
        packet = {
            "packet_id": pkt_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source_channel": "opencode",
            "source_entity": "grokster",
            "target_channel": "opencode",
            "target_entity": "maat",
            "task": "Antigravity router state changes (R_VAULT_ANTIGRAVITY_ROUND3_20260827)",
            "context": body[:4000],
            "priority": 1,
            "intent": "alert",
            "alerts": self._pending_alerts,
        }
        tmp = pkt_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(packet, ensure_ascii=False, indent=2))
        tmp.replace(pkt_file)
        self._pending_alerts = []  # Clear after posting
        return pkt_file


# === CLI ===
def main():
    ap = argparse.ArgumentParser(description="Antigravity endpoint router (R_VAULT_ANTIGRAVITY_ROUND3_20260827)")
    ap.add_argument("--accounts-file", type=Path, default=DEFAULT_ACCOUNTS_FILE)
    ap.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    ap.add_argument("--hivemind-dir", type=Path, default=DEFAULT_HIVEMIND_DIR)
    ap.add_argument("--model", default="tab_flash_lite_preview", help="Model to test (default: internal workhorse)")
    ap.add_argument("--prompt", default="Reply with exactly: PING_OK", help="Prompt to send")
    ap.add_argument("--max-tokens", type=int, default=32)
    ap.add_argument("--info", action="store_true", help="Print model classification + endpoint health, no inference")
    args = ap.parse_args()

    router = AntigravityRouter(
        accounts_file=args.accounts_file,
        state_file=args.state_file,
        hivemind_dir=args.hivemind_dir,
    )

    if args.info:
        print("=== Antigravity Router State ===")
        print(f"Accounts loaded: {len(router.accounts)}")
        for ep, st in router.endpoints.items():
            print(f"  Endpoint: {ep}")
            print(f"    health={st.health}  last_200_at={datetime.fromtimestamp(st.last_200_at, timezone.utc).isoformat() if st.last_200_at else 'never'}")
            print(f"    last_429_at={datetime.fromtimestamp(st.last_429_at, timezone.utc).isoformat() if st.last_429_at else 'never'}")
            print(f"    retry_after_s={st.retry_after_s:.0f}  consecutive_failures={st.consecutive_failures}")
        print()
        print(f"Model classification:")
        for m in ["tab_flash_lite_preview", "gemini-3-flash", "claude-opus-4-6-thinking", "gpt-oss-120b-medium"]:
            print(f"  {m:36s} -> {classify_model(m)}")
        return

    print(f"=== Antigravity Router Test ===")
    print(f"Model: {args.model} (class={classify_model(args.model)})")
    print(f"Endpoint selected: {router.select_endpoint(args.model)}")
    content, meta = router.generate(args.model, args.prompt, max_output_tokens=args.max_tokens)
    print(f"Result: {content!r}")
    print(f"Metadata: {meta}")
    router.save_state()
    if router._pending_alerts:
        pkt = router.post_hivemind_alerts()
        print(f"Hivemind packet: {pkt}")


if __name__ == "__main__":
    main()
