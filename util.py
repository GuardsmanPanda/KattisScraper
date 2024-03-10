from functools import lru_cache

import util_ignore_files
import wrong_to_right_map
import sqlite3
import os
import re


def create_solution_cache():
    execute_query("""
        CREATE TABLE IF NOT EXISTS problem_cache(
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            difficulty_low FLOAT,
            difficulty_high FLOAT,
            description_length INTEGER,
            shortest_solution_length INTEGER,
            solution_status TEXT,
            solved_at TEXT,
            from_contest TEXT,
            created_at TEXT,
            last_seen_at TEXT
        )
    """)


def execute_query(query: str, *args):
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute(query, args)
    result = cur.fetchall()
    con.commit()
    con.close()
    return result


@lru_cache(maxsize=1000)
def get_all_unsolved() -> dict:
    return {tt[0]: tt for tt in execute_query("SELECT id, difficulty_high, name FROM problem_cache WHERE solution_status != 'Accepted'")}


part_removals = [
    'kattis_', 'kattis-', 'katttis_', '_kattis', '-sm', '-node', '_hcz', '_laurence', '_wally', '_lok'
] + list("_()-,'?^ +&)!=#")


@lru_cache(maxsize=10)
def get_all_problems(version=0) -> dict:
    res = {xx[0]: xx for xx in execute_query("SELECT id, difficulty_high, name, solution_status FROM problem_cache")}
    res2 = {}
    for k, v in res.items():
        name_match = v[2].lower()
        for part in part_removals:
            name_match = name_match.replace(part, '')
        if name_match not in res:
            res2[name_match] = v
    return res | res2


ignore_suffix = (
    '.md', '.out', '.in', '.txt', '.jpg', '.json', '.ans', '.class', '.zpts', 'html', 'css',
    '.sh', '.mod', '.png', '.toml', '.nix', '.yml', '.ignore', '.layout', '.fsproj',
    '.h', '.ipynb', '.lock', '.class', '.xml', '.pde', '.txt', '.wsf', '.yaml',
    'template.java', 'template.py', 'template.go',
)
ignore_directories = {
    'CTFs', 'incomplete', 'ICPC_2019',
    'KattisRSSParser', 'KattisRSSNotifier',
    'PO-Kattis',
    'repo-scripts',
    'scripts', 'Samples',
    'templates', 'template', 'test', 'todo', 'tests', 'TLE',
    'verbose',
}
ignore_files = util_ignore_files.ignore_files
name_mapping = wrong_to_right_map.name_mappings

if os.path.exists('problem_cache.db'):
    for x in get_all_problems():
        name_mapping[x] = x


def check_problem(text: str, directory_name=None) -> (str, float, str):
    if any(text.endswith(suffix) for suffix in ignore_suffix) or len(text) >= 60:
        return text, -1, 'Ignored'

    if directory_name is not None and directory_name in ignore_directories:
        return text, -1, 'Ignored'

    parts = text
    for part in part_removals:
        parts = parts.replace(part, '')
    parts = parts.split('.')
    name, ext = name_mapping[parts[0]] if parts[0] in name_mapping else parts[0], parts[-1]

    problems = get_all_problems(version=1)

    if name in problems:
        return problems[name][0], problems[name][1], 'Solved' if problems[name][3] == 'Accepted' else 'Unsolved'

    if len(name) < 3 or name.isdigit():
        return text, -1, 'Ignored'

    # Try to remove digits and add / remove 's'
    m = re.match(r'(\d*\D+)\d*$', name)
    if m is not None:
        name = name_mapping[m.group(1)] if m.group(1) in name_mapping else m.group(1)
    name = name_mapping[name[:-1]] if name[-1] == 's' and name[:-1] in name_mapping else name
    name = name_mapping[name + 's'] if name + 's' in name_mapping else name

    if name in problems:
        return problems[name][0], problems[name][1], 'Solved' if problems[name][3] == 'Accepted' else 'Unsolved'

    if name in ignore_files:
        return text, -1, 'Ignored'

    return name, -1, 'Unknown' if directory_name is not None else 'Ignored'
