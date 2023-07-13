from datetime import datetime
from zoneinfo import ZoneInfo
from tabulate import tabulate
import kattis_sync
import subprocess
import util
import sys
import os


class Repo:
    def __init__(self, name, branch="master", prefix=None, ignore_files=False):
        self.name = name
        self.branch = branch
        self.ignore_files = ignore_files
        self.path = "repos/" + name
        self.solutions = self.path + "/" + (prefix if prefix else "")
        self.solved = 0
        self.unsolved = 0
        self.points_acquired = 0.0
        self.points_missing = 0.0
        self.unknown = []
        self.last_commit = None


# https://github.com/truongcongthanh2000/TrainACM-ICPC-OLP
repo_list = [
    Repo("aheschl1/Kattis-Solutions", branch='main'),
    Repo("aiviaghost/Kattis_solutions"),
    Repo("BC46/kattis-solutions", branch='main'),
    Repo("bradendubois/competitive-programming"),
    Repo("chonkykai/General-Coding", branch='main', prefix='open_kattis'),
    Repo("ChrisVilches/Algorithms", prefix="kattis"),
    Repo("cs-un/Kattis"),
    Repo("dakoval/Kattis-Solutions"),
    Repo("donaldong/kattis", prefix="solutions"),
    Repo("DongjiY/Kattis"),
    Repo("ecly/kattis"),
    Repo("HermonMulat/Kattis"),
    Repo("iamvickynguyen/Kattis-Solutions"),
    Repo("jerryxu20/kattis", branch='main'),
    Repo("JonSteinn/Kattis-Solutions"),
    Repo("kantuni/Kattis"),
    Repo("KentGrigo/Kattis", branch='main'),
    Repo("leslieyip02/kattis"),
    Repo("matthewReff/Kattis-Problems"),
    Repo("Mdan12/Kattis-solutions", branch='main'),
    Repo("meysamaghighi/Kattis"),
    Repo("minidomo/Kattis"),
    Repo("mpfeifer1/Kattis"),
    Repo("PedroContipelli/Kattis"),
    Repo("RJTomk/Kattis", ignore_files=True),
    Repo("robertusbagaskara/kattis-solutions"),
    Repo("RussellDash332/kattis", branch='main'),
    Repo("shakeelsamsu/kattis"),
    Repo("versenyi98/kattis-solutions", branch='main', prefix='solutions'),
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

        res = subprocess.Popen(['git', '--no-pager', 'log', '-1', '--format="%ai"'], cwd=rep.path,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time = res.stdout.readlines()[0].decode('utf-8').strip('\n')
        rep.last_commit = datetime.strptime(time, '"%Y-%m-%d %H:%M:%S %z"').replace(tzinfo=None)


def handle_repo_solution(canonical, points, result, repo, path, seen, unsolved, file=None):
    if canonical in seen or result == 'Ignored':
        return
    seen.add(canonical)
    if result == 'Solved':
        repo.solved += 1
        repo.points_acquired += points
    elif result == 'Unsolved':
        repo.points_missing += points
        repo.unsolved += 1
        if file is None:
            unsolved.append([canonical, points, '', f"https://github.com/{repo.name}/tree/{repo.branch}/{'/'.join(path)}"])
        else:
            file_size = os.path.getsize(f"repos/{repo.name}{('/' + '/'.join(path)) if path[0] != '' else ''}/{file}")
            unsolved.append([canonical, points, file_size, f"https://github.com/{repo.name}/blob/{repo.branch}{('/' + '/'.join(path)) if path[0] != '' else ''}/{file}"])
    else:
        repo.unknown.append((canonical, file, path[-1]))


def find_unsolved_problems():
    for repo in repo_list:
        unsolved = []
        seen = set()
        for x in os.walk(repo.solutions):
            waste, github_user, repo_name, *rest = x[0].split("/")
            canonical, points, result = util.check_problem(rest[-1].lower())
            handle_repo_solution(canonical, points, result, repo, rest, seen, unsolved)
            if repo.ignore_files:
                continue
            for file in x[2]:
                canonical, points, result = util.check_problem(file.lower(), rest[-1])
                handle_repo_solution(canonical, points, result, repo, rest, seen, unsolved, file=file)
        if len(unsolved) > 0:
            print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
            print("🔱 Unsolved Problems In " + repo.name)
            print(tabulate(sorted(unsolved), headers=["Problem ID", "Points", "Size", "Link"], tablefmt='outline', floatfmt='0.1f'))


def print_repo_stats():
    find_unsolved_problems()
    rows = []
    for repo in sorted(repo_list, key=lambda x: x.last_commit if x.last_commit is not None else datetime.min):
        rows.append((repo.name, repo.solved, round(repo.points_acquired), repo.unsolved, round(repo.points_missing), repo.last_commit))
        if len(repo.unknown) > 0:
            print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
            print('', repo.name)
            print("  Unknown: ")
            for x in sorted(repo.unknown):
                print(x)
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print(
        tabulate(rows, headers=["Repository Name", "Solved", "Points", "Unsolved", "Points", "Last Commit"], tablefmt='outline'))


def main():
    args = sys.argv[1:]
    if '--skip' not in args:
        create_and_sync_repos()
    if '--scrape' in args:
        kattis_sync.update_solution_cache()
        # kattis_sync.update_problem_created_at()
        kattis_sync.update_problem_length()
        kattis_sync.update_problem_solved_at()
    print_repo_stats()


if __name__ == '__main__':
    main()
