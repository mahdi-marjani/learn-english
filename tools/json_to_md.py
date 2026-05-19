import json
import sys
import re
import os
import glob

PERSIAN_PATTERN = re.compile(r'[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]')
ENGLISH_PATTERN = re.compile(r'[A-Za-z]')

def has_persian(text):
    return isinstance(text, str) and bool(PERSIAN_PATTERN.search(text))

def has_english(text):
    return isinstance(text, str) and bool(ENGLISH_PATTERN.search(text))

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

def parse_word(word_str):
    match = re.match(r'^(.*?)\s*\(([^)]+)\)$', word_str)
    if match:
        base = match.group(1).strip()
        tag = match.group(2).strip()
        return base, tag
    return word_str.strip(), None

def write_section(section, level, md_lines, toc_lines, base_map, section_path):
    heading = section['heading']
    word_count = section['_word_count']
    display_heading = f"{heading} ({word_count} words)"
    prefix = '##' if level == 0 else '###'
    md_lines.append(f"\n{prefix} {display_heading}\n")

    anchor = slugify(display_heading)
    indent = '  ' * level
    toc_lines.append(f"{indent}- [{display_heading}](#{anchor})")

    for word_obj in section.get('words', []):
        original_word = word_obj['word']
        base, tag = parse_word(original_word)
        base_lower = base.lower()
        tag_key = tag.lower() if tag else None

        if base_lower in base_map:
            existing = base_map[base_lower]
            if (None in existing) or (tag_key is None) or (tag_key in existing):
                print(f"⚠️ Duplicate base '{base}' (existing tags: {existing}, new tag: '{tag_key}') for word '{original_word}' in {section_path}", file=sys.stderr)
            existing.add(tag_key)
        else:
            base_map[base_lower] = {tag_key}

        phonetic = f' {word_obj["phonetic"]}' if word_obj.get('phonetic') else ''
        mean_en = word_obj.get('mean_en', '')
        mean_fa = word_obj.get('mean_fa', '')
        separator = ' - ' if mean_en and mean_fa else ''
        md_lines.append(f"- **{word_obj['word']}**{phonetic} : {mean_en}")
        md_lines.append(f"{separator}{mean_fa}\n")

        if mean_fa and not has_persian(mean_fa):
            print(f"⚠️ No Persian in 'mean_fa' for '{word_obj['word']}' in {section_path}", file=sys.stderr)
        if mean_en and not has_english(mean_en):
            print(f"⚠️ No English in 'mean_en' for '{word_obj['word']}' in {section_path}", file=sys.stderr)

    for sub in section.get('subsections', []):
        write_section(sub, level + 1, md_lines, toc_lines, base_map, f"{section_path} > {sub['heading']}")

    if level == 0:
        md_lines.append("---\n")

def process_json_file(json_path, base_map):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    total_words = 0
    for sec in data['sections']:
        total_words += compute_word_count(sec)

    md_lines = []
    toc_lines = []

    for sec in data['sections']:
        write_section(sec, 0, md_lines, toc_lines, base_map, f"{data['title']} > {sec['heading']}")

    md_path = json_path.replace('.json', '.md')
    with open(md_path, 'w', encoding='utf-8') as out:
        out.write(f"# {data['title']}\n\n")
        out.write(f"**Total words: {total_words}**\n\n")
        out.write(f"## 📑 Table of Contents\n\n")
        out.write('\n'.join(toc_lines))
        out.write("\n\n---\n")
        out.write(''.join(md_lines))

    print(f"✅ Generated {md_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python json_to_md.py <vocabulary_directory>")
        sys.exit(1)

    dir_path = sys.argv[1]
    if not os.path.isdir(dir_path):
        print(f"Error: '{dir_path}' is not a directory")
        sys.exit(1)

    json_files = glob.glob(os.path.join(dir_path, '*.json'))
    if not json_files:
        print(f"No JSON files found in '{dir_path}'")
        sys.exit(1)

    base_map = {}
    for json_file in json_files:
        process_json_file(json_file, base_map)

if __name__ == "__main__":
    main()