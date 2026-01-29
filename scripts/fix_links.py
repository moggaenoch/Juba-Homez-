#!/usr/bin/env python3
import re
from pathlib import Path
import os

root = Path('/workspaces/Juba-Homez-')
pages_dir = root / 'pages'

changed = []

pattern = re.compile(r'(?P<prefix>\b(?:href|src)\s*=\s*)(?P<quote>["\'])(?P<path>[^"\']+)(?P=quote)', re.I)

for html in pages_dir.rglob('*.html'):
    text = html.read_text(encoding='utf-8')
    new_text = text
    def repl(m):
        orig = m.group(0)
        attr_prefix = m.group('prefix')
        quote = m.group('quote')
        val = m.group('path')
        # skip absolute or protocol or anchors
        if val.startswith(('http://','https://','//','mailto:','tel:','javascript:','#')):
            return orig
        # resolve candidate relative to current file
        candidate = (html.parent / val).resolve()
        if candidate.exists():
            return orig
        # try root-relative (strip leading ./)
        candidate2 = (root / val.lstrip('./')).resolve()
        if candidate2.exists():
            rel = os.path.relpath(candidate2, html.parent)
            return f"{attr_prefix}{quote}{rel}{quote}"
        # if path contains 'pages/', map to correct location under pages/
        if 'pages/' in val:
            tail = val.split('pages/',1)[1]
            candidate3 = (root / 'pages' / tail).resolve()
            if candidate3.exists():
                rel = os.path.relpath(candidate3, html.parent)
                return f"{attr_prefix}{quote}{rel}{quote}"
        # fallback: search for basename anywhere under repository
        basename = os.path.basename(val)
        matches = list(root.rglob(basename))
        if matches:
            target = matches[0].resolve()
            rel = os.path.relpath(target, html.parent)
            return f"{attr_prefix}{quote}{rel}{quote}"
        # no change
        return orig

    new_text = pattern.sub(repl, text)
    if new_text != text:
        bak = html.with_suffix(html.suffix + '.bak')
        bak.write_text(text, encoding='utf-8')
        html.write_text(new_text, encoding='utf-8')
        changed.append(str(html.relative_to(root)))

print('Updated', len(changed), 'files')
for p in changed:
    print(p)
