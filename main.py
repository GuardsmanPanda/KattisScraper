from bs4 import BeautifulSoup
import kattis_sync
import requests
import sqlite3
import util


def compare_to_github_repo(url):
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    problem_ids = []
    for table in soup.find_all('table'):
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            problem_id = None
            for td in row.find_all('td'):
                if td.find('a') is not None and 'https://open.kattis.com/problems/' in td.find('a').attrs['href']:
                    problem_id = td.find('a').attrs['href'][33:]
                    break
            if problem_id is not None:
                problem_ids.append(problem_id)
    print_repo_diff(url, problem_ids)


def compare_to_github_folder(url):
    data = requests.get(url.replace('tree', 'tree-commit-info'), headers={'Accept': 'application/json'}).json()
    problem_ids = []
    for key in data:
        key = key.split('.')[0]
        problem_ids.append(key)
    print_repo_diff(url, problem_ids)


def print_repo_diff(url, problem_ids):
    unsolved = util.get_all_unsolved()
    missing_problems = []
    for problem in problem_ids:
        if problem in unsolved:
            missing_problems.append(unsolved[problem])
    if len(missing_problems) == 0:
        return
    print("*************************************")
    print("Solution status for", url)
    print(round(sum(x[1] for x in missing_problems)), "points missing")
    for x in missing_problems:
        print(x)
    print("*************************************")


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
    # create_and_sync_repos()
    kattis_sync.update_solution_cache()
    # kattis_sync.update_problem_created_at()
    kattis_sync.update_problem_length()
    kattis_sync.update_problem_solved_at()
    # kattis_sync.download_latest_solutions()
    compare_to_github_repo("https://github.com/robertusbagaskara/kattis-solutions")
    compare_to_github_repo("https://github.com/JonSteinn/Kattis-Solutions")
    compare_to_github_repo("https://github.com/matthewReff/Kattis-Problems")
    compare_to_github_repo("https://github.com/RJTomk/Kattis")
    compare_to_github_repo("https://github.com/Wabri/SomeKattisProblem")
    compare_to_github_repo("https://github.com/donaldong/kattis")
    compare_to_github_repo("https://github.com/RussellDash332/kattis")
    compare_to_github_folder('https://github.com/bradendubois/competitive-programming/tree/master/kattis')
    compare_to_github_folder('https://github.com/ecly/kattis/tree/master')
    compare_to_github_folder('https://github.com/PedroContipelli/Kattis/tree/master')
    compare_to_github_folder('https://github.com/iamvickynguyen/Kattis-Solutions/tree/master')
    compare_to_github_folder('https://github.com/DongjiY/Kattis/tree/master/src')
    compare_to_github_folder('https://github.com/HermonMulat/Kattis/tree/master/src')
    compare_to_github_folder('https://github.com/mpfeifer1/Kattis/tree/master')
    compare_to_github_folder('https://github.com/kantuni/Kattis/tree/master')
    compare_to_github_folder('https://github.com/ChrisVilches/Algorithms/tree/master/kattis')
    compare_to_github_folder('https://github.com/aheschl1/Kattis-Solutions/tree/master')
    compare_to_github_repo("https://github.com/BrandonTang89/Competitive_Programming_4_Solutions")
    print_simple_stats()


if __name__ == '__main__':
    main()
