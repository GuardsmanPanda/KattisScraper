from bs4 import BeautifulSoup
from datetime import date
import requests
import sqlite3
import os


def get_headers():
    headers = {
        "User-Agent": "Guardsmanpanda Problem Scraper"
    }
    with open('cookie.txt', 'r') as file:
        headers["cookie"] = file.readline()
    return headers


def get_kattis_user_name():
    data = requests.get("https://open.kattis.com/", headers=get_headers()).text
    soup = BeautifulSoup(data, 'html.parser')
    return soup.find('a', {'class': 'static_link'}).get('href')[7:]


def get_all_from_query(query: str):
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute(query)
    return cur.fetchall()


def create_solution_cache():
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
            average_solution_length INTEGER,
            solution_status TEXT,
            solved_at TEXT,
            created_at TEXT,
            last_seen_at TEXT
        )
    """)
    con.commit()
    con.close()


def update_solution_cache():
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    url, page = "https://open.kattis.com/problems?page=",  0
    while True:
        print("Scraping page {}".format(page))
        data = requests.get(url+str(page), headers=get_headers()).text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('table', {'class': 'table2'}).find('tbody').find_all('tr')
        found = 0
        for row in table:
            cols = row.find_all('td')
            problem_id = cols[0].find('a').get('href')[10:]
            name = cols[0].find('a').text
            solution_status = cols[1].find('div').text
            shortest_solution_length = cols[3].text
            diff_text = cols[7].find('span').text
            difficulty_low = float(diff_text) if '-' not in diff_text else float(diff_text.split(' - ')[0])
            difficulty_high = float(diff_text) if '-' not in diff_text else float(diff_text.split(' - ')[1])
            cur.execute("""
                INSERT INTO problem_cache (
                    id, name, shortest_solution_length, difficulty_low, difficulty_high, solution_status, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    shortest_solution_length = excluded.shortest_solution_length,
                    difficulty_low = excluded.difficulty_low,
                    difficulty_high = excluded.difficulty_high,
                    solution_status = excluded.solution_status,
                    last_seen_at = excluded.last_seen_at
            """, (problem_id, name, shortest_solution_length, difficulty_low, difficulty_high, solution_status, date.today()))
            found += 1
        page += 1
        if found == 0:
            break
    con.commit()
    con.close()


def update_problem_created_at():
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute("SELECT id FROM problem_cache WHERE created_at IS NULL")
    for problem in cur.fetchall():
        print("Updating created_at for problem {}".format(problem[0]))
        data = requests.get(f"https://open.kattis.com/problems/{problem[0]}/statistics/", headers=get_headers()).text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('section', {'id': 'toplist0'})
        if table is None:
            continue
        solutions = table.find('table').find('tbody').find_all('tr')
        first_solution = '2030-01-01'
        for xx in solutions:
            first_solution = min(xx.find_all('td')[-2].text.strip(), first_solution)
        if len(first_solution) < 15:
            first_solution = None
        cur.execute("""
            UPDATE problem_cache
            SET created_at = ?
            WHERE id = ?
        """, (first_solution, problem[0]))
        con.commit()
    con.close()


def update_problem_length():
    con = sqlite3.connect('problem_cache.db')
    for problem in get_all_from_query("SELECT id FROM problem_cache WHERE description_length IS NULL"):
        print("Updating description_length for problem {}".format(problem[0]))
        data = requests.get(f"https://open.kattis.com/problems/{problem[0]}/", headers=get_headers()).text
        soup = BeautifulSoup(data, 'html.parser')
        description = soup.find('div', {'class': 'problembody'}).text
        con.cursor().execute("""
            UPDATE problem_cache
            SET description_length = ?
            WHERE id = ?
        """, (len(description), problem[0]))
        con.commit()
    con.close()


def update_problem_solved_at():
    con = sqlite3.connect('problem_cache.db')
    user_name = get_kattis_user_name()
    for problem in get_all_from_query("SELECT id FROM problem_cache WHERE solved_at IS NULL AND solution_status = 'Accepted'"):
        print("Updating solved_at for problem {}".format(problem[0]))
        data = requests.get(f"https://open.kattis.com/users/{user_name}/submissions/{problem[0]}", headers=get_headers()).text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('table', {'class': 'table2'})
        if table is None:
            continue
        first_solution = '2030-01-01'
        for xx in table.find('tbody').find_all('tr'):
            tds = xx.find_all('td')
            if len(tds) == 2:
                continue
            print(tds)
            if 'Accepted' in tds[3].find('div').text:
                first_solution = min(tds[1].text.strip(), first_solution)
        if len(first_solution) < 15:
            first_solution = None

        con.cursor().execute("""
            UPDATE problem_cache
            SET solved_at = ?
            WHERE id = ?
        """, (first_solution, problem[0]))
        con.commit()
    con.close()


def download_latest_solutions():
    # make directory 'solutions' if not exists
    if not os.path.exists('solutions'):
        os.makedirs('solutions')
    downloaded_solutions = []
    # get all ids from already downloaded file
    if os.path.exists('already_downloaded.txt'):
        with open('already_downloaded.txt', 'r', encoding='utf-8') as f:
            downloaded_solutions = f.read().splitlines()
    user_name = get_kattis_user_name()
    for problem in get_all_from_query("SELECT id FROM problem_cache WHERE is_solved = 1 AND is_deleted = 0"):
        data = requests.get(f"https://open.kattis.com/users/{user_name}/submissions/{problem[0]}", headers=get_headers()).text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('table', {'class': 'table-submissions'})
        if table is None:
            continue
        for xx in table.find('tbody').find_all('tr'):
            tds = xx.find_all('td')
            if 'Accepted' in tds[-3].find('span').text:
                print("Downloading solution for problem {}".format(problem[0]))
                download_specific_solution(tds[0].find('a').text, downloaded_solutions)
                break


def download_specific_solution( solution_id, downloaded_solutions):
    # skip already downloaded solutions
    if solution_id in downloaded_solutions:
        print("Skipping already downloaded solution {}".format(solution_id))
        return
    data = requests.get(f"https://open.kattis.com/submissions/{solution_id}", headers=get_headers()).text
    soup = BeautifulSoup(data, 'html.parser')
    file_name = soup.find('h3').text
    code = requests.get(f"https://open.kattis.com/submissions/{solution_id}/source/{file_name}", headers=get_headers()).text
    first_char = file_name[0]
    if not first_char.isalpha():
        first_char = '#'
    # create first char folder if not exists
    if not os.path.exists(f'solutions/{first_char}'):
        os.makedirs(f'solutions/{first_char}')
    with open(f'solutions/{first_char}/{file_name}', 'w', encoding='utf-8') as f:
        # write code to file but fix line endings between linux and windows
        f.write(code.replace('\r\n', '\n'))
    # append the problem_id to a file 'already downloaded'
    with open('already_downloaded.txt', 'a', encoding='utf-8') as f:
        f.write(f'{solution_id}\n')
    return


def compare_to_github_repo(url):
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    table = soup.find('table')
    rows = table.find('tbody').find_all('tr')
    missing_problems = []
    for row in rows:
        problem_id = None
        for td in row.find_all('td'):
            if td.find('a') is not None and 'https://open.kattis.com/problems/' in td.find('a').attrs['href']:
                problem_id = td.find('a').attrs['href'][33:]
                break
        if problem_id is not None:
            cur.execute("SELECT * FROM problem_cache WHERE id = ?", (problem_id,))
            res = cur.fetchone()
            if res is None:
                print("Missing problem {}".format(problem_id))


def print_simple_stats():
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute("""
        SELECT 
            SUM(difficulty_high) FILTER(WHERE solution_status = 'Accepted') AS 'My Points',
            SUM(difficulty_high) AS 'Total Points',
            SUM(difficulty_high) FILTER(WHERE solution_status = 'Accepted')/SUM(difficulty_high)*100 AS percentage_points,
            COUNT(difficulty_high) FILTER(WHERE solution_status = 'Accepted') AS 'My Problems',
            COUNT(difficulty_high) AS 'Total Problems',
            COUNT(difficulty_high) FILTER(WHERE solution_status = 'Accepted')*100.0/COUNT(difficulty_high) AS percentage_problems
        FROM problem_cache
    """)
    res = cur.fetchone()
    print(f"My Points: {int(res[0])}, Total Points: {int(res[1])}, Percentage Points: {round(res[2], 1)}%")
    print(f"My Problems: {int(res[3])}, Total Problems: {int(res[4])}, Percentage Problems: {round(res[5], 1)}%")
    con.close()


def main():
    # create_solution_cache()
    # update_solution_cache()
    # update_problem_created_at()
    # update_problem_length()
    update_problem_solved_at()
    # download_latest_solutions()
    compare_to_github_repo("https://github.com/JonSteinn/Kattis-Solutions")
    print_simple_stats()


if __name__ == '__main__':
    main()
