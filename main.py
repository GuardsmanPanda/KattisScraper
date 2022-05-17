from bs4 import BeautifulSoup
import requests
import sqlite3
import os


def get_kattis_user_name(headers):
    data = requests.get("https://open.kattis.com/", headers=headers).text
    soup = BeautifulSoup(data, 'html.parser')
    return soup.find('div', {'class': 'user-infobox-name'}).find('a').get('href')[7:]


def get_all_from_query(query: str):
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute(query)
    return cur.fetchall()


def create_solution_cache():
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS problem_cache (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            difficulty FLOAT,
            description_length INTEGER,
            is_solved INTEGER NOT NULL,
            solved_at TEXT,
            created_at TEXT,
            is_deleted INTEGER NOT NULL DEFAULT 0
        )
    """)
    con.commit()
    con.close()


def update_solution_cache(headers):
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    url, page = "https://open.kattis.com/problems?page=",  0
    cur.execute("UPDATE problem_cache SET is_deleted = 1")
    while True:
        print("Scraping page {}".format(page))
        data = requests.get(url+str(page), headers=headers).text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('table', {'class': 'problem_list'}).find('tbody').find_all('tr')
        found = 0
        for row in table:
            cols = row.find_all('td')
            problem_id = cols[0].find('a').get('href')[10:]
            name = cols[0].find('a').text
            difficulty = float(cols[8].text) if '-' not in cols[8].text else float(cols[8].text.split(' - ')[1])
            solved = 1 if 'solved' in row.get('class') else 0
            cur.execute("""
                INSERT INTO problem_cache (
                    id, name, difficulty, is_solved, is_deleted
                ) VALUES (?, ?, ?, ?, 0)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    difficulty = excluded.difficulty,
                    is_solved = excluded.is_solved,
                    is_deleted = 0
            """, (problem_id, name, difficulty, solved))
            found += 1
        page += 1
        if found == 0:
            break
    con.commit()
    con.close()


def update_problem_created_at(headers):
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute("SELECT id FROM problem_cache WHERE created_at IS NULL")
    for problem in cur.fetchall():
        print("Updating created_at for problem {}".format(problem[0]))
        data = requests.get(f"https://open.kattis.com/problems/{problem[0]}/statistics/", headers=headers).text
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


def update_problem_length(headers):
    con = sqlite3.connect('problem_cache.db')
    for problem in get_all_from_query("SELECT id FROM problem_cache WHERE description_length IS NULL"):
        print("Updating description_length for problem {}".format(problem[0]))
        data = requests.get(f"https://open.kattis.com/problems/{problem[0]}/", headers=headers).text
        soup = BeautifulSoup(data, 'html.parser')
        description = soup.find('div', {'class': 'problembody'}).text
        con.cursor().execute("""
            UPDATE problem_cache
            SET description_length = ?
            WHERE id = ?
        """, (len(description), problem[0]))
        con.commit()
    con.close()


def update_problem_solved_at(headers):
    con = sqlite3.connect('problem_cache.db')
    user_name = get_kattis_user_name(headers)
    for problem in get_all_from_query("SELECT id FROM problem_cache WHERE solved_at IS NULL AND is_solved = 1 AND is_deleted = 0"):
        print("Updating solved_at for problem {}".format(problem[0]))
        data = requests.get(f"https://open.kattis.com/users/{user_name}/submissions/{problem[0]}", headers=headers).text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('table', {'class': 'table-submissions'})
        if table is None:
            continue
        first_solution = '2030-01-01'
        for xx in table.find('tbody').find_all('tr'):
            tds = xx.find_all('td')
            if 'Accepted' in tds[-3].find('span').text:
                first_solution = min(tds[-5].text.strip(), first_solution)
        if len(first_solution) < 15:
            first_solution = None
        con.cursor().execute("""
            UPDATE problem_cache
            SET solved_at = ?
            WHERE id = ?
        """, (first_solution, problem[0]))
        con.commit()
    con.close()


def download_latest_solutions(headers):
    # make directory 'solutions' if not exists
    if not os.path.exists('solutions'):
        os.makedirs('solutions')
    downloaded_solutions = []
    # get all ids from already downloaded file
    if os.path.exists('already_downloaded.txt'):
        with open('already_downloaded.txt', 'r', encoding='utf-8') as f:
            downloaded_solutions = f.read().splitlines()
    user_name = get_kattis_user_name(headers)
    for problem in get_all_from_query("SELECT id FROM problem_cache WHERE is_solved = 1 AND is_deleted = 0"):
        data = requests.get(f"https://open.kattis.com/users/{user_name}/submissions/{problem[0]}", headers=headers).text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('table', {'class': 'table-submissions'})
        if table is None:
            continue
        for xx in table.find('tbody').find_all('tr'):
            tds = xx.find_all('td')
            if 'Accepted' in tds[-3].find('span').text:
                print("Downloading solution for problem {}".format(problem[0]))
                download_specific_solution(headers, tds[0].find('a').text, downloaded_solutions)
                break


def download_specific_solution(headers, solution_id, downloaded_solutions):
    # skip already downloaded solutions
    if solution_id in downloaded_solutions:
        print("Skipping already downloaded solution {}".format(solution_id))
        return
    data = requests.get(f"https://open.kattis.com/submissions/{solution_id}", headers=headers).text
    soup = BeautifulSoup(data, 'html.parser')
    file_name = soup.find('h3').text
    code = requests.get(f"https://open.kattis.com/submissions/{solution_id}/source/{file_name}", headers=headers).text
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


def print_simple_stats():
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    cur.execute("""
        SELECT 
            SUM(difficulty) FILTER(WHERE is_solved = 1) AS 'My Points',
            SUM(difficulty) AS 'Total Points',
            SUM(difficulty) FILTER(WHERE is_solved = 1)/SUM(difficulty)*100 AS percentage_points,
            COUNT(difficulty) FILTER(WHERE is_solved = 1) AS 'My Problems',
            COUNT(difficulty) AS 'Total Problems',
            COUNT(difficulty) FILTER(WHERE is_solved = 1)*100/COUNT(difficulty) AS percentage_problems
        FROM problem_cache
    """)
    res = cur.fetchone()
    print(f"My Points: {int(res[0])}, Total Points: {int(res[1])}, Percentage Points: {round(res[2], 1)}%")
    print(f"My Problems: {int(res[3])}, Total Problems: {int(res[4])}, Percentage Problems: {res[5]}%")
    con.close()


def main():
    headers = {
        "Cookie": "",
        "User-Agent": "Guardsmanpanda Problem Scraper"
    }
    #create_solution_cache()
    #update_solution_cache(headers)
    update_problem_created_at(headers)
    update_problem_length(headers)
    update_problem_solved_at(headers)
    download_latest_solutions(headers)
    print_simple_stats()


if __name__ == '__main__':
    main()
