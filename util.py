from functools import lru_cache
import wrong_to_right_map
import sqlite3
import os
import re


def create_solution_cache():
    if os.path.exists('problem_cache.db'):
        return
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute("""
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
    con.commit()
    con.close()


def get_all_from_query(query: str):
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute(query)
    return cur.fetchall()


@lru_cache(maxsize=1000)
def get_all_unsolved() -> dict:
    return {tt[0]: tt for tt in get_all_from_query("SELECT id, difficulty_high, name FROM problem_cache WHERE solution_status != 'Accepted'")}


part_removals = ['kattis_', 'katttis_', '-sm', '-node'] + list("_()-,'?^ +&)!=#")


@lru_cache(maxsize=1000)
def get_all_problems() -> dict:
    res = {xx[0]: xx for xx in get_all_from_query("SELECT id, difficulty_high, name, solution_status FROM problem_cache")}
    res2 = {}
    for k, v in res.items():
        name_match = v[2].lower()
        for part in part_removals:
            name_match = name_match.replace(part, '')
        if name_match not in res:
            res2[name_match] = v
    return res | res2


ignore_extensions = ['md', 'out', 'in', 'txt', 'jpg', 'json', 'ans', 'sh', 'mod', 'png', 'toml', 'nix', 'yml', 'ignore',
                     'h', 'ipynb', 'lock', 'class']
ignore_directories = {
    '_meta',
    'heads', 'hooks',
    'info', 'incomplete', 'ICPC_2019',
    'KattisRSSParser', 'KattisRSSNotifier',
    'logs',
    'origin',
    'pack', 'PO-Kattis',
    'repo-scripts',
    'scripts',
    'templates', 'template', 'test', 'todo', 'tests',
    'verbose',
}
ignore_files = {
    'authors', 'acc', 'answer',
    'build', 'buildwiki', 'breadthfirstsearch', 'bnnaccuracy', 'brutebrute', 'branches',
    'comp', 'check', 'contest4solutions', 'c++', 'completed',
    'directoryreader', 'deque', 'djikstra', 'datetime',
    'error', 'easy',
    'generatereadme',
    'hooks', 'heads', 'hard',
    'in', 'info', 'incomplete', 'input',
    'java', 'jbuild',
    'kattio', 'kattis',
    'license', 'logs',
    'main', 'makefile', 'matrixmult', 'medium',
    'node',
    'output', 'oops', 'objects', 'origin', 'openkattis',
    'pair', 'point2d', 'pack', 'python',
    'readmegenerator', 'refs', 'remotes',
    'scrapper', 'sticky', 'secret', 'stringhashing', 'solutions', 'src', 'sol', 'solution',
    'testgen', 'test', 'template', 'testingtool', 'tle', 'tempcoderunnerfile', 'tags',
    'version',
    'wronganswer', 'why',

    # Old problems?
    'androids', 'alphabetical',
    'casual', 'cesta',
    'duplicates',
    'happytrails',
    'iterm',
    'monstertruck',
    'neolexicographicordering',
    'primedrive', 'plantina', 'psenica',
    'runningrace', 'reverse',
    'spanavac',
}
ignore_file_parts = [
    'noi2020', 'neo-',
    'scl2022', 'scl2021',
    'vjudge',
]

name_mapping = wrong_to_right_map.name_mappings

for x in get_all_problems():
    name_mapping[x] = x


def check_problem(text: str, directory_name=None) -> (str, float, str):
    if len(text) >= 38 or text.startswith('.') or (directory_name is not None and directory_name.startswith('.')):
        return text, -1, 'Ignored'

    if directory_name is not None and directory_name in ignore_directories:
        return text, -1, 'Ignored'

    parts = text
    for part in part_removals:
        parts = parts.replace(part, '')
    parts = parts.split('.')
    name, ext = name_mapping[parts[0]] if parts[0] in name_mapping else parts[0], parts[-1]

    problems = get_all_problems()

    if name in problems:
        return problems[name][0], problems[name][1], 'Solved' if problems[name][3] == 'Accepted' else 'Unsolved'

    if len(name) < 3 or name.isdigit() or ext in ignore_extensions:
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

    # Ignore files if they contain a substring that means they are unrelated to kattis.
    for part in ignore_file_parts:
        if part in name:
            return text, -1, 'Ignored'

    return name, -1, 'Unknown' if directory_name is not None else 'Ignored'
