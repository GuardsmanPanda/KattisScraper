import kattis_sync
import subprocess
import util
import sys
import os


class Repo:
    def __init__(self, name):
        self.name = name
        self.path = "repos/" + name


repo_list = [
    Repo("RussellDash332/kattis"),
    Repo("donaldong/kattis")
]


def create_and_sync_repos():
    print("--------------------- Cloning Git Repos ------------------------")
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
                        print(line)
            else:
                print("ERROR UPDATING: " + rep.name)
                print(res.returncode)
                print(res.stderr.readlines())


def main():
    if sys.argv[1] == '--scrape':
        kattis_sync.update_solution_cache()
        # kattis_sync.update_problem_created_at()
        kattis_sync.update_problem_length()
        kattis_sync.update_problem_solved_at()
    create_and_sync_repos()


if __name__ == '__main__':
    main()
