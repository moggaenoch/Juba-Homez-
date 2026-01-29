#!/usr/bin/env python3
import re
from pathlib import Path
import urllib.request
import urllib.error
import os

root = Path('/workspaces/Juba-Homez-')
pages = list((root / 'pages').rglob('*.html'))
pattern = re.compile(r'(?:(?:href|src)\s*=\s*["\'])([^"\']+)', re.I)
base_url = 'http://127.0.0.1:8000/'

not_found = {}

for html in pages:
    text = html.read_text(encoding='utf-8', errors='ignore')
    for m in pattern.findall(text):
        val = m.strip()
        if val.startswith(('http://','https://','//','mailto:','tel:','javascript:','#')):
            continue
        # normalize relative path to repo root
        candidate = (html.parent / val).resolve()
        try:
            rel = candidate.relative_to(root)
            rel_path = str(rel).replace('\\','/')
        except Exception:
            # if cannot relativize, try stripping leading ./
            rel_path = val.lstrip('./')
        url = base_url + rel_path
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=5) as resp:
                code = resp.getcode()
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:
            code = None
        if code != 200:
            key = f"{url} ({code})"
            not_found.setdefault(key, set()).add(str(html.relative_to(root)))

# print summary
print('404 Diagnostic Report')
print('Total broken URLs found:', len(not_found))
for url, refs in sorted(not_found.items()):
    print('\n'+url)
    for r in sorted(refs):
        print('  referenced in:', r)
