#! ./venv/bin/python3
from collections import defaultdict
import wrong_to_right_map

mapping = wrong_to_right_map.name_mappings
md = defaultdict(list)

for key, val in mapping.items():
    md[val[0]].append((key, val))

wrong = input('Wrong Problem ID: ')
right = input('Right Problem ID: ')
md[wrong[0]].append((wrong, right))

with open('wrong_to_right_map.py', 'w') as f:
    f.write("name_mappings = {\n")
    first = True
    for key in sorted(md.keys()):
        if not first:
            f.write('\n')
        first = False
        for x, y in sorted(md[key], key=lambda t: t[1] + '-' + t[0]):
            f.write(f"    '{x}': '{y}',\n")
    f.write('}\n')
