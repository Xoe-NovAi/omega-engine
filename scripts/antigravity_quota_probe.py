#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
ag_quota_probe.py — Probe all 7 Antigravity accounts for live quota state.
Live execute this session to write data/metrics/antigravity_quotas.jsonl.

Output: one JSONL row per account with all model quota states.
"""
import json
import os
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

ACCOUNTS_FILE = Path.home() / ".config/opencode/antigravity-accounts.json"
OUT_FILE = Path.home() / "Documents/Xoe-NovAi/omega-engine/data/metrics/antigravity_quotas.jsonl"
CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
# M23 round-4 fix: was hardcoded GOCSPX-... — moved to env var to remove
# from version control. The hardcoded value is now in git history; the
# corresponding GCP OAuth client secret MUST be rotated at console.cloud.google.com
# (APIs & Services > Credentials > 1071006060591-... > Regenerate Secret).
# Track rotation in data/coordination/secret_rotation_log.yaml.
try:
    CLIENT_SECRET = os.environ["ANTIGRAVITY_CLIENT_SECRET"]
except KeyError:
    raise SystemExit(
        "FATAL: ANTIGRAVITY_CLIENT_SECRET env var is not set.\n"
        "       Export it before running: export ANTIGRAVITY_CLIENT_SECRET='GOCSPX-...'\n"
        "       To rotate: GCP Console > APIs & Services > Credentials > Regenerate Secret.\n"
        "       See data/coordination/secret_rotation_log.yaml for the rotation record."
    )
ANTIGRAVITY_ENDPOINT_PROD = "https://cloudcode-pa.googleapis.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Antigravity/1.18.3 Chrome/138.0.7204.235 Electron/37.3.1 Safari/537.36"

def http_post(url, body, headers):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def refresh_token(refresh_t):
    body = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_t,
        "grant_type": "refresh_token",
    }
    data = urllib.parse.urlencode(body).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    accounts = json.loads(ACCOUNTS_FILE.read_text())["accounts"]
    print(f"Probing {len(accounts)} Antigravity accounts...")
    out_records = []
    for idx, acc in enumerate(accounts):
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "idx": idx,
            "email": acc.get("email"),
            "enabled": acc.get("enabled"),
            "has_projectId": bool(acc.get("projectId")),
        }
        try:
            tokens = refresh_token(acc["refreshToken"])
            rec["access_token_len"] = len(tokens.get("access_token", ""))
            rec["refresh_ok"] = True
        except urllib.error.HTTPError as e:
            rec["refresh_ok"] = False
            rec["refresh_error"] = f"HTTP {e.code}: {e.read().decode('utf-8', errors='ignore')[:120]}"
            print(f"  [{idx}] {acc['email']} → REFRESH FAILED: {rec['refresh_error']}")
            out_records.append(rec)
            continue
        except Exception as e:
            rec["refresh_ok"] = False
            rec["refresh_error"] = str(e)[:120]
            print(f"  [{idx}] {acc['email']} → REFRESH ERR: {e}")
            out_records.append(rec)
            continue

        at = tokens["access_token"]
        headers = {
            "Authorization": f"Bearer {at}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        # loadCodeAssist for project
        try:
            lc = http_post(f"{ANTIGRAVITY_ENDPOINT_PROD}/v1internal:loadCodeAssist",
                           {"metadata": {"ideType": "ANTIGRAVITY", "platform": 1, "pluginType": "GEMINI"}},
                           headers)
            rec["project"] = lc.get("cloudaicompanionProject", "") or "DEFAULT_rising-fact-p41fc"
            rec["tier"] = (lc.get("currentTier") or {}).get("id", "?")
        except Exception as e:
            rec["project_error"] = str(e)[:120]
            rec["project"] = ""
            print(f"  [{idx}] {acc['email']} → loadCodeAssist FAILED: {e}")
            out_records.append(rec)
            continue

        # fetchAvailableModels
        try:
            fam_body = {"project": rec["project"]} if rec["project"] and rec["project"] != "DEFAULT_rising-fact-p41fc" else {}
            fam = http_post(f"{ANTIGRAVITY_ENDPOINT_PROD}/v1internal:fetchAvailableModels",
                            fam_body, headers)
            models_dict = fam.get("models", {})  # NOTE: it's a dict, not a list
            if isinstance(models_dict, dict):
                models = [{"id": k, **v} for k, v in models_dict.items()]
            else:
                models = models_dict
            rec["model_count"] = len(models)
            rec["models"] = []
            for m in models:
                if not isinstance(m, dict):
                    continue
                qi = m.get("quotaInfo") or {}
                rec["models"].append({
                    "id": m.get("id") or m.get("displayName"),
                    "remainingFraction": qi.get("remainingFraction"),
                    "resetTime": qi.get("resetTime"),
                })
            focus = [m for m in rec["models"] if any(k in (m["id"] or "") for k in ["claude", "gemini", "gpt-oss"])]
            print(f"  [{idx}] {acc['email']} → project={rec['project']}, {rec['model_count']} models ({len(focus)} key)")
            for m in focus[:6]:
                print(f"      {m['id']:36s} quota={m['remainingFraction']} reset={m['resetTime']}")
        except Exception as e:
            rec["quota_error"] = str(e)[:200]
            print(f"  [{idx}] {acc['email']} → fetchAvailableModels FAILED: {e}")

        out_records.append(rec)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w") as f:
        for rec in out_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nWrote {len(out_records)} records to {OUT_FILE}")

if __name__ == "__main__":
    main()
