from utility_functions import *
# ODD*ODD=FREAKY
# TWO*TWO=SQUARE
# HIP*HIP=HURRAY
# MAD*MAN=ASYLUM


def multiply():
    


def backtracking_level4(assignment, csp):



def solve(csp):
    if len(csp['variables']) > 10:
        return None

    assignment = {}
    has_solution = backtracking_level4(assignment, csp, 0, 0)

    if has_solution:
        return assignment
    return None


if __name__ == '__main__':
    input_file_path = '../files/input.txt'
    output_file_path = '../files/output.txt'

    data = read_file(input_file_path)
    if data != None:
        operands = data['operands']
        if len(operands[0]) < len(operands[1]):
            operands[0], operands[1] = operands[1], operands[0]

        csp = create_csp(data)
        assignment = solve(csp)

        result = 'NO SOLUTION'
        has_solution = (assignment != None)
        if has_solution:
            result = ''
            variables = ''  # this line need deleteing when submitting
            for item in sorted(assignment.items()):
                result += str(item[1])
                variables += item[0]  # this line need deleteing when submitting
            print(variables, '=', end = ' ')  # this line need deleteing when submitting
        # write_file(output_file_path, result)
        print(result)
    else:
        print('Cannot open:', input_file_path)
