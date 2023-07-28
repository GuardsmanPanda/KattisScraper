from random import randint, shuffle
import subprocess

compiled = set()


def generate_data():
    """Generate test data and write it to data.txt"""
    with open('input.txt', 'w') as f:
        f.write(f"5\n")
        for _ in range(5):
            if randint(0, 1) == 0:
                f.write(f"1 {randint(1, 10)}\n")
            else:
                f.write(f"2 {randint(1, 10)} {randint(1, 10)}\n")


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
        run_result(['javac', name + '.java'])
        compiled.add(name)
    return run_result(['java', name])


def run_cpp(name):
    if name not in compiled:
        run_result(['g++', name + '.cpp', '-o', name + ".o"])
        compiled.add(name)
    return run_result(['./' + name + ".o"])


def main():
    for _ in range(100):
        generate_data()
        result_other = run_python('other_solution')
        result_me = run_go('my_solution')
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
