from datetime import datetime
from tabulate import tabulate
import kattis_sync
import subprocess
import util
import sys
import os


class Repo:
    def __init__(self, name, prefix=None, ignore_files=False, hosting='github'):
        self.name = name
        self.ignore_files = ignore_files
        self.hosting = hosting
        self.path = "repos/" + name
        self.solutions = self.path + "/" + (prefix if prefix else "")
        self.solved = 0
        self.unsolved = 0
        self.unknown = 0
        self.branch = 'main'
        self.points_acquired = 0.0
        self.points_missing = 0.0
        self.unknownFiles = []
        self.last_commit = None


# https://github.com/truongcongthanh2000/TrainACM-ICPC-OLP
repo_list = [
    # Repo("Syuq/Kattis", hosting='gitlab'), # clone of mpfeifer1/Kattis

    Repo("abeaumont/competitive-programming", prefix='kattis'),
    Repo("aheschl1/Kattis-Solutions"),
    Repo("aiviaghost/Kattis_solutions"),
    Repo("albe2669/kattis-solutions"),
    Repo("AliMuhammadAsad/Kattis-Solutions"),
    Repo("andreaskrath/Kattis"),
    Repo("arsdorintbp2003/KattisPractice"),
    Repo("Athaws/KattisSolutions"),
    Repo("AugustDanell/Kattis-Assignments"),
    Repo("BC46/kattis-solutions"),
    Repo("BooleanCube/cp", prefix='kattis'),
    # Repo("bradendubois/competitive-programming", prefix='kattis'),
    Repo("chiralcentre/Kattis"),
    Repo("chonkykai/General-Coding", prefix='open_kattis'),
    Repo("ChrisVilches/Algorithms", prefix="kattis"),
    # Repo("cs-un/Kattis"),
    # Repo("dakoval/Kattis-Solutions"),
    Repo("DaltonCole/ProgramingProblems", prefix='kattis'),
    Repo("DomBinks/kattis"),
    Repo("donaldong/kattis", prefix="solutions"),
    Repo("DongjiY/Kattis"),
    Repo("ecly/kattis"),
    Repo("EoinDavey/Competitive", prefix='Kattis'),
    Repo("FT-Labs/KattisProblems-Python"),
    Repo("HermonMulat/Kattis"),
    Repo("hliuliu/kattis_problems"),
    Repo("hoi-yin/Kattis-Java"),
    Repo("iamvickynguyen/Kattis-Solutions"),
    Repo("iandioch/solutions", prefix='kattis'),
    Repo("Ikerlb/kattis"),
    Repo("jakobkhansen/KattisSolutions"),
    Repo("Jasonzhou97/Kattis-Solutions"),
    Repo("jerryxu20/kattis"),
    Repo("JonSteinn/Kattis-Solutions"),
    Repo("JaydenPahukula/competitive-coding", prefix='Kattis'),
    Repo("JKeane4210/KattisProblems"),
    Repo("JordanHassy/Kattis"),
    Repo("kailashgautham/Kattis", prefix='completed'),
    # Repo("kantuni/Kattis"),
    # Repo("KentGrigo/Kattis"),
    Repo("KiranKaravaev/kattis"),
    Repo("kristiansordal/kattis"),
    Repo("kumarchak30/Kattis-solutions"),
    Repo("leslieyip02/kattis"),
    Repo("LoiNguyennn/CompetitiveProgramming4_Solutions", prefix="Kattis_OJ"),
    # Repo("lisansulistiani/Kattis"),
    Repo("luffingluffy/cp", prefix='kattis'),
    Repo("Mangern/kattis"),
    Repo("MarkusMathiasen/CP4_Kattis_Solutions"),
    Repo("MatthewFreestone/Kattis"),
    Repo("matthewReff/Kattis-Problems"),
    Repo("Mdan12/Kattis-solutions"),
    Repo("meysamaghighi/Kattis"),
    # Repo("minidomo/Kattis"),
    Repo("mpfeifer1/Kattis"),
    Repo("mwebber3/CodingChallengeSites", prefix='Kattis'),
    Repo("patrick-may/kattis"),
    Repo("olasundell/kattis", prefix='src/main'),
    Repo("PedroContipelli/Kattis"),
    Repo("prokarius/hello-world"),
    Repo("rishabhgoel0213/KattisSolutions"),
    Repo("RJTomk/Kattis", ignore_files=True),
    Repo("robertusbagaskara/kattis-solutions"),
    Repo("RussellDash332/kattis"),
    Repo("rvrheenen/OpenKattis"),
    Repo("shakeelsamsu/kattis"),
    Repo("Skantz/Puzzles", prefix='kattis'),
    Repo("ssmall90/Open-Kattis"),
    Repo("SurgicalSteel/Competitive-Programming", prefix='Kattis-Solutions'),
    Repo("Thomas-McKanna/Kattis"),
    Repo("versenyi98/kattis-solutions", prefix='solutions'),
    Repo("Wabri/SomeKattisProblem"),
    Repo("Zyzzava/kattis"),
    # Repo("xCiaraG/Kattis"),
    Repo("BrandonTang89/Competitive_Programming_4_Solutions"),
]


def create_and_sync_repos():
    print("--------------------- Cloning & Syncing Git Repos ------------------------")
    if not os.path.exists('repos'):
        os.mkdir('repos')
    for rep in repo_list:
        if not os.path.exists(rep.path):
            git_command = f"git@github.com:{rep.name}.git" if rep.hosting == 'github' else f"https://gitlab.com/{rep.name}.git"
            res = subprocess.run(['git', 'clone', git_command, rep.path], capture_output=True)
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
                print(res.stderr.readlines())

        res = subprocess.Popen(['git', '--no-pager', 'log', '-1', '--format="%ai"'], cwd=rep.path,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time = res.stdout.readlines()[0].decode('utf-8').strip('\n')
        rep.last_commit = datetime.strptime(time, '"%Y-%m-%d %H:%M:%S %z"').replace(tzinfo=None)

        res = subprocess.Popen(['git', 'branch', '--show-current'], cwd=rep.path,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rep.branch = res.stdout.readlines()[0].decode('utf-8').strip('\n')


def handle_repo_solution(canonical, points, result, repo, path, seen, unsolved, file=None, dir_result=None, full_path=None):
    if canonical in seen or result == 'Ignored':
        return
    seen.add(canonical)
    if result == 'Solved':
        repo.solved += 1
        repo.points_acquired += points
    elif result == 'Unsolved':
        repo.points_missing += points
        repo.unsolved += 1
        local_location = f"repos/{repo.name}{('/' + '/'.join(path)) if path[0] != '' else ''}/"
        if file is None:
            file_size = 0
            for ff in os.listdir(local_location):
                if os.path.isfile(local_location + ff):
                    file_size = max(file_size, os.path.getsize(local_location + ff))
            unsolved.append([canonical, points, f'-{file_size}', f"https://github.com/{repo.name}/tree/{repo.branch}/{'/'.join(path)}"])
        else:
            file_size = os.path.getsize(local_location + file)
            unsolved.append([canonical, points, file_size, f"https://github.com/{repo.name}/blob/{repo.branch}{('/' + '/'.join(path)) if path[0] != '' else ''}/{file}"])
    elif dir_result != 'Solved' and dir_result != 'Unsolved':
        repo.unknownFiles.append((canonical, file, full_path))
        repo.unknown += 1
    # else:
    #     print("ERROR: ",(canonical, file, path[-1]))


path_ignore =[
    '/.', '/_', '@todo', '/venv', '/Practice', '/debug',
    'codingame', 'hackerrank', 'vjudge', 'leetcode',
    'cmake-build-debug',
    'scl2022', 'noi_2020', 'scl2021',
]


def find_unsolved_problems():
    for repo in repo_list:
        unsolved = []
        seen = set()
        for x in os.walk(repo.solutions):
            if any(ignore in x[0] for ignore in path_ignore):
                continue
            waste, github_user, repo_name, *rest = x[0].split("/")
            dir_canonical, dir_points, dir_result = util.check_problem(rest[-1].lower())
            handle_repo_solution(dir_canonical, dir_points, dir_result, repo, rest, seen, unsolved, full_path=x[0])
            if repo.ignore_files:
                continue
            for file in x[2]:
                if any(ignore in file.lower() for ignore in path_ignore):
                    continue
                canonical, points, result = util.check_problem(file.lower(), rest[-1])
                handle_repo_solution(canonical, points, result, repo, rest, seen, unsolved, file=file, dir_result=dir_result, full_path=x[0])
        if len(unsolved) > 0:
            print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
            print("🔱 Unsolved Problems In " + repo.name)
            print(tabulate(sorted(unsolved), headers=["Problem ID", "Points", "Size", "Link"], tablefmt='outline', floatfmt='0.1f'))


def print_repo_stats():
    solved, unsolved, unknown = 0, 0, 0
    find_unsolved_problems()
    rows = []
    for repo in sorted(repo_list, key=lambda xx: xx.points_missing):
        solved += repo.solved
        unsolved += repo.unsolved
        unknown += repo.unknown
        rows.append((repo.name, repo.solved, round(repo.points_acquired), repo.unsolved, round(repo.points_missing), repo.last_commit, repo.unknown))
        if len(repo.unknownFiles) > 0:
            print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
            print('', repo.name)
            print("  Unknown: ")
            for x in sorted(repo.unknownFiles):
                print(x)
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print(
        tabulate(rows, headers=["Repository Name", "Solved", "Points", "Unsolved", "Points", "Last Commit", "Unknown"], tablefmt='outline'))
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print("Total Solved: ", solved, "Total Unsolved: ", unsolved, "Total Unknown: ", unknown)


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
