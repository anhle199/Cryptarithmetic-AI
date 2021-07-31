import sys
import first_three_level
import level_four
import utility_funcs
from threading import Thread, Event


bridge = Event()


def solve(input_filename, output_filename):
    data = utility_funcs.read_file(input_filename)
    if data != None:
        csp, assignment = None, None
        if data['operators'][0] == '*':  # level 4
            (solved, assignment) = level_four.pre_proccess(data)
            if not solved:
                csp = level_four.create_csp(data)
                assignment = level_four.execute(csp, bridge)
        else:  # level 1, 2, 3
            csp = create_csp(data)
            assignment = first_three_level.execute(csp, bridge)

        result = 'NO SOLUTION'
        has_solution = (assignment != None)
        if has_solution:
            result = ''
            variables = ''
            for item in sorted(assignment.items()):
                result += str(item[1])
                variables += item[0]
            print(variables, '=', end = ' ')

        utility_funcs.write_file(output_filename, result)
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
