# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import json
import re
import argparse
from pathlib import Path

def extract_dpo_from_markdown(md_path: Path, output_path: Path, metadata: dict):
    if not md_path.exists():
        print(f"Error: {md_path} not found.")
        return

    content = md_path.read_text(encoding="utf-8")
    
    pattern = re.compile(
        r'### Pattern.*?\n+'
        r'\*\*Situation\*\*: (.*?)\n+'
        r'\*\*Naive(?: response)?\*\*: (.*?)\n+'
        r'\*\*Correct(?: response)?\*\*: (.*?)\n+'
        r'\*\*Why(?:[^*]*?)\*\*: (.*?)(?=\n###|\n---|\Z)',
        re.DOTALL | re.IGNORECASE
    )
    
    matches = pattern.findall(content)
    
    seen_prompts = set()
    dpo_pairs = []
    for match in matches:
        situation, naive, correct, why = [m.strip().replace('\n', ' ') for m in match]
        
        prompt = f"Fix this situation: {situation}"
        if prompt in seen_prompts:
            continue
        seen_prompts.add(prompt)
        
        # Infer failure mode tag if not explicitly provided
        tag = metadata.get("failure_mode_tag")
        if not tag or tag == "auto":
            lower_prompt = prompt.lower()
            lower_correct = correct.lower()
            if "lazy import" in lower_prompt or "wrapper" in lower_prompt:
                tag = "lazy_import_wrapper_misuse"
            elif "inline" in lower_correct or "conditional" in lower_correct:
                tag = "inline_import_hoisting"
            elif "type_checking" in lower_correct or "forward reference" in lower_correct:
                tag = "type_checking_violation"
            elif "instructional" in lower_correct or "<--" in lower_correct:
                tag = "instructional_comment_contamination"
            elif "conflict" in lower_correct or "supersede" in lower_correct:
                tag = "multi_doc_merge_hallucination"
            else:
                tag = "general_remediation"
        
        pair_metadata = metadata.copy()
        pair_metadata["failure_mode_tag"] = tag

        dpo_pair = {
            "prompt": prompt,
            "chosen": f"{correct}\n\nExplanation: {why}",
            "rejected": f"{naive}",
            "metadata": pair_metadata
        }
        dpo_pairs.append(dpo_pair)
        
    if not dpo_pairs:
        print(f"No teaching patterns found matching the strict schema in {md_path}.")
        return

    with open(output_path, "a", encoding="utf-8") as f:
        for pair in dpo_pairs:
            f.write(json.dumps(pair) + "\n")
            
    print(f"Successfully extracted {len(dpo_pairs)} DPO pairs from {md_path.name} to {output_path.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract DPO pairs from markdown artifacts.")
    parser.add_argument("--active-model", default="nemotron-3-ultra-free", help="Target execution model")
    parser.add_argument("--thinking-level", default="high", help="Thinking level of the model")
    parser.add_argument("--context-usage", default="85%", help="Context window pressure")
    parser.add_argument("--provider", default="opencode", help="Inference provider")
    parser.add_argument("--failure-mode-tag", default="auto", help="Failure mode tag (auto-inferred if 'auto')")
    args = parser.parse_args()

    metadata = {
        "active_model": args.active_model,
        "thinking_level": args.thinking_level,
        "context_usage": args.context_usage,
        "provider": args.provider,
        "failure_mode_tag": args.failure_mode_tag
    }

    sources = [
        Path("docs/sprints/f821-remediation/OPUS_STRATEGIC_GUIDE.md"),
        Path("docs/sprints/f821-remediation/HYBRID_STRATEGIC_GUIDE.md"),
    ]
    output_jsonl = Path("data/training/dpo_dataset.jsonl")
    
    # Fresh write for testing extraction
    if output_jsonl.exists():
        output_jsonl.unlink()
        
    for src in sources:
        extract_dpo_from_markdown(src, output_jsonl, metadata)
