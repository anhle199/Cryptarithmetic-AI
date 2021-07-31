import copy
import re
import utility_funcs


def execute(csp, bridge):
    if len(csp['variables']) > 10:
        return None

    assignment = {}
    has_solution = backtracking(assignment, csp, 0, 0, bridge)

    if has_solution:
        return assignment
    return None


# Find the longest word
def find_longest_word(words):
    if len(words) == 0:
        return "Empty array"
    longest = words[0]
    for i in range(1, len(words)):
        if len(words[i]) > len(longest):
            longest = words[i]

    return longest


# Create csp
def create_csp(data):
    # Get all fields in data
    operands, operators, result = data["operands"], data["operators"], data["result"]
    variables = list(set(''.join(operands) + result))

    # return format
    csp = {
        "variables": copy.deepcopy(variables),
        "constraints": [],
        "operators": copy.deepcopy(operators),
        "visited": {},
        "domains": {},
        'length': {}
    }

    # initialize `visited` and `domains` properties of csp
    for var in variables:
        csp["visited"][var] = False
        csp["domains"][var] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # find the word has longest length
    longest = find_longest_word(operands)
    csp['length'] = {
        'longest_operand': len(longest),
        'result': len(result)
    }
    if len(longest) < len(result):
        longest = result

    # words_list = [...operands, result]
    words_list = copy.deepcopy(operands)
    # words_list.append(result)


    # some leadings is not equal to zero
    leading_possible_zero = set()
    leading_impossible_zero = set()
    for word in words_list:
        if len(word) == 1:
            leading_possible_zero.add(word[0])
        else:
            leading_impossible_zero.add(word[0])

    if len(result) == 1 and result[0] not in leading_impossible_zero:
        leading_possible_zero.add(result[0])
    else:
        leading_impossible_zero.add(result[0])

    leading_impossible_zero.difference_update(leading_possible_zero)
    for var in leading_impossible_zero:
        csp['domains'][var].remove(0)


    words_list.append(result)
    # Transform a single word from TWO to 0TWO - fill up by zero at head
    for i in range(len(words_list)):
        words_list[i] = words_list[i].zfill(len(longest))

    for i in range(len(longest) - 1, -1, -1):
        constraint = {
            "operands": [],
            "result": words_list[-1][i],
            "carry": 0
        }

        for j in range(len(words_list)):
            # The last character of a word
            char = words_list[j][i]
            constraint["operands"].append(char)

        constraint['operands'].pop()
        csp["constraints"].append(constraint)

    return csp


def calc_all_rest_leading(assignment, csp):
    len_result, len_longest = csp['length']['result'], csp['length']['longest_operand']
    values = str(csp['constraints'][len_longest]['carry'])
    offset = len_result - len_longest

    if len(set(values)) == len(values) and len(values) == offset:
        j = offset
        for i in range(len_longest, len_result):
            j -= 1
            var = csp['constraints'][i]['result']
            val = int(values[j])

            if csp['visited'][var] and assignment[var] != val:
                return False
            if not csp['visited'][var] and (val in assignment.values() or val not in csp['domains'][var]):
                    return False

        j = offset
        for i in range(len_longest, len_result):
            j -= 1
            var = csp['constraints'][i]['result']
            val = int(values[j])
            assignment[var] = val

        return True
    else:
        return False


def calc(lhs, rhs, operator):
    if operator == '+':
        return lhs + rhs
    if operator == '-':
        return lhs - rhs
    if operator == '*':
        return lhs * rhs
    return 0


# return value: (status, is_mark, is_removed)
# status: True or False
# is_mark: True or False
# is_removed: True or False if `is_mark` is True. Otherwise, the value is None.
def calc_column(assignment, csp, col, domains_removed):
    # calc all element in `col` column
    operands = csp['constraints'][col]['operands']
    val = csp['constraints'][col]['carry']
    val += 0 if operands[0] == '0' else assignment[operands[0]]
    for i in range(1, len(operands)):
        rhs = 0 if operands[i] == '0' else assignment[operands[i]]
        val = calc(val, rhs, csp['operators'][i - 1])

    # calculate carry and calculate again result to match with carry
    carry = 0
    if val < 0:
        while val < 0:
            val += 10
            carry -= 1
    else:
        carry = val // 10
        val %= 10

    if col < len(csp['constraints']) - 1:
        csp['constraints'][col + 1]['carry'] = 0

    var = csp['constraints'][col]['result']
    if var == '0':
        if val == 0:
            if col == len(csp['constraints']) - 1 and carry != 0:
                return (False, False, None)
            if col < len(csp['constraints']) - 1:
                csp['constraints'][col + 1]['carry'] = carry
            return (True, False, None)
        return (False, False, None)

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


def calc_next_index(col, i, is_calc):
    col += 1 if is_calc else 0
    i = 0 if is_calc else i + 1
    return (col, i)


def backtracking(assignment, csp, col, i, bridge):
    if bridge.is_set():
        return False

    len_result, len_longest = csp['length']['result'], csp['length']['longest_operand']
    if col == csp['length']['longest_operand'] and len_result > len_longest and csp['constraints'][col]['carry'] >= 0:
        return calc_all_rest_leading(assignment, csp)

    var = csp['constraints'][col]['operands'][i]
    is_calc = (i == len(csp['constraints'][col]['operands']) - 1)

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

                        clone_col_i = (col, i)
                        (col, i) = calc_next_index(col, i, is_calc)
                        next_var = csp['constraints'][col]['operands'][i]
                        clone_domains_next_var = []
                        if next_var != '0':
                            clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

                        result = backtracking(assignment, csp, col, i, bridge)
                        if result:
                            return result

                        (col, i) = clone_col_i
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
                clone_col_i = (col, i)
                (col, i) = calc_next_index(col, i, is_calc)
                next_var = csp['constraints'][col]['operands'][i]
                clone_domains_next_var = []
                if next_var != '0':
                    clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

                result = backtracking(assignment, csp, col, i, bridge)
                if result:
                    return result

                (col, i) = clone_col_i
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
