from datetime import datetime
import requests
import util


def ensure_table_created():
    util.create_solution_cache()
    util.execute_query("""
        CREATE TABLE IF NOT EXISTS vjudge_solutions(
            problem_id TEXT NOT NULL,
            solution_id INTEGER NOT NULL,
            length INTEGER NOT NULL,
            language TEXT NOT NULL,
            runtime INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            solution_status TEXT NOT NULL,
            access_status INTEGER NOT NULL,
            submitted_at DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (problem_id, solution_id),
            FOREIGN KEY (problem_id) REFERENCES problem_cache(id)
        )
    """)


def fill_table():
    problems = util.execute_query(f"""
        SELECT id FROM problem_cache WHERE solution_status != 'Accepted'
        AND id NOT IN (SELECT problem_id FROM vjudge_solutions WHERE solution_status IN ('Accepted', 'Accepted (100)'))
    """)
    for problem in problems:
        print("Fetching", problem[0])
        data = requests.get(f"https://vjudge.net/status/data?start=0&length=20&OJId=Kattis&probNum={problem[0]}&res=1").json()
        for v in data['data']:
            if v['status'] not in ('Accepted', 'Accepted (100)'):
                continue
            print(v)
            unix_time = v['time']
            util.execute_query("""
                INSERT INTO vjudge_solutions(problem_id, solution_id, length, language, runtime, user_name, solution_status, access_status, submitted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, v['probNum'], v['runId'], v['sourceLength'], v['language'], v['runtime'], v['userName'], v['status'], v['access'], datetime.fromtimestamp(unix_time//1000).strftime('%Y-%m-%d %H:%M:%S'))


def main():
    ensure_table_created()
    fill_table()


if __name__ == '__main__':
    main()
