from functools import lru_cache
import sqlite3
import os


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


def check_problem(text: str, is_file=False):
    all_problems = get_all_problems()
    if text in all_problems:
        return text, all_problems[text][1], 'Solved' if all_problems[text][3] == 'Accepted' else 'Unsolved'
    return text, -1, 'Unknown'
