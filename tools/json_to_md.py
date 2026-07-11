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
    text = re.sub(r'\s', '-', text)
    return text


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


def check_duplicates(section, base_map, section_path):
    for word_obj in section.get('words', []):
        original_word = word_obj['word']
        base, tag_str = parse_word(original_word)
        base_lower = base.lower()

        if tag_str is None:
            tags = {None}
        else:
            tags = {t.strip().lower() for t in tag_str.split(',')}

        if base_lower in base_map:
            existing = base_map[base_lower]
            for t in tags:
                if t in existing:
                    print(f"⚠️ Duplicate base '{base}' (tag: {t}) for word '{original_word}' in {section_path}", file=sys.stderr)
                elif None in existing and t is not None:
                    print(f"⚠️ Duplicate base '{base}' (generic entry exists, adding specific tag '{t}') for word '{original_word}' in {section_path}", file=sys.stderr)
                elif t is None and existing:
                    print(f"⚠️ Duplicate base '{base}' (specific tags {existing} exist, adding generic entry) for word '{original_word}' in {section_path}", file=sys.stderr)
                else:
                    existing.add(t)
        else:
            base_map[base_lower] = tags

        mean_en = word_obj.get('mean_en', '')
        mean_fa = word_obj.get('mean_fa', '')
        if mean_fa and not has_persian(mean_fa):
            print(f"⚠️ No Persian in 'mean_fa' for '{word_obj['word']}' in {section_path}", file=sys.stderr)
        if mean_en and not has_english(mean_en):
            print(f"⚠️ No English in 'mean_en' for '{word_obj['word']}' in {section_path}", file=sys.stderr)

    for sub in section.get('subsections', []):
        check_duplicates(sub, base_map, f"{section_path} > {sub['heading']}")


def write_section(section, level, md_lines, toc_lines, level_offset=0):
    heading = section['heading']
    word_count = section['_word_count']
    display_heading = f"{heading} ({word_count} words)"

    base_len = 2 if level == 0 else 3
    prefix = '#' * (base_len + level_offset)
    md_lines.append(f"\n{prefix} {display_heading}\n")

    anchor = slugify(display_heading)
    indent = '  ' * (level + level_offset)
    toc_lines.append(f"{indent}- [{display_heading}](#{anchor})")

    for word_obj in section.get('words', []):
        phonetic = f' {word_obj["phonetic"]}' if word_obj.get('phonetic') else ''
        mean_en = word_obj.get('mean_en', '')
        mean_fa = word_obj.get('mean_fa', '')
        separator = ' - ' if mean_en and mean_fa else ''
        md_lines.append(f"- `   {word_obj['word']}   ` {phonetic} <br> {mean_en}")
        md_lines.append(f"{separator}{mean_fa}\n")

    for sub in section.get('subsections', []):
        write_section(sub, level + 1, md_lines, toc_lines, level_offset)

    if level == 0:
        md_lines.append("---\n")


def render_document(title, sections, total_words):
    md_lines = []
    toc_lines = []
    for sec in sections:
        write_section(sec, 0, md_lines, toc_lines)

    out = [f"# {title}\n\n", f"**Total words: {total_words}**\n\n", "## 📑 Table of Contents\n\n"]
    out.append('\n'.join(toc_lines))
    out.append("\n\n---\n")
    out.append(''.join(md_lines))
    return ''.join(out)


def load_json(json_path):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    total_words = 0
    for sec in data['sections']:
        total_words += compute_word_count(sec)
    return data, total_words


def main():
    if len(sys.argv) != 2:
        print("Usage: python json_to_md.py <vocabulary_directory>")
        sys.exit(1)

    dir_path = sys.argv[1]
    if not os.path.isdir(dir_path):
        print(f"Error: '{dir_path}' is not a directory")
        sys.exit(1)

    json_files = sorted(glob.glob(os.path.join(dir_path, '*.json')))
    if not json_files:
        print(f"No JSON files found in '{dir_path}'")
        sys.exit(1)

    base_map = {}
    loaded = []

    for json_path in json_files:
        data, total_words = load_json(json_path)
        for sec in data['sections']:
            check_duplicates(sec, base_map, f"{data['title']} > {sec['heading']}")
        loaded.append((json_path, data, total_words))

    for json_path, data, total_words in loaded:
        content = render_document(data['title'], data['sections'], total_words)
        md_path = json_path.replace('.json', '.md')
        with open(md_path, 'w', encoding='utf-8') as out:
            out.write(content)
        print(f"✅ Generated {md_path}")

    grand_total = sum(total_words for _, _, total_words in loaded)
    all_md_lines = []
    all_toc_lines = []

    for json_path, data, total_words in loaded:
        display_title = f"{data['title']} ({total_words} words)"
        all_md_lines.append(f"\n## {display_title}\n")
        anchor = slugify(display_title)
        all_toc_lines.append(f"- [{display_title}](#{anchor})")

        for sec in data['sections']:
            write_section(sec, 0, all_md_lines, all_toc_lines, level_offset=1)

        all_md_lines.append("\n---\n")

    all_path = os.path.join(dir_path, 'all.md')
    with open(all_path, 'w', encoding='utf-8') as out:
        out.write("# All Vocabulary\n\n")
        out.write(f"**Total words: {grand_total}**\n\n")
        out.write("## 📑 Table of Contents\n\n")
        out.write('\n'.join(all_toc_lines))
        out.write("\n\n---\n")
        out.write(''.join(all_md_lines))

    print(f"✅ Generated {all_path}")


if __name__ == "__main__":
    main()