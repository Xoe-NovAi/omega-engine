import json
import re
from pathlib import Path

def extract_dpo_from_markdown(md_path: Path, output_path: Path):
    if not md_path.exists():
        print(f"Error: {md_path} not found.")
        return

    content = md_path.read_text(encoding="utf-8")
    
    # Robust Regex — handles label variants across frontier artifacts:
    #   - "**Naive response**:" (Opus) OR "**Naive**:" (synthesized hybrids)
    #   - "**Correct response**:" (Opus) OR "**Correct**:" (synthesized hybrids)
    #   - "**Why**:" OR "**Why the X matters**:" (Opus Pattern 6 variant)
    #   - Optional blank lines between fields (Opus) or none (hybrid)
    #   - Section end: next "###", a "---" divider, or end of file
    pattern = re.compile(
        r'### Pattern.*?\n+'
        r'\*\*Situation\*\*: (.*?)\n+'
        r'\*\*Naive(?: response)?\*\*: (.*?)\n+'
        r'\*\*Correct(?: response)?\*\*: (.*?)\n+'
        r'\*\*Why(?:[^*]*?)\*\*: (.*?)(?=\n###|\n---|\Z)',
        re.DOTALL | re.IGNORECASE
    )
    
    matches = pattern.findall(content)
    
    # Deduplicate by prompt to allow multi-document extraction without overlap
    seen_prompts = set()
    dpo_pairs = []
    for match in matches:
        situation, naive, correct, why = [m.strip().replace('\n', ' ') for m in match]
        
        prompt = f"Fix this situation: {situation}"
        if prompt in seen_prompts:
            continue
        seen_prompts.add(prompt)
        
        dpo_pair = {
            "prompt": prompt,
            "chosen": f"{correct}\n\nExplanation: {why}",
            "rejected": f"{naive}"
        }
        dpo_pairs.append(dpo_pair)
        
    if not dpo_pairs:
        print("No teaching patterns found matching the strict schema.")
        return

    with open(output_path, "a", encoding="utf-8") as f:
        for pair in dpo_pairs:
            f.write(json.dumps(pair) + "\n")
            
    print(f"Successfully extracted {len(dpo_pairs)} DPO pairs to {output_path}")

if __name__ == "__main__":
    sources = [
        Path("docs/sprints/f821-remediation/OPUS_STRATEGIC_GUIDE.md"),
        Path("docs/sprints/f821-remediation/HYBRID_STRATEGIC_GUIDE.md"),
    ]
    output_jsonl = Path("data/training/dpo_dataset.jsonl")
    # Fresh write (not append) — multi-source extraction with dedup
    if output_jsonl.exists():
        output_jsonl.unlink()
    for src in sources:
        extract_dpo_from_markdown(src, output_jsonl)
