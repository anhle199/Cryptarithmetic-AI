import copy
import re


# Error: return None | Success: return {'operands': operands, 'operators': operators, 'result': result}
def read_file(filename):
    # open input file
    try:
        f = open(filename, "r")
    except FileNotFoundError:
        return None # return None if there is an error in opening input file

    # variables for returning
    operands = []
    operators = []
    result = ""

    # process input string
    temp_string = f.readline()
    for item in re.split(r"([+-=*])", temp_string):
        if item == "+" or item == "-" or item == "*":
            operators.append(item)
        elif item != "=":
            operands.append(item)
    result = operands.pop()

    # close file and return result
    f.close()
    return {'operands': operands, 'operators': operators, 'result': result} # successfully read file


# Error: return False | Success: return True
def write_file(filename, result):
    # create output file
    try:
        f = open(filename, "w")
    except:
        return False # return False if there is an error in creating output file

    f.write(result)
    f.close()
    return True # return True if creating file successfully


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
    words_list.append(result)


    # some leadings is not equal to zero
    leading_possible_zero = set()
    leading_impossible_zero = set()
    for word in words_list:
        if len(word) == 1:
            leading_possible_zero.add(word[0])
        else:
            leading_impossible_zero.add(word[0])

    leading_impossible_zero.difference_update(leading_possible_zero)
    for var in leading_impossible_zero:
        csp['domains'][var].remove(0)


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


def insert_domains(csp, domains):
    for key, value in domains.items():
        # index = find_index_of_element_less_than(csp['domains'][key], value)
        # csp['domains'][key].insert(index, value)
        csp['domains'][key].extend(value)
        csp['domains'][key].sort()


# removes all `val` values in `csp.domains`.
# validate remaining domains of all variables in the csp.
# if the rest domains is valid, then `status` is `True`;
# otherwise `status` is `False`.
def inference(assignment, csp, val):
    domains_removed = {}

    for var in csp['domains']:
        if val in csp['domains'][var]:
            csp['domains'][var].remove(val)
            domains_removed[var] = []
            domains_removed[var].append(val)
            if not csp['visited'][var] and len(csp['domains'][var]) == 0:
                return (domains_removed, False)

    return (domains_removed, True)


def calculate(lhs, rhs, operator):
    if operator == '+':
        return lhs + rhs
    if operator == '-':
        return lhs - rhs
    if operator == '*':
        return lhs * rhs
    return 0


def sum_all_rest_leading(assignment, csp):
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
            if not csp['visited'][var] and (val in assignment or val not in csp['domains'][var]):
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


# return value: (is_mark, status)
def sum_column(assignment, csp, col, domains_removed):
    # sum all element in `col` column
    val = csp['constraints'][col]['carry']
    operands = csp['constraints'][col]['operands']
    val += 0 if operands[0] == '0' else assignment[operands[0]]
    for i in range(1, len(operands)):
        rhs = 0 if operands[i] == '0' else assignment[operands[i]]
        val = calculate(val, rhs, csp['operators'][i - 1])

    # calculate the carry
    carry = val // 10
    val %= 10

    if col < len(csp['constraints']) - 1:
        csp['constraints'][col + 1]['carry'] = 0

    var = csp['constraints'][col]['result']
    domains = csp['domains'][var]
    if csp['visited'][var]:
        if assignment[var] == val:
            if col < len(csp['constraints']) - 1:
                csp['constraints'][col + 1]['carry'] = carry
            return (False, True)
        return (False, False)
    if val in assignment.values() or val not in domains:  # csp['visited'][var] = false
        return (False, False)

    # if sum is leading, then 0 < sum < 10
    if col == len(csp['constraints']) - 1 and carry != 0:
        return (False, False)
    if col < len(csp['constraints']) - 1:
        csp['constraints'][col + 1]['carry'] = carry

    # apply sum to csp and infer
    assignment[var] = val
    csp['visited'][var] = True
    infer_result = inference(assignment, csp, val)

    for key, value in infer_result[0].items():  # infer_result.domains_removed
        if key not in domains_removed:
            domains_removed[key] = []
        domains_removed[key].extend(value)

    if not infer_result[1]:  # infer_result.status
        del assignment[var]

    return (True, infer_result[1])


def backtracking(assignment, csp, col, i):
    len_result, len_longest = csp['length']['result'], csp['length']['longest_operand']
    if col == csp['length']['longest_operand'] and len_result > len_longest:
        return sum_all_rest_leading(assignment, csp)

    var = csp['constraints'][col]['operands'][i]
    is_calc = (i == len(csp['constraints'][col]['operands']) - 1)

    if var != '0' and not csp['visited'][var]:
        domains = copy.deepcopy(csp['domains'][var])

        for val in domains:
            if val not in assignment.values():
                assignment[var] = val
                csp['visited'][var] = True
                (domains_removed, status) = inference(assignment, csp, val)

                if status:
                    result = True
                    is_mark = False
                    if is_calc:
                        (is_mark, result) = sum_column(assignment, csp, col, domains_removed)

                    if result:
                        if col == len(csp['constraints']) - 1 and is_calc:
                            return result

                        clone_col_i = (col, i)
                        col += 1 if is_calc else 0
                        i = 0 if is_calc else i + 1
                        next_var = csp['constraints'][col]['operands'][i]
                        clone_domains_next_var = []
                        if next_var != '0':
                            clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

                        result = backtracking(assignment, csp, col, i)
                        if result:
                            return result

                        col = clone_col_i[0]
                        i = clone_col_i[1]
                        if next_var != '0':
                            csp['domains'][next_var] = copy.deepcopy(clone_domains_next_var)
                    if not result and is_mark:
                        csp['visited'][csp['constraints'][col]['result']] = False

                del assignment[var]
                csp['visited'][var] = False
                insert_domains(csp, domains_removed)
                csp['domains'][var].remove(val)
        return False

    else:
        domains_removed = {}
        result = True
        is_mark = False
        if is_calc:
            (is_mark, result) = sum_column(assignment, csp, col, domains_removed)

        if not (col == len(csp['constraints']) - 1 and is_calc):
            if result:
                clone_col_i = (col, i)
                col += 1 if is_calc else 0
                i = 0 if is_calc else i + 1
                next_var = csp['constraints'][col]['operands'][i]
                clone_domains_next_var = []
                if next_var != '0':
                    clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

                result = backtracking(assignment, csp, col, i)
                if result:
                    return result

                col = clone_col_i[0]
                i = clone_col_i[1]
                if next_var != '0':
                    csp['domains'][next_var] = copy.deepcopy(clone_domains_next_var)

        if not result:
            insert_domains(csp, domains_removed)
            if is_mark:
                csp['visited'][csp['constraints'][col]['result']] = False
        return result
