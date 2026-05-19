import json
import sys
import re

# Regular expressions to detect Persian and English characters
PERSIAN_PATTERN = re.compile(r'[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]')
ENGLISH_PATTERN = re.compile(r'[A-Za-z]')

def has_persian(text):
    """Return True if text contains Persian characters."""
    return isinstance(text, str) and bool(PERSIAN_PATTERN.search(text))

def has_english(text):
    """Return True if text contains English letters."""
    return isinstance(text, str) and bool(ENGLISH_PATTERN.search(text))

def slugify(text):
    """Convert text to a URL-friendly anchor string."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)  # remove punctuation
    text = re.sub(r'[\s-]+', '-', text)   # replace spaces with hyphens
    return text.strip('-')

def compute_word_count(section):
    """
    Recursively count all words in a section and its subsections.
    Stores the result in section['_word_count'].
    """
    count = len(section.get('words', []))
    for sub in section.get('subsections', []):
        count += compute_word_count(sub)
    section['_word_count'] = count
    return count

def parse_word(word_str):
    """
    Split a word like 'run (verb)' into base 'run' and tag 'verb'.
    If no parentheses, tag is None.
    """
    match = re.match(r'^(.*?)\s*\(([^)]+)\)$', word_str)
    if match:
        base = match.group(1).strip()
        tag = match.group(2).strip()
        return base, tag
    return word_str.strip(), None

def write_section(section, level, markdown_lines, table_of_contents, base_to_tags_map):
    """
    Convert a section (and its subsections) into markdown.
    level: 0 for top-level sections (## heading), 1 for subsections (### heading)
    """
    heading = section['heading']
    word_count = section['_word_count']
    display_heading = f"{heading} ({word_count} words)"
    prefix = '##' if level == 0 else '###'
    markdown_lines.append(f"\n{prefix} {display_heading}\n")

    # Build table of contents entry
    anchor = slugify(display_heading)
    indent = '  ' * level
    table_of_contents.append(f"{indent}- [{display_heading}](#{anchor})")

    # Write each word in this section
    for word_obj in section.get('words', []):
        original_word = word_obj['word']
        base, tag = parse_word(original_word)
        base_lower = base.lower()
        tag_key = tag.lower() if tag else None

        # Track duplicate base words (with different tags) and warn
        if base_lower in base_to_tags_map:
            existing_tags = base_to_tags_map[base_lower]
            # If existing has None (no tag) or tag_key already present or None, warn
            if (None in existing_tags) or (tag_key is None) or (tag_key in existing_tags):
                print(f"⚠️ Warning: Duplicate base '{base}' (existing tags: {existing_tags}, new tag: '{tag_key}') for word '{original_word}' in section: {heading}", file=sys.stderr)
            existing_tags.add(tag_key)
        else:
            base_to_tags_map[base_lower] = {tag_key}

        # Build phonetic part if present
        phonetic = f' {word_obj["phonetic"]}' if word_obj.get('phonetic') else ''
        # Build meaning lines
        mean_en = word_obj.get('mean_en', '')
        mean_fa = word_obj.get('mean_fa', '')
        separator = ' - ' if mean_en and mean_fa else ''
        markdown_lines.append(f"- **{word_obj['word']}**{phonetic} : {mean_en}")
        markdown_lines.append(f"{separator}{mean_fa}\n")

        # Validate meanings contain expected scripts
        if mean_fa and not has_persian(mean_fa):
            print(f"⚠️ Warning: No Persian characters in 'mean_fa' for word '{word_obj['word']}' (section: {heading})", file=sys.stderr)
        if mean_en and not has_english(mean_en):
            print(f"⚠️ Warning: No English characters in 'mean_en' for word '{word_obj['word']}' (section: {heading})", file=sys.stderr)

    # Recursively handle subsections
    for sub in section.get('subsections', []):
        write_section(sub, level + 1, markdown_lines, table_of_contents, base_to_tags_map)

    # Add a horizontal rule after each top-level section
    if level == 0:
        markdown_lines.append("---\n")

def main():
    if len(sys.argv) != 3:
        print("Usage: python json_to_md.py <input.json> <output.md>")
        sys.exit(1)

    # Load JSON data
    with open(sys.argv[1], encoding='utf-8') as f:
        data = json.load(f)

    # Count total words across all sections
    total_words = 0
    for sec in data['sections']:
        total_words += compute_word_count(sec)

    # Prepare containers for markdown generation
    markdown_lines = []          # stores the main content lines
    table_of_contents = []       # stores TOC entries
    base_to_tags_map = {}        # tracks base words and their tags to detect duplicates

    # Generate markdown for each top-level section
    for sec in data['sections']:
        write_section(sec, 0, markdown_lines, table_of_contents, base_to_tags_map)

    # Write final markdown file
    with open(sys.argv[2], 'w', encoding='utf-8') as out:
        out.write(f"# {data['title']}\n\n")
        out.write(f"**Total words: {total_words}**\n\n")
        out.write(f"## 📑 Table of Contents\n\n")
        out.write('\n'.join(table_of_contents))
        out.write("\n\n---\n")
        out.write(''.join(markdown_lines))

    print(f"✅ Generated {sys.argv[2]}")

if __name__ == "__main__":
    main()