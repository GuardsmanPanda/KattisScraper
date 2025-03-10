from functools import lru_cache
from bs4 import BeautifulSoup
from datetime import date
import configparser
import requests
import sqlite3
import util
import os

mark_accepted_if_partial = ['mnist2class', 'mnist10class']


@lru_cache(maxsize=None)
def get_headers():
    headers = {
        "User-Agent": "GuardsmanPanda's Problem Scraper"
    }
    config = configparser.ConfigParser()
    config.read('.kattisrc')
    username, token = config.get('user', 'username'), config.get('user', 'token')
    resp = requests.post(config.get('kattis', 'loginurl'), headers=headers,
                         data={'token': token, 'user': username, 'script': 'true'})
    if resp.status_code != 200:
        print("Failed to login to kattis")
        exit(1)
    else:
        print("Successfully logged in to kattis")
    headers["cookie"] = resp.headers['set-cookie']
    headers["cookie"] = config.get('user', 'cookie')  # fix for CF block, remove when can.
    return headers


def get_url(url):
    retries = 5
    while retries >= 0:
        try:
            text = requests.get(url, headers=get_headers(), timeout=10).text
            return text
        except requests.exceptions.Timeout:
            print("Timeout for", url)
            retries -= 1
    raise Exception("Failed to get url")


def get_kattis_user_name():
    data = get_url("https://open.kattis.com/")
    soup = BeautifulSoup(data, 'html.parser')
    return soup.find('a', {'class': 'static_link'}).get('href')[7:]


def update_solution_cache():
    util.create_solution_cache()
    con = sqlite3.connect('problem_cache.db')
    cur = con.cursor()
    url, page = "https://open.kattis.com/problems?page=", 0
    while True:
        data = get_url(url + str(page))
        soup = BeautifulSoup(data, 'html.parser')
        try:
            table = soup.find_all('table', {'class': 'table2'})[1].find('tbody').find_all('tr')
        except (AttributeError, IndexError):
            print("No more pages to scrape")
            break
        print("Scraping page {}".format(page))
        found = 0
        for row in table:
            cols = row.find_all('td')
            problem_id = cols[0].find('a').get('href')[10:]
            name = cols[0].find('a').text
            solution_status = cols[1].find('div').text
            if solution_status == 'Partial' and problem_id in mark_accepted_if_partial:
                solution_status = 'Accepted'
            shortest_solution_length = cols[3].text
            acc = cols[5].text
            diff_text = cols[7].find('span').text
            if diff_text == '?':
                continue
            difficulty_low = float(diff_text) if '-' not in diff_text else float(diff_text.split(' - ')[0])
            difficulty_high = float(diff_text) if '-' not in diff_text else float(diff_text.split(' - ')[1])
            cur.execute("""
                INSERT INTO problem_cache (
                    id, name, shortest_solution_length, difficulty_low, difficulty_high, solution_status, acc, last_seen_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_DATE)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    shortest_solution_length = excluded.shortest_solution_length,
                    difficulty_low = excluded.difficulty_low,
                    difficulty_high = excluded.difficulty_high,
                    solution_status = excluded.solution_status,
                    acc = excluded.acc,
                    acc_delta = excluded.acc - acc + acc_delta,
                    last_seen_at = excluded.last_seen_at
            """, (problem_id, name, shortest_solution_length, difficulty_low, difficulty_high, solution_status, acc, date.today()))
            found += 1
        page += 1
        if found == 0:
            break
    con.commit()
    con.close()


def update_problem_created_at():
    con = sqlite3.connect('problem_cache.db')
    for problem in util.execute_query("SELECT id FROM problem_cache WHERE created_at IS NULL"):
        print("Updating created_at for problem {}".format(problem[0]))
        data = get_url(f"https://open.kattis.com/problems/{problem[0]}/statistics/")
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
        con.cursor().execute("""
            UPDATE problem_cache
            SET created_at = ?
            WHERE id = ?
        """, (first_solution, problem[0]))
        con.commit()
    con.close()


def update_problem_length():
    con = sqlite3.connect('problem_cache.db')
    for problem in util.execute_query("SELECT id FROM problem_cache WHERE description_length IS NULL"):
        print("Updating description_length for problem {}".format(problem[0]))
        data = get_url(f"https://open.kattis.com/problems/{problem[0]}/")
        soup = BeautifulSoup(data, 'html.parser')
        if soup.find('div', {'class': 'problembody'}) is None:
            print("*** Problem {} has no description ***".format(problem[0]))
            continue
        description = soup.find('div', {'class': 'problembody'}).text
        contest = None
        for a_data in soup.find('div', {'class': 'metadata-license-card'}).find_all('a'):
            if '/problem-sources/' in a_data.get('href'):
                contest = a_data.text
                break
        print(problem, contest)
        con.cursor().execute("""
            UPDATE problem_cache
            SET description_length = ?, from_contest = ?
            WHERE id = ?
        """, (len(description), contest, problem[0]))
        con.commit()
    con.close()


def update_problem_solved_at():
    con = sqlite3.connect('problem_cache.db')
    user_name = get_kattis_user_name()
    for problem in util.execute_query(
            "SELECT id FROM problem_cache WHERE solved_at IS NULL AND solution_status = 'Accepted'"):
        print("Updating solved_at for problem {}".format(problem[0]))
        data = get_url(f"https://open.kattis.com/users/{user_name}?problem={problem[0]}&status=AC&tab=submissions")
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('table', {'id': 'submissions'})
        if table is None:
            continue
        first_solution = '2030-01-01'
        for xx in table.find('tbody').find_all('tr'):
            tds = xx.find_all('td')
            if len(tds) == 2:
                continue
            if 'Accepted' in tds[4].find('div').text:
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
    for problem in util.execute_query("SELECT id FROM problem_cache WHERE solution_status = 'Accepted'"):
        data = get_url(f"https://open.kattis.com/users/{user_name}/submissions/{problem[0]}")
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


def download_specific_solution(solution_id, downloaded_solutions):
    # skip already downloaded solutions
    if solution_id in downloaded_solutions:
        print("Skipping already downloaded solution {}".format(solution_id))
        return
    data = get_url(f"https://open.kattis.com/submissions/{solution_id}")
    soup = BeautifulSoup(data, 'html.parser')
    file_name = soup.find('h3').text
    code = get_url(f"https://open.kattis.com/submissions/{solution_id}/source/{file_name}")
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
