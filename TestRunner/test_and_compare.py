from random import randint
import subprocess

compiled = set()


def generate_data():
    """Generate test data and write it to data.txt"""
    n = randint(1, 1)
    with open('data.txt', 'w') as f:
        f.write(f'{randint(2, 10)} {randint(2, 10)}')


def run_python_and_capture_output(path):
    result = subprocess.run(['python3', path], input=open('data.txt', 'rb').read(), capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stderr.decode('utf-8'))
    return result.stdout.decode('utf-8').strip()


def run_java_and_capture_output(name):
    if name not in compiled:
        result = subprocess.run(['javac', name + '.java'], capture_output=True)
        if result.returncode != 0:
            raise Exception(result.stderr.decode('utf-8'))
        compiled.add(name)

    result = subprocess.run(['java', name], input=open('data.txt', 'rb').read(), capture_output=True)
    if result.returncode != 0:
        raise Exception(result.stderr.decode('utf-8'))
    return result.stdout.decode('utf-8').strip()


def main():
    for _ in range(100):
        generate_data()
        result_other = run_python_and_capture_output('other_code.py')
        result_me = run_java_and_capture_output('factorialpower')
        if result_me == result_other:
            print('OK')
        else:
            print('WA')
            with open('data.txt', 'r') as f:
                test_data = f.read()
                print(test_data)
                print("Other code result:")
                print(result_other)
                print("My code result:")
                print(result_me)
            break


if __name__ == '__main__':
    main()
