from random import randint, shuffle, choice, random
from math import comb
import subprocess
import time

compiled = set()


def generate_data():
    """Generate test data and write it to data.txt"""
    arr = [["." for _ in range(8)] for _ in range(8)]
    arr[randint(0, 7)][randint(0, 7)] = 'k'
    arr[randint(0, 7)][randint(0, 7)] = 'K'
    arr[randint(0, 7)][randint(0, 7)] = 'R'
    if sum(1 for cc in arr for c in cc if c == '.') != 61:
        return
    with open('input.txt', 'w') as f:
        for a in arr:
            f.write(f"{''.join(a)}\n")


def run_result(command):
    result = subprocess.run(command, input=open('input.txt', 'rb').read(), capture_output=True, shell=True)
    if result.returncode != 0:
        raise Exception(result.stderr.decode('utf-8'))
    return result.stdout.decode('utf-8').strip()


def run_python(name):
    return run_result([f'python3 {name}.py'])


def run_go(name):
    return run_result([f'go run {name}.go'])


def run_java(name):
    if name not in compiled:
        run_result([f'javac {name}.java'])
        compiled.add(name)
    return run_result([f'java {name}'])


def run_cpp(name):
    if name not in compiled:
        run_result([f'g++ {name}.cpp -o {name}.o'])
        compiled.add(name)
    return run_result(['./' + name + ".o"])


def main():
    for _ in range(1000):
        generate_data()
        result_other = run_cpp('other_solution')
        result_me = run_java('checkmateinone')
        if result_me == result_other:
            print('OK')
        else:
            print('WA')
            with open('input.txt', 'r') as f:
                test_data = f.read()
                print(test_data)
                print("Other code result:")
                print(result_other)
                print("My code result:")
                print(result_me)
            break


if __name__ == '__main__':
    main()
