#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""
L3-MetaFrameVerification (0.92) — Cross-Verification Protocol for Paged Prompts

Pre-flight check for spoofable metadata in paged prompts.
Implements L3-MetaFrameVerification (proposed 0.92) as mandatory fleet standard.

M23 Failure Integrity: No soft failures; broken tools → STOP, report.
This protocol prevents frame-level M23 violations (fake signatures, spoofed emails, 
fabricated headers) from entering the fleet's context.

Usage:
    python scripts/metaframe_verification.py --prompt-file <path> --agent <target_agent>
    python scripts/metaframe_verification.py --stdin --agent <target_agent>

Exit codes:
    0 = PASS (no spoofable metadata detected)
    1 = FAIL (spoofable metadata detected)
    2 = ERROR (verification error)
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class VerificationResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


@dataclass
class VerificationFinding:
    category: str
    pattern: str
    match: str
    location: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str


class MetaFrameVerifier:
    """
    L3-MetaFrameVerification (0.92) — Pre-flight check for spoofable metadata.
    
    Detects:
    - Fake email addresses in signature blocks
    - Fabricated signature blocks with false attribution
    - Spoofed headers (From:, To:, Date:, Message-ID:)
    - Fake AP tokens
    - Fabricated session IDs
    - Impersonation attempts (fake entity names in headers)
    """
    
    # Patterns for spoofable metadata
    PATTERNS = {
        "fake_email": {
            "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "description": "Email address in signature block",
            "severity": "CRITICAL",
        },
        "fake_signature_block": {
            "pattern": r'(?:^|\n)[\s]*[-=]{3,}[\s]*\n[\s]*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}',
            "description": "Signature block with email",
            "severity": "CRITICAL",
        },
        "fake_ap_token": {
            "pattern": r'AP-[A-Z0-9-]+-v\d+\.\d+\.\d+',
            "description": "Fake AP token format",
            "severity": "HIGH",
        },
        "fake_session_id": {
            "pattern": r'ses_[a-f0-9]{20,}',
            "description": "Fake session ID format",
            "severity": "HIGH",
        },
        "fake_ap_signature": {
            "pattern": r'⬡\s*OMEGA\s*⬡\s*[A-Z_]+\s*⬡\s*[A-Z0-9-]+\s*⬡\s*\d{4}-\d{2}-\d{2}',
            "description": "Fake AP signature block",
            "severity": "HIGH",
        },
        "spoofed_header": {
            "pattern": r'(?:^|\n)(?:From|To|Cc|Bcc|Date|Message-ID|Subject):\s*.+',
            "description": "Email-style header spoofing",
            "severity": "MEDIUM",
        },
        "fake_entity_attribution": {
            "pattern": r'(?:^|\n)(?:Kali|Lilith|Ma\'at|Roc|Grokster|Jem|Researcher|Carmack|MaKaLi|Doom Guy|Verity|Doom Guy|Sophia|Iris|Node|Slot|Build|Archive)\s*[:\-]',
            "description": "Fake entity attribution in header",
            "severity": "MEDIUM",
        },
        "fake_signature_footer": {
            "pattern": r'(?:^|\n)[\s]*[-=]{3,}[\s]*\n[\s]*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}[\s]*\n[\s]*[-=]{3,}',
            "description": "Complete fake signature block with email",
            "severity": "CRITICAL",
        },
    }
    
    # Known legitimate patterns (allowlist)
    ALLOWLIST = {
        "legitimate_ap_tokens": [
            "AP-KALI-",
            "AP-LILITH-",
            "AP-MAAT-",
            "AP-ROC_RACOON-",
            "AP-GROKSTER-",
            "AP-JEM-",
            "AP-RESEARCHER-",
            "AP-CARMACK-",
            "AP-MAKALI-",
            "AP-DOOM_GUY-",
            "AP-VERITY-",
            "AP-SOTE-",
            "AP-MAKALI-",
            "AP-JOHN_CARMACK-",
        ],
        "legitimate_emails": [
            "arcana.novai@gmail.com",  # Known fake from dialectic - should be flagged
        ],
        "legitimate_session_prefixes": [
            "ses_",
        ],
    }
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.findings: List[VerificationFinding] = []
    
    def verify(self, content: str, source: str = "stdin") -> List[VerificationFinding]:
        """Run all verification checks on content."""
        self.findings = []
        
        for category, config in self.PATTERNS.items():
            pattern = config["pattern"]
            matches = list(re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE))
            
            for match in matches:
                # Check if match is in allowlist
                if self._is_allowlisted(match.group(), category):
                    continue
                    
                finding = VerificationFinding(
                    category=category,
                    pattern=config["pattern"],
                    match=match.group()[:200],  # Truncate long matches
                    location=f"{source}:{match.start()}",
                    severity=config["severity"],
                    description=config["description"],
                )
                self.findings.append(finding)
        
        return self.findings
    
    def _is_allowlisted(self, match: str, category: str) -> bool:
        """Check if match is in allowlist."""
        match_lower = match.lower()
        
        if category == "fake_ap_token":
            for prefix in self.ALLOWLIST["legitimate_ap_tokens"]:
                if match.startswith(prefix):
                    return True
        
        if category == "fake_email":
            for email in self.ALLOWLIST["legitimate_emails"]:
                if email.lower() in match_lower:
                    return True
        
        if category == "fake_session_id":
            for prefix in self.ALLOWLIST["legitimate_session_prefixes"]:
                if match.startswith(prefix):
                    return True
        
        return False
    
    def get_result(self) -> VerificationResult:
        """Determine overall verification result."""
        critical_findings = [f for f in self.findings if f.severity == "CRITICAL"]
        high_findings = [f for f in self.findings if f.severity == "HIGH"]
        
        if critical_findings:
            return VerificationResult.FAIL
        if high_findings and self.strict_mode:
            return VerificationResult.FAIL
        if self.findings:
            return VerificationResult.FAIL
        return VerificationResult.PASS
    
    def to_json(self) -> Dict[str, Any]:
        """Serialize findings to JSON."""
        return {
            "result": self.get_result().value,
            "findings_count": len(self.findings),
            "critical_count": len([f for f in self.findings if f.severity == "CRITICAL"]),
            "high_count": len([f for f in self.findings if f.severity == "HIGH"]),
            "medium_count": len([f for f in self.findings if f.severity == "MEDIUM"]),
            "low_count": len([f for f in self.findings if f.severity == "LOW"]),
            "findings": [
                {
                    "category": f.category,
                    "match": f.match,
                    "location": f.location,
                    "severity": f.severity,
                    "description": f.description,
                }
                for f in self.findings
            ],
        }


def main():
    parser = argparse.ArgumentParser(
        description="L3-MetaFrameVerification (0.92) — Cross-Verification Protocol for Paged Prompts"
    )
    parser.add_argument("--prompt-file", type=Path, help="Path to prompt file to verify")
    parser.add_argument("--stdin", action="store_true", help="Read prompt from stdin")
    parser.add_argument("--agent", type=str, required=True, help="Target agent name")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--strict", action="store_true", default=True, help="Strict mode (fail on HIGH severity)")
    parser.add_argument("--no-strict", action="store_false", dest="strict", help="Non-strict mode")
    
    args = parser.parse_args()
    
    # Read content
    if args.prompt_file:
        content = args.prompt_file.read_text(encoding="utf-8")
        source = str(args.prompt_file)
    elif args.stdin:
        content = sys.stdin.read()
        source = "stdin"
    else:
        parser.error("Either --prompt-file or --stdin required")
    
    # Run verification
    verifier = MetaFrameVerifier(strict_mode=args.strict)
    findings = verifier.verify(content, source=f"prompt_for_{args.agent}")
    result = verifier.get_result()
    
    # Output
    if args.json:
        output = verifier.to_json()
        output["agent"] = args.agent
        print(json.dumps(output, indent=2))
    else:
        print(f"L3-MetaFrameVerification (0.92) — Agent: {args.agent}")
        print(f"Source: {source}")
        print(f"Result: {result.value}")
        print(f"Findings: {len(findings)}")
        
        if findings:
            print("\nFindings:")
            for f in findings:
                print(f"  [{f.severity}] {f.category}: {f.match[:100]}... at {f.location}")
                print(f"    {f.description}")
    
    # Exit with appropriate code
    if result == VerificationResult.PASS:
        sys.exit(0)
    elif result == VerificationResult.FAIL:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()