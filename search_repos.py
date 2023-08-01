from tabulate import tabulate
import requests

repo_ignore = {
    '0xecho/KattisSubmissionsDownloader',
    'isaaclo97/programacion-competitiva',
    'MilladMuhammadi/Competitive-Programming',
    'cebrusfs/kattis-examples',
    'AgentEnder/OpenKattis',
    'CatEars/Companion',
    'HowardChengUleth/RMRC2015-public',
    'ollebaack/Kattis',
    'INDAPlus20/kevinwe-task-18',
    'wgranados/utscode',
    'Zantier/vikattis',
    'dulapahv/ProblemSet',
    'bibookss/cp-book-kattis-problems',
    'TUHHStartupEngineers-Classroom/ss23-bdsb-PriyankaKattishetti',
    'jaARke/LeetCode',
    'Rikveet/Programing_Problems_Manager',
    'MrStarman18/CompetitionProgramming',
    'vader-coder/Kattis',
    'kattisA/kattisa.github.io',
    'ishandutta2007/chatgpt-competitive-programming-extension',
    'jmerle/competitive-companion',
    'NoelEmaas/kattest',


    # Too few solutions
    'Darksonn/kattis',
    'AlexanderGracetantiono/Kattis',
}

unix_text = "".join(open('unix_only.py', 'r').readlines())


def include_repo(repo):
    if repo in repo_ignore or repo in unix_text:
        return False
    return True


def main():
    repos = []
    for i in range(1, 4):
        resp = requests.get(f"https://api.github.com/search/repositories?q=kattis&page={i}&per_page=100&sort=updated")
        if 'items' not in resp.json():
            print(resp.json())
            continue
        for x in resp.json()['items']:
            if include_repo(x['full_name']) and x['size'] > 10:
                repos.append((x['full_name'], x['size']))

    repos = sorted(repos, key=lambda k: k[1])
    print(tabulate(repos, headers=["Repo Name", "Size"], tablefmt='outline'))


if __name__ == '__main__':
    main()
