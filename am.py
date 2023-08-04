#! ./venv/bin/python3
from collections import defaultdict

import util_ignore_files
import wrong_to_right_map

mapping = wrong_to_right_map.name_mappings
md = defaultdict(list)

for key, val in mapping.items():
    md[val[0]].append((key, val))

with open('wrong_to_right_map.py', 'w') as f:
    f.write("name_mappings = {\n")
    for key in sorted(md.keys()):
        if key != '1':
            f.write('\n')
        first = False
        for x, y in sorted(md[key], key=lambda t: t[1] + '-' + t[0]):
            f.write(f"    '{x}': '{y}',\n")
    f.write('}\n')

with open('util_ignore_files.py', 'w') as f:
    f.write("ignore_files = {\n")
    last = 'a'
    for key in sorted(util_ignore_files.ignore_files):
        if key[0] != last:
            f.write('\n')
            last = key[0]
        f.write(f"    '{key}',\n")
    f.write('}\n')
