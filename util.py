from functools import lru_cache
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
    return {x[0]: x for x in get_all_from_query(
        "SELECT id, difficulty_high, name FROM problem_cache WHERE solution_status != 'Accepted'")}


@lru_cache(maxsize=1000)
def get_all_problems() -> dict:
    return {x[0]: x for x in get_all_from_query("SELECT id, difficulty_high, name, solution_status FROM problem_cache")}


part_removals = ['kattis_', 'katttis_','-sm','-node', '_']
ignore_extensions = ['md', 'out', 'in', 'txt', 'jpg', 'json', 'ans', 'sh', 'mod', 'toml', 'nix', 'yml', 'ignore', 'ipynb']
ignore_directories = {
    'heads',
    'hooks',
    'info',
    'KattisRSSParser', 'KattisRSSNotifier',
    'logs',
    'origin',
    'pack',
    'repo-scripts',
    'scripts',
    'templates', 'template', 'test',
    'verbose',
}
ignore_files = {
    'authors',
    'build', 'buildwiki','breadthfirstsearch',
    'directoryreader','deque','djikstra',
    'error',
    'generatereadme',
    'kattio',
    'license',
    'main',
    'node',
    'output',
    'pair',
    'readmegenerator',
    'scrapper', 'sodasurpler',
    'testgen', 'test', 'template',
    'version',
    'wronganswer',
}
ignore_file_parts = [
    'noi2020', 'neo-',
    'scl2022', 'scl2021',
    'vjudge',
]

name_mapping = {
    'eightqueens': '8queens',
    'greetingcards': 'greetingcard',
    'zebraocelots': 'zebrasocelots'
}


def check_problem(text: str, directory_name=None) -> (str, float, str):
    if len(text) >= 38 or text.startswith('.') or (directory_name is not None and directory_name.startswith('.')):
        return text, -1, 'Ignored'

    if directory_name is not None and directory_name in ignore_directories:
        return text, -1, 'Ignored'

    parts = text
    for part in part_removals:
        parts = parts.replace(part, '')
    parts = parts.split('.')
    name, ext = parts[0], parts[-1]

    if len(name) < 3 or name.isdigit() or ext in ignore_extensions:
        return text, -1, 'Ignored'

    all_problems = get_all_problems()
    if name in all_problems:
        return name, all_problems[name][1], 'Solved' if all_problems[name][3] == 'Accepted' else 'Unsolved'

    m = re.match(r'(\d*\D+)\d*$', name)
    if m is not None:
        name = m.group(1)

    if name in all_problems:
        return name, all_problems[name][1], 'Solved' if all_problems[name][3] == 'Accepted' else 'Unsolved'

    if name in ignore_files:
        return text, -1, 'Ignored'

    if name in name_mapping:
        return name_mapping[name],  all_problems[name_mapping[name]][1], 'Solved' if all_problems[name_mapping[name]][3] == 'Accepted' else 'Unsolved'

    for part in ignore_file_parts:
        if part in name:
            return text, -1, 'Ignored'

    return name, -1, 'Unknown' if directory_name is not None else 'Ignored'
