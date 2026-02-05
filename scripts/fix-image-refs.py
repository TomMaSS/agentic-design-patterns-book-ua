#!/usr/bin/env python3
"""Fix duplicate image reference labels across markdown files.

When pandoc concatenates multiple .md files, reference-style image links
like [image1] collide if multiple files define the same label.
This script converts reference-style image links to inline image links.
"""

import re
import sys
from pathlib import Path

def fix_file(filepath: Path):
    text = filepath.read_text(encoding='utf-8')

    # Extract reference definitions: [image1]: path
    ref_pattern = re.compile(r'^\[([^\]]+)\]:\s*(.+)$', re.MULTILINE)
    refs = {}
    for match in ref_pattern.finditer(text):
        label = match.group(1)
        path = match.group(2).strip()
        refs[label] = path

    if not refs:
        return False

    # Replace usage: ![][image1] -> ![](path)
    # Also handles: ![alt text][image1] -> ![alt text](path)
    def replace_usage(match):
        alt = match.group(1)
        label = match.group(2)
        if label in refs:
            return f'![{alt}]({refs[label]})'
        return match.group(0)  # leave unchanged if no definition found

    text = re.sub(r'!\[([^\]]*)\]\[([^\]]+)\]', replace_usage, text)

    # Remove reference definitions
    text = ref_pattern.sub('', text)

    # Clean up trailing blank lines from removed definitions
    text = re.sub(r'\n{3,}$', '\n', text)

    filepath.write_text(text, encoding='utf-8')
    return True


def main():
    root = Path(__file__).parent
    md_files = list(root.rglob('*.md'))

    fixed = 0
    for f in sorted(md_files):
        if fix_file(f):
            print(f'Fixed: {f.relative_to(root)}')
            fixed += 1

    print(f'\nTotal files fixed: {fixed}')


if __name__ == '__main__':
    main()
