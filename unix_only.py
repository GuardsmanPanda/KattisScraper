from datetime import datetime
from zoneinfo import ZoneInfo
from tabulate import tabulate
import kattis_sync
import subprocess
import util
import sys
import os


class Repo:
    def __init__(self, name, branch="master", prefix=None):
        self.name = name
        self.branch = branch
        self.path = "repos/" + name
        self.solutions = self.path + "/" + (prefix if prefix else "")
        self.solved = 0
        self.unsolved = 0
        self.points_missing = 0.0
        self.unknown = []
        self.last_commit = None


# https://github.com/truongcongthanh2000/TrainACM-ICPC-OLP
repo_list = [
    Repo("aheschl1/Kattis-Solutions", branch='main'),
    Repo("bradendubois/competitive-programming"),
    Repo("ChrisVilches/Algorithms", prefix="kattis"),
    Repo("cs-un/Kattis"),
    Repo("dakoval/Kattis-Solutions"),
    Repo("donaldong/kattis", prefix="solutions"),
    Repo("DongjiY/Kattis"),
    Repo("ecly/kattis"),
    Repo("HermonMulat/Kattis"),
    Repo("iamvickynguyen/Kattis-Solutions"),
    Repo("JonSteinn/Kattis-Solutions"),
    Repo("kantuni/Kattis"),
    Repo("KentGrigo/Kattis", branch='main'),
    Repo("matthewReff/Kattis-Problems"),
    Repo("meysamaghighi/Kattis"),
    Repo("minidomo/Kattis"),
    Repo("mpfeifer1/Kattis"),
    Repo("PedroContipelli/Kattis"),
    Repo("RJTomk/Kattis"),
    Repo("robertusbagaskara/kattis-solutions"),
    Repo("RussellDash332/kattis", branch='main'),
    Repo("shakeelsamsu/kattis", branch='main'),
    Repo("Wabri/SomeKattisProblem"),
    Repo("xCiaraG/Kattis"),
    Repo("BrandonTang89/Competitive_Programming_4_Solutions", branch='main'),
]


def create_and_sync_repos():
    print("--------------------- Cloning & Syncing Git Repos ------------------------")
    if not os.path.exists('repos'):
        os.mkdir('repos')
    for rep in repo_list:
        if not os.path.exists(rep.path):
            res = subprocess.run(['git', 'clone', f"git@github.com:{rep.name}.git", rep.path], capture_output=True)
            if res.returncode != 0:
                print("Error cloning " + rep.name)
                print(res.stderr)
            else:
                print("Successfully cloned " + rep.name)
        else:
            res = subprocess.Popen(['git', 'pull'], cwd=rep.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            res.wait()
            if res.returncode == 0:
                lines = res.stdout.readlines()
                if len(lines) > 1:
                    print("Updated " + rep.name)
                    for line in lines:
                        print('  ', line.decode('utf-8').strip('\n'))
            else:
                print("ERROR UPDATING: " + rep.name)
                print(res.returncode)
                print(res.stderr.readlines())

        res = subprocess.Popen(['git', '--no-pager', 'log', '-1', '--format="%ai"'],cwd=rep.path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time = res.stdout.readlines()[0].decode('utf-8').strip('\n')
        rep.last_commit = datetime.strptime(time, '"%Y-%m-%d %H:%M:%S %z"').astimezone(ZoneInfo('localtime'))


def find_unsolved_problems():
    all_problems = util.get_all_problems()
    for repo in repo_list:
        unsolved = []
        seen = set()
        for x in os.walk(repo.solutions):
            waste, github_user, repo_name, *rest = x[0].split("/")
            directory_name = rest[-1].lower()
            if directory_name in all_problems:
                if directory_name in seen:
                    continue
                seen.add(directory_name)
                problem = all_problems[directory_name]
                if problem[3] == "Accepted":
                    repo.solved += 1
                else:
                    repo.points_missing += problem[1]
                    unsolved.append([directory_name, problem[1], f"https://github.com/{github_user}/{repo_name}/tree/{repo.branch}/{'/'.join(rest)}"])
                    repo.unsolved += 1
            for file in x[2]:
                parts = file.lower().split(".")
                if len(parts) != 2 or parts[1] in ('md', 'out', 'in', 'txt', 'json', 'ans') or len(parts[0]) < 2 or parts[0].startswith('template'):
                    continue

                if parts[0].startswith('kattis_'):
                    parts[0] = parts[0][7:]
                parts[0] = parts[0].replace('_', '')
                if parts[0] in seen:
                    continue
                seen.add(parts[0])

                if parts[0] in all_problems:
                    problem = all_problems[parts[0]]
                    if problem[3] == "Accepted":
                        repo.solved += 1
                    else:
                        repo.points_missing += problem[1]
                        unsolved.append([parts[0], problem[1], f"https://github.com/{github_user}/{repo_name}/blob/{repo.branch}{('/' + '/'.join(rest)) if rest[0] != '' else ''}/{file}"])
                        repo.unsolved += 1
                else:
                    if 'vjudge' not in parts[0] and '-' not in parts[0] and rest[-1] != 'hooks':
                        repo.unknown.append((parts[0], file, rest[-1]))
        if len(unsolved) > 0:
            print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
            print("🔱 Unsolved Problems In " + repo.name)
            print(tabulate(sorted(unsolved), headers=["Problem ID", "Points", "Link"], tablefmt='outline', floatfmt='0.1f'))


def print_repo_stats():
    find_unsolved_problems()
    rows = []
    for repo in sorted(repo_list, key=lambda x: x.last_commit):
        rows.append((repo.name, repo.solved, repo.unsolved, round(repo.points_missing), repo.last_commit))
        if len(repo.unknown) > 0:
            print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
            print('', repo.name)
            print("  Unknown: " + str(repo.unknown))
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print(tabulate(rows, headers=["Repository Name", "Solved", "Unsolved", "Points", "Last Commit"], tablefmt='outline'))


def main():
    args = sys.argv[1:]
    if '--scrape' in args:
        kattis_sync.update_solution_cache()
        # kattis_sync.update_problem_created_at()
        kattis_sync.update_problem_length()
        kattis_sync.update_problem_solved_at()
    create_and_sync_repos()
    print_repo_stats()


if __name__ == '__main__':
    main()
