from random import randint, shuffle, choice,random
from math import comb
import subprocess
import time

compiled = set()


def generate_data():
    """Generate test data and write it to data.txt"""
    with open('input.txt', 'w') as f:
        a = randint(2, 400)
        f.write(f"{comb(a, randint(1, a//2 + 1))}\n")


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
        result_other = run_python('other_solution')
        result_me = run_python('my_solution')
        if result_me == result_other:
            print('OK', result_me)
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
