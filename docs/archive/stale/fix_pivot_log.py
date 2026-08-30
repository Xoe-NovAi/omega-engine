# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

import re
from collections import defaultdict

def parse_pivot_log(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'^## Decision\s+', content, flags=re.MULTILINE)
    header = blocks[0]
    decision_blocks = blocks[1:]
    
    decisions = []
    for block in decision_blocks:
        match = re.match(r'(\d+)(?:\s+UPDATE)?:\s*(.*)', block)
        if match:
            num = int(match.group(1))
            title = match.group(2).split('\n')[0].strip()
            body = block[match.end():].strip()
            decisions.append({
                'num': num,
                'title': title,
                'body': body,
                'original_header': '## Decision ' + block.strip().split('\n')[0]
            })
    
    return header, decisions

def main():
    header, decisions = parse_pivot_log('docs/decisions/PIVOT_LOG.md')
    sorted_decisions = sorted(decisions, key=lambda x: x['num'])
    
    num_counts = defaultdict(int)
    for d in sorted_decisions:
        num_counts[d['num']] += 1
    
    current_counts = defaultdict(int)
    final_output = []
    registry_rows = []
    
    for d in sorted_decisions:
        num = d['num']
        title = d['title']
        body = d['body']
        
        # Determine display number
        display_num = str(num)
        if num_counts[num] > 1 and "UPDATE" not in d['original_header']:
            current_counts[num] += 1
            suffix = chr(64 + current_counts[num])
            display_num = f"{num}_{suffix}"
        
        # Extract date for registry
        date_match = re.search(r'\*\*Date\*\*:\s*([\d-]+)', body)
        date = date_match.group(1) if date_match else "Unknown"
        
        registry_rows.append(f"| {display_num} | {date} | {title} |")
        final_output.append(f"## Decision {display_num}: {title}\n\n{body}\n\n---")

    registry = "# Decision Registry\n\n| D# | Date | Summary |\n|---|---|---|\n" + "\n".join(registry_rows) + "\n\n---\n\n"
    
    with open('docs/decisions/PIVOT_LOG.md', 'w', encoding='utf-8') as f:
        f.write(registry)
        f.write("\n".join(final_output))

if __name__ == "__main__":
    main()
