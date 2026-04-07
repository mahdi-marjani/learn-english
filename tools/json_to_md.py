import json
import sys

if len(sys.argv) != 3:
    print("Usage: python json_to_md.py <input.json> <output.md>")
    sys.exit(1)

with open(sys.argv[1]) as f:
    data = json.load(f)

toc = []
lines = []

def write_section(section, level):
    heading = section['heading']
    prefix = '##' if level == 0 else '###'
    lines.append(f"\n{prefix} {heading}\n")
    anchor = heading.lower().replace(' ', '-').replace(':', '').replace(',', '')
    toc.append('  ' * level + f"- [{heading}](#{anchor})")
    if 'words' in section:
        for w in section['words']:
            lines.append(f"- **{w['word']}** {w['phonetic']} - {w['mean_en']}")
            lines.append(f"  {w['mean_fa']}\n")
    if 'subsections' in section:
        for sub in section['subsections']:
            write_section(sub, level + 1)
    if level == 0:
        lines.append("---\n")

for sec in data['sections']:
    write_section(sec, 0)

with open(sys.argv[2], 'w') as out:
    out.write(f"# {data['title']}\n\n## 📑 Table of Contents\n\n")
    out.write('\n'.join(toc))
    out.write("\n\n---\n")
    out.write(''.join(lines))

print(f"✅ Generated {sys.argv[2]}")