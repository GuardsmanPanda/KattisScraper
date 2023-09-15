#! ./venv/bin/python3

from tabulate import tabulate
import unix_only
import requests
import os

repo_ignore = {
    '0xecho/KattisSubmissionsDownloader',
    'isaaclo97/programacion-competitiva',
    'MilladMuhammadi/Competitive-Programming',
    'cebrusfs/kattis-examples',
    'CatEars/Companion',
    'HowardChengUleth/RMRC2015-public',
    'INDAPlus20/kevinwe-task-18',
    'wgranados/utscode',
    'Zantier/vikattis',
    'dulapahv/ProblemSet',
    'TUHHStartupEngineers-Classroom/ss23-bdsb-PriyankaKattishetti',
    'jaARke/LeetCode',
    'Rikveet/Programing_Problems_Manager',
    'MrStarman18/CompetitionProgramming',
    'kattisA/kattisa.github.io',
    'ishandutta2007/chatgpt-competitive-programming-extension',
    'jmerle/competitive-companion',
    'NoelEmaas/kattest',
    'Matistjati/kattis-ceoi2022',
    'GuardsmanPanda/KattisScraper',
    'Infus3d/CP-solutions',  # too cluttered
    'singmyr/kattis.com',
}

unix_text = "".join(open('unix_only.py', 'r').readlines())


def include_repo(repo):
    if repo in repo_ignore or repo in unix_text:
        return False
    return True


def main():
    repos = []
    seen = set()
    for i in range(1, 6):
        resp = requests.get(f"https://api.github.com/search/repositories?q=kattis&page={i}&per_page=100&sort=updated")
        if 'items' not in resp.json():
            print(resp.json())
            continue
        for x in resp.json()['items']:
            if x['full_name'] in seen:
                continue
            seen.add(x['full_name'])
            if include_repo(x['full_name']) and x['size'] > 0:
                repos.append((x['full_name'], x['size']))

    repos = sorted(repos, key=lambda k: k[1])
    print(tabulate(repos, headers=["Repo Name", "Size"], tablefmt='outline'))

    if not os.path.exists('test-repos'):
        os.mkdir('test-repos')

    rows = []
    for rr in repos:
        repo = unix_only.Repo(rr[0], path='test-repos')
        unix_only.create_and_sync_repo(repo)
        unix_only.find_unsolved_problems(repo)
        if repo.unsolved > 0 or repo.solved > 10 or repo.unknown > 100:
            rows.append((f"https://github.com/{repo.name}", repo.solved, round(repo.points_acquired), repo.unsolved, round(repo.points_missing), repo.last_commit, repo.unknown))
    unix_only.print_most_solved_problems()
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print(tabulate(sorted(rows, key=lambda r: r[3]), headers=["Repository Name", "Solved", "Points", "Unsolved", "Points", "Last Commit", "Unknown"], tablefmt='outline'))


if __name__ == '__main__':
    main()
