from random import randint, shuffle, choice,random
import subprocess

compiled = set()


def generate_data():
    """Generate test data and write it to data.txt"""
    x = randint(1, 100)
    with open('input.txt', 'w') as f:
        f.write("100 10\n")
        f.write("707169221 41608301 101586402 393006344 859553265 730023425 98814853 477972519 166309797 232573781 780896817 296557660 462568221 332140093 476440388 929670827 390185874 127825418 549723534 714034592 627159951 447041669 846601260 334545617 610845899 567525566 359169134 492494772 235497283 887279329 176330745 698552539 491145993 460854453 191704407 732336865 828420484 412146074 370728695 179795679 999098300 567203308 464971038 651451124 567021462 273755624 608948553 789472236 161100690 848498651 131725514 961892574 414665650 649170386 501932761 694345321 848440282 854287694 326359402 77821656 843650236 564962392 410319836 724440261 235394031 273305964 721348846 575901808 374150150 523632565 23124086 551171914 983557339 667687411 69351084 664179885 963000490 784711346 392851314 417655912 742169169 355023150 596908941 90594892 150378734 438964443 826216324 476215157 786953683 736684095 557754330 41962299 25212032 374208046 900106957 534384422 351410895 959683619 18854761 18836144\n")
        # f.write(f"{randint(1,523)} {randint(1,1000000000)} {randint(1,10000)}\n")
        for _ in range(10):
            f.write(f"{randint(1, 100000)}\n")


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
        result_me = run_java('atomicenergy')
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
