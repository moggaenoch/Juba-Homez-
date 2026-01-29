#!/usr/bin/env python3
import os
from pathlib import Path

root = Path('/workspaces/Juba-Homez-')
pages_dir = root / 'pages'

changed_files = []
for path in pages_dir.rglob('*.html'):
    rel = path.relative_to(root)
    parts = rel.parts  # e.g., ('pages', 'public', 'Index.html')
    dir_count = len(parts) - 1
    # number of ../ needed to reach repo root
    prefix = '../' * dir_count
    desired = prefix + 'assets/'

    text = path.read_text(encoding='utf-8')
    new_text = text
    # Replace patterns like ../assets/ or ../../assets/ etc with desired
    import re
    new_text = re.sub(r'(?:\.{2}/)+assets/', desired, new_text)

    if new_text != text:
        backup = path.with_suffix(path.suffix + '.bak')
        backup.write_text(text, encoding='utf-8')
        path.write_text(new_text, encoding='utf-8')
        changed_files.append(str(rel))

print('Updated files:', len(changed_files))
for f in changed_files[:200]:
    print(f)
