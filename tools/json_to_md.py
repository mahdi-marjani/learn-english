import json
import sys
import re

PERSIAN_PATTERN = re.compile(r'[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]')

def has_persian(text):
    if not isinstance(text, str):
        return False
    return bool(PERSIAN_PATTERN.search(text))

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def compute_word_count(section):
    count = len(section.get('words', []))
    for sub in section.get('subsections', []):
        count += compute_word_count(sub)
    section['_word_count'] = count
    return count

if len(sys.argv) != 3:
    print("Usage: python json_to_md.py <input.json> <output.md>")
    sys.exit(1)

with open(sys.argv[1], encoding='utf-8') as f:
    data = json.load(f)

total_words = 0
for sec in data['sections']:
    total_words += compute_word_count(sec)

toc = []
lines = []
seen_words = set()

def write_section(section, level):
    heading = section['heading']
    word_count = section['_word_count']
    display_heading = f"{heading} ({word_count} words)"
    prefix = '##' if level == 0 else '###'
    lines.append(f"\n{prefix} {display_heading}\n")
    anchor = slugify(display_heading)
    toc.append('  ' * level + f"- [{display_heading}](#{anchor})")
    
    if 'words' in section:
        for w in section['words']:
            original_word = w['word']
            lower_word = original_word.lower()
            
            if lower_word in seen_words:
                print(f"⚠️ Warning: Duplicate word '{original_word}' (lowercase: '{lower_word}') found in section: {heading}", file=sys.stderr)
            else:
                seen_words.add(lower_word)
            
            w['word'] = lower_word
            
            phonetic = f' {w["phonetic"]}' if w.get('phonetic') else ''
            mean_separator = ' - ' if w.get('mean_en') and w.get('mean_fa') else ''
            lines.append(f"- **{w['word']}**{phonetic} : {w.get('mean_en', '')}")
            lines.append(f"{mean_separator}{w.get('mean_fa', '')}\n")
            
            mean_fa_val = w.get('mean_fa')
            if mean_fa_val and not has_persian(mean_fa_val):
                print(f"⚠️ Warning: No Persian characters in 'mean_fa' for word '{w['word']}' (section: {heading})", file=sys.stderr)
    
    if 'subsections' in section:
        for sub in section['subsections']:
            write_section(sub, level + 1)
    
    if level == 0:
        lines.append("---\n")

for sec in data['sections']:
    write_section(sec, 0)

with open(sys.argv[2], 'w', encoding='utf-8') as out:
    out.write(f"# {data['title']}\n\n")
    out.write(f"**Total words: {total_words}**\n\n")
    out.write(f"## 📑 Table of Contents\n\n")
    out.write('\n'.join(toc))
    out.write("\n\n---\n")
    out.write(''.join(lines))

print(f"✅ Generated {sys.argv[2]}")