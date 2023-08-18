from random import randint, shuffle, choice,random
import subprocess

compiled = set()


def generate_data():
    """Generate test data and write it to data.txt"""
    with open('input.txt', 'w') as f:
        f.write("1\n")
        f.write("450 2\n")
        for _ in range(3):
            x = randint(4400, 4500)
            f.write(f"{x} {int(x * 1.005)}\n")


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
    for _ in range(100):
        generate_data()
        result_other = run_cpp('other_solution')
        result_me = run_java('wine')
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
