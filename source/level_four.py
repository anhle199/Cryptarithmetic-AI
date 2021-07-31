import copy
import utility_funcs

def multiply_with_zero(data):
    first_op, second_op, result = data['operands'][0], data['operands'][1], data['result']
    if first_op[0] == second_op[0] or second_op[0] != result[0]:
        return None

    assignment = { second_op[0]: 0 }
    val = 1
    for var in first_op:
        if var not in assignment:
            assignment[var] = val
            val += 1
    return assignment


def pre_proccess(data):
    if len(list(set(''.join(data['operands']) + data['result']))) > 10:
        return (True, None)

    solved = False
    assignment = None
    len_result, len_first_op, len_second_op = len(data['result']), len(data['operands'][0]), len(data['operands'][1])
    if len_first_op < len_second_op:
        data[operands[0]], data[operands[1]] = data[operands[1]], data[operands[0]]
        len_first_op, len_second_op = len_second_op, len_first_op

    min_len_result = len_first_op
    max_len_result = len_first_op + len_second_op
    if len_first_op > 1 and len_second_op == 1 and len_result == 1:
        assignment = {}
        assignment = multiply_with_zero(data)
        solved = True
    elif len_result < min_len_result or len_result > max_len_result:
        solved = True

    return (solved, assignment)


def execute(csp, bridge):
    assignment = {}
    has_solution = backtracking(assignment, csp, 0, 0, 0, bridge)

    if has_solution:
        return assignment
    return None


# Create csp
def create_csp(data):
    # Get all fields in data
    operands, operators, result = data["operands"], data["operators"], data["result"]
    variables = list(set(''.join(operands) + result))

    # return format
    csp = {
        "variables": copy.deepcopy(variables),
        "constraints": [],
        "visited": {},
        "domains": {},
        'has_dummy': False
    }

    # initialize `visited` and `domains` properties of csp
    for var in variables:
        csp["visited"][var] = False
        csp["domains"][var] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    var_impossible_zero = set([operands[0][0], operands[1][0], result[0]])
    for var in var_impossible_zero:
        csp['domains'][var].remove(0)

    csp['constraints'] = [{ 'operands': [], 'result': result[-i - 1], 'carry': 0 } for i in range(len(result))]
    for i in range(len(operands[1])):
        for j in range(len(operands[0])):
            csp['constraints'][i + j]['operands'].append((operands[0][-j - 1], operands[1][-i - 1]))

    if len(csp['constraints'][-1]['operands']) == 0:
        csp['constraints'][-1]['operands'].append(('0', '0'))  # dummy
        csp['has_dummy'] = True

    return csp


def calc_column(assignment, csp, col, domains_removed):
    # calc all element in `col` column
    operands = csp['constraints'][col]['operands']
    val = csp['constraints'][col]['carry']
    for (first, second) in operands:
        val += assignment[first] * assignment[second]

    # calculate carry and calculate again result to match with carry
    carry = val // 10
    val %= 10

    if col < len(csp['constraints']) - 1:
        csp['constraints'][col + 1]['carry'] = 0

    var = csp['constraints'][col]['result']

    if csp['visited'][var]:
        if assignment[var] == val:
            if col == len(csp['constraints']) - 1 and carry != 0:
                return (False, False, None)
            if col < len(csp['constraints']) - 1:
                csp['constraints'][col + 1]['carry'] = carry
            return (True, False, None)
        return (False, False, None)
    if val in assignment.values() or val not in csp['domains'][var]:  # csp['visited'][var] = false
        return (False, False, None)

    # if it is leading, then 0 < sum or diffrence < 10
    if col == len(csp['constraints']) - 1 and carry != 0:
        return (False, False, None)
    if col < len(csp['constraints']) - 1:
        csp['constraints'][col + 1]['carry'] = carry

    # apply sum or difference to csp and infer
    assignment[var] = val
    csp['visited'][var] = True
    is_removed = False
    infer_result = utility_funcs.inference(csp, val)

    for key, value in infer_result[0].items():  # infer_result.domains_removed
        if key not in domains_removed:
            domains_removed[key] = []
        domains_removed[key].extend(value)

    if not infer_result[1]:  # infer_result.status
        is_removed = True
        del assignment[var]

    return (infer_result[1], True, is_removed)


def calc_next_index(col, i, j, is_calc):
    col += 1 if is_calc else 0
    if is_calc:
        i, j = 0, 0
    else:
        i += 1 if j == 1 else 0
        j = 0 if j == 1 else j + 1

    return (col, i, j)


def backtracking(assignment, csp, col, i, j, bridge):
    if bridge.is_set():
        return False

    # carry must be one
    if col == len(csp['constraints']) - 1 and csp['has_dummy']:
        carry = csp['constraints'][col]['carry']
        if carry == 0:
            return False
        else:
            var = csp['constraints'][col]['result']
            if csp['visited'][var]:
                return assignment[var] == carry
            elif carry not in assignment.values():
                if carry in csp['domains'][var]:
                    assignment[var] = carry
                    csp['visited'][var] = True
                    return True
            return False

    var = csp['constraints'][col]['operands'][i][j]
    is_calc = (i == len(csp['constraints'][col]['operands']) - 1) and (j == 1)

    if var != '0' and not csp['visited'][var]:
        domains = copy.deepcopy(csp['domains'][var])

        for val in domains:
            if val not in assignment.values():
                assignment[var] = val
                csp['visited'][var] = True
                (domains_removed, status) = utility_funcs.inference(csp, val)

                if status:
                    result, is_mark, is_removed = True, False, None
                    if is_calc:
                        (result, is_mark, is_removed) = calc_column(assignment, csp, col, domains_removed)
                    if result:
                        if col == len(csp['constraints']) - 1 and is_calc:
                            return result

                        clone_index = (col, i, j)
                        (col, i, j) = calc_next_index(col, i, j, is_calc)
                        next_var = csp['constraints'][col]['operands'][i][j]
                        clone_domains_next_var = []
                        if next_var != '0':
                            clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

                        result = backtracking(assignment, csp, col, i, j, bridge)
                        if result:
                            return result

                        (col, i, j) = clone_index
                        if next_var != '0':
                            csp['domains'][next_var] = copy.deepcopy(clone_domains_next_var)

                    if not result and is_mark:
                        var_result = csp['constraints'][col]['result']
                        csp['visited'][var_result] = False
                        if not is_removed:
                            del assignment[var_result]

                del assignment[var]
                csp['visited'][var] = False
                utility_funcs.insert_domains(csp, domains_removed)
                csp['domains'][var].remove(val)

        return False
    else:
        domains_removed = {}
        result, is_mark, is_removed = True, False, None
        if is_calc:
            (result, is_mark, is_removed) = calc_column(assignment, csp, col, domains_removed)
        if not (col == len(csp['constraints']) - 1 and is_calc):
            if result:
                clone_index = (col, i, j)
                (col, i, j) = calc_next_index(col, i, j, is_calc)
                next_var = csp['constraints'][col]['operands'][i][j]
                clone_domains_next_var = []
                if next_var != '0':
                    clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

                result = backtracking(assignment, csp, col, i, j, bridge)
                if result:
                    return result

                (col, i, j) = clone_index
                if next_var != '0':
                    csp['domains'][next_var] = copy.deepcopy(clone_domains_next_var)

        if not result:
            utility_funcs.insert_domains(csp, domains_removed)
            if is_mark:
                var_result = csp['constraints'][col]['result']
                csp['visited'][var_result] = False
                if not is_removed:
                    del assignment[var_result]

        return result
