from utility_functions import *


def solve(csp):
    if len(csp['variables']) > 10:
        return {}

	infer_same_operand(csp)

	assignment = {}
	has_solution = backtracking(assignment, csp, len(csp.constraints) - 1, 0)
	if has_solution:
		return assignment
    return


if __name__ == '__main__':
    input_file_path = '../files/input.txt'
    output_file_path = '../files/output.txt'

    data = read_file(input_file_path)
    has_solution = False
    if data != None:
        csp = create_csp(data)
        assignment = solve(csp)
        write_file(output_file_path)
        has_solution = len(assignment) != 0

    if not has_solution:
        print("NO SOLUTION")