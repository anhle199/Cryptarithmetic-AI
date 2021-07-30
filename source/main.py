from utility_functions import *
import sys
from threading import Thread, Event


bridge = Event()


def first_three_level(csp):
    if len(csp['variables']) > 10:
        return None

    assignment = {}
    has_solution = backtracking(assignment, csp, 0, 0, bridge)

    if has_solution:
        return assignment
    return None


def solve(input_filename, output_filename):
    input_filename = sys.argv[1]
    output_filename = 'output.txt'

    data = read_file(input_filename)
    if data != None:
        csp = create_csp(data)
        assignment = None
        if csp['operators'][0] == '*':  # level 4
            assignment = None
        else:  # level 1, 2, 3
            assignment = first_three_level(csp)

        result = 'NO SOLUTION'
        has_solution = (assignment != None)
        if has_solution:
            result = ''
            variables = ''  # this line need deleteing when submitting
            for item in sorted(assignment.items()):
                result += str(item[1])
                variables += item[0]  # this line need deleteing when submitting
            print(variables, '=', end = ' ')  # this line need deleteing when submitting

        write_file(output_filename, result)
        print(result)
    else:
        print('Cannot open:', input_filename)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main_thread = Thread(target=solve, args=(sys.argv[1], 'output.txt',))

        print('This program will execute in 2 minutes.')
        print('After 2 minutes, it will automatically terminate and print NO SOLUTION.')
        main_thread.start()
        main_thread.join(timeout=120)

        bridge.set()
    else:
        print('The number of command-line arguments is invalid.')
