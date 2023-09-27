#! ./venv/bin/python3

from collections import defaultdict
from datetime import datetime
from tabulate import tabulate
import kattis_sync
import subprocess
import util
import sys
import os


class Repo:
    def __init__(self, name, prefix=None, path='repos', ignore_unknown=False):
        self.name = name
        self.ignore_unknown = ignore_unknown
        self.path = path + "/" + name
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
    Repo("abeaumont/competitive-programming", prefix='kattis'),
    Repo("aheschl1/Kattis-Solutions"),
    Repo("aiviaghost/Kattis_solutions"),
    Repo("albe2669/kattis-solutions"),
    Repo("AliMuhammadAsad/Kattis-Solutions"),
    Repo("andreaskrath/Kattis"),
    Repo("arsdorintbp2003/KattisPractice"),
    Repo("Athaws/KattisSolutions"),
    Repo("AugustDanell/Kattis-Assignments"),
    Repo("ayoubc/competitive-programming", prefix='online_judges/kattis'),
    Repo("BC46/kattis-solutions"),
    Repo("BooleanCube/cp", prefix='kattis'),
    # Repo("bradendubois/competitive-programming", prefix='kattis'),
    Repo("chiralcentre/Kattis"),
    Repo("ChrisVilches/Algorithms", prefix="kattis"),
    Repo("coding-armadillo/kattis"),
    Repo("Cryst67/KattisSolutions"),
    # Repo("cs-un/Kattis"),
    # Repo("dakoval/Kattis-Solutions"),
    Repo("DangerousCactus/Kattis"),
    Repo("DaltonCole/ProgramingProblems", prefix='kattis'),
    Repo("darrinmwiley/Kattis-Solutions"),
    Repo("DedsecKnight/kattis-competitive-programming"),
    Repo("DomBinks/kattis"),
    Repo("donaldong/kattis", prefix="solutions"),
    Repo("DongjiY/Kattis"),
    Repo("ecly/kattis"),
    Repo("EoinDavey/Competitive", prefix='Kattis'),
    Repo("FT-Labs/KattisProblems-Python"),
    Repo("gladwinyjh/Kattis"),
    Repo("HermonMulat/Kattis"),
    Repo("Hjaltesorgenfrei/kattisexercises"),
    Repo("hliuliu/kattis_problems"),
    Repo("hvrlxy/KATTIS", ignore_unknown=True),
    Repo("iamvickynguyen/Kattis-Solutions"),
    Repo("iandioch/solutions", prefix='kattis'),
    Repo("Ikerlb/kattis"),
    Repo("jakobkhansen/KattisSolutions"),
    Repo("jasonincanada/kattis"),
    Repo("Jasonzhou97/Kattis-Solutions"),
    Repo("JaydenPahukula/competitive-coding", prefix='Kattis'),
    Repo("jerryxu20/kattis"),
    Repo("JKeane4210/KattisProblems"),
    Repo("JonSteinn/Kattis-Solutions"),
    Repo("kailashgautham/Kattis", prefix='completed'),
    # Repo("kantuni/Kattis"),
    # Repo("KentGrigo/Kattis"),
    # Repo("KiranKaravaev/kattis"),
    Repo("kristiansordal/kattis"),
    Repo("kscharlund/kattis"),
    Repo("kumarchak30/Kattis-solutions"),
    Repo("leslieyip02/kattis"),
    Repo("LoiNguyennn/CompetitiveProgramming4_Solutions", prefix="Kattis_OJ"),
    # Repo("lisansulistiani/Kattis"),
    Repo("lucasscharenbroch/kattis-solutions"),
    Repo("luffingluffy/cp", prefix='kattis'),
    Repo("Mangern/kattis"),
    Repo("MarkusMathiasen/CP4_Kattis_Solutions"),
    Repo("MatthewFreestone/Kattis"),
    Repo("matthewReff/Kattis-Problems"),
    Repo("Mdan12/Kattis-solutions"),
    Repo("meysamaghighi/Kattis"),
    # Repo("minidomo/Kattis"),
    Repo("mpfeifer1/Kattis"),
    Repo("mukerem/competitive-programming", prefix="kattis"),
    Repo("muffin02/Kattis"),
    Repo("mwebber3/CodingChallengeSites", prefix='Kattis'),
    Repo("NikitaSandstrom/Kattis-Solutions"),
    Repo("norlen/kattis"),
    Repo("patrick-may/kattis"),
    Repo("olasundell/kattis", prefix='src/main'),
    # Repo("PedroContipelli/Kattis"),
    Repo("prokarius/hello-world"),
    Repo("ricardo0129/KattisSolutions"),
    Repo("rishabhgoel0213/KattisSolutions"),
    Repo("RJTomk/Kattis", ignore_unknown=True),
    Repo("robertusbagaskara/kattis-solutions"),
    Repo("RussellDash332/kattis"),
    Repo("rvrheenen/OpenKattis"),
    Repo("samjwu/OpenKattis"),
    Repo("shakeelsamsu/kattis"),
    Repo("Skantz/Puzzles", prefix='kattis'),
    Repo("ssmall90/Open-Kattis"),
    Repo("SurgicalSteel/Competitive-Programming", prefix='Kattis-Solutions'),
    Repo("Thomas-McKanna/Kattis"),
    Repo("traffaillac/traf-kattis"),
    Repo("versenyi98/kattis-solutions", prefix='solutions'),
    Repo("zhuodannychen/Competitive-Programming", prefix='Kattis'),
    Repo("Zyzzava/kattis"),
    # Repo("xCiaraG/Kattis"),
    Repo("BrandonTang89/Competitive_Programming_4_Solutions"),
]

solution_count = defaultdict(int)


def create_and_sync_repo(rep: Repo):
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
            print(res.stderr.readlines())

    res = subprocess.Popen(['git', '--no-pager', 'log', '-1', '--format="%ai"'], cwd=rep.path,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = res.stdout.readlines()
    if len(output) == 0:
        rep.last_commit = '-'
    else:
        time = output[0].decode('utf-8').strip('\n')
        rep.last_commit = datetime.strptime(time, '"%Y-%m-%d %H:%M:%S %z"').replace(tzinfo=None)

    res = subprocess.Popen(['git', 'branch', '--show-current'], cwd=rep.path, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    rep.branch = res.stdout.readlines()[0].decode('utf-8').strip('\n')


def handle_repo_solution(canonical, points, result, repo, path, seen, unsolved, file=None, dir_result=None, full_path=None):
    if canonical in seen or result == 'Ignored':
        return

    local_location, file_size = f"{repo.path}{('/' + '/'.join(path)) if path[0] != '' else ''}/", 0
    if file is None:
        for ff in os.listdir(local_location):
            if os.path.isfile(local_location + ff):
                file_size = max(file_size, os.path.getsize(local_location + ff))
    else:
        file_size = os.path.getsize(local_location + file)
    if file_size == 0:
        return

    seen.add(canonical)
    if result == 'Solved':
        repo.points_acquired += points
        repo.solved += 1
    elif result == 'Unsolved':
        solution_count[(canonical, points)] += 1
        repo.points_missing += points
        repo.unsolved += 1
        if file is None:
            unsolved.append([canonical, points, f'-{file_size}', f"https://github.com/{repo.name}/tree/{repo.branch}/{'/'.join(path)}".replace(' ', '%20')])
        else:
            unsolved.append([canonical, points, file_size, f"https://github.com/{repo.name}/blob/{repo.branch}{('/' + '/'.join(path)) if path[0] != '' else ''}/{file}".replace(' ', '%20')])
    elif dir_result != 'Solved' and dir_result != 'Unsolved' and not repo.ignore_unknown:
        repo.unknownFiles.append((canonical, file, full_path))
        repo.unknown += 1
    # else:
    #     print("ERROR: ",(canonical, file, path[-1]))


path_ignore = [
    '/.', '/_', '@todo', '/venv', '/Practice', '/debug', '/dist-newstyle/', '/unsolved',
    'codingame', 'hackerrank', 'vjudge', 'leetcode', 'adventofcode',
    'cmake-build-debug',
    '/node_modules/',
    '/obj/Debug',
    '/bin/Debug',
    '/data/secret',
    'scl2022', 'noi_2020', 'scl2021',
    '/MatthewFreestone/Kattis/DataStructures',
    '/jasonincanada/kattis/cs/semirings',
    '/olasundell/kattis/src/main/java/util',
]


def find_unsolved_problems(repo: Repo):
    unsolved = []
    seen = set()
    for x in os.walk(repo.solutions):
        if any(ignore in x[0] for ignore in path_ignore):
            continue
        waste, github_user, repo_name, *rest = x[0].split("/")
        dir_canonical, dir_points, dir_result = util.check_problem(rest[-1].lower())
        handle_repo_solution(dir_canonical, dir_points, dir_result, repo, rest, seen, unsolved, full_path=x[0])
        for file in x[2]:
            if not os.path.isfile(f"{x[0]}/{file}") or any(ignore in file.lower() for ignore in path_ignore):
                continue
            canonical, points, result = util.check_problem(file.lower(), rest[-1])
            handle_repo_solution(canonical, points, result, repo, rest, seen, unsolved, file=file,
                                 dir_result=dir_result, full_path=x[0])
    if len(unsolved) > 0:
        print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
        print("🔱 Unsolved Problems In " + repo.name)
        print(tabulate(sorted(unsolved), headers=["Problem ID", "Points", "Size", "Link"], tablefmt='outline', floatfmt='0.1f'))


def print_repo_stats():
    for repo in repo_list:
        find_unsolved_problems(repo)
    solved, unsolved, unknown = 0, 0, 0
    rows = []
    for repo in sorted(repo_list, key=lambda rr: (rr.points_missing, rr.points_acquired)):
        solved += repo.solved
        unsolved += repo.unsolved
        unknown += repo.unknown
        rows.append((repo.name, repo.solved, round(repo.points_acquired), repo.unsolved, round(repo.points_missing), repo.last_commit, '-' if repo.ignore_unknown else repo.unknown))
        if len(repo.unknownFiles) > 0:
            print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
            print('', repo.name)
            print("  Unknown: ")
            for x in sorted(repo.unknownFiles):
                path = ''
                for xx in x[2].split('/'):
                    if util.check_problem(xx.lower())[1] != -1:
                        path += '/**' + xx + "**"
                    else:
                        path += '/' + xx
                print(f"'{x[0]}'", f"'{x[1]}' ->", path)
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print(
        tabulate(rows, headers=["Repository Name", "Solved", "Points", "Unsolved", "Points", "Last Commit", "Unknown"], tablefmt='outline'))
    print("➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖")
    print("Total Solved: ", solved, "Total Unsolved: ", unsolved, "Total Unknown: ", unknown)


def print_most_solved_problems():
    print("🔱 Most Solved Problems")
    print(tabulate(map(lambda x: [*x[0]] + [x[1]], sorted(solution_count.items(), key=lambda x: x[1], reverse=True)[:20]), headers=["Problem ID", "Points", "Solved"], tablefmt='outline'))


def main():
    args = sys.argv[1:]
    if '--skip' not in args:
        print("--------------------- Cloning & Syncing Git Repos ------------------------")
        if not os.path.exists('repos'):
            os.mkdir('repos')
        for repo in repo_list:
            create_and_sync_repo(repo)

    if '--scrape' in args:
        kattis_sync.update_solution_cache()
        # kattis_sync.update_problem_created_at()
        kattis_sync.update_problem_length()
        kattis_sync.update_problem_solved_at()
    print_repo_stats()
    print_most_solved_problems()


if __name__ == '__main__':
    main()
