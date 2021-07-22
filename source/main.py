from utility_functions import *


def solve(csp):
    if len(csp['variables']) > 10:
        return None

    assignment = {}
    has_solution = backtracking(assignment, csp, 0, 0)
    if has_solution:
        return assignment
    return None


if __name__ == '__main__':
    input_file_path = '../files/input.txt'
    output_file_path = '../files/output.txt'

    data = read_file(input_file_path)
    if data != None:
        csp = create_csp(data)
        assignment = solve(csp)

        result = 'NO SOLUTION'
        has_solution = (assignment != None)
        if has_solution:
            result = ''
            for item in sorted(assignment.items()):
                result += str(item[1])

        write_file(output_file_path, result)
        print(result)
    else:
        print('Cannot open:', input_file_path)
