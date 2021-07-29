import copy
import re


# this function is used for breaking all brackets in the expression
def break_bracket(operators):
    reList = []
    n = len(operators)
    reverse_flag = False
    index = 0
    while (index < n):
        if (operators[index] == "("):
            if (reverse_flag):
                next = index + 1
                while (True):
                    if (operators[next] == "+"):
                        reList.append("-")
                        reverse_flag = True
                    elif (operators[next] == "-"):
                        reList.append("+")
                        reverse_flag = False
                    elif (operators[next] == "("):
                        index = next - 1
                        break
                    elif (operators[next] == ")"):
                        index = next
                        break
                    next += 1
        elif (operators[index] != ")"):
            if (operators[index] == "+"):
                reverse_flag = False
            else:
                reverse_flag = True
            reList.append(operators[index])
        index += 1
    return reList

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
    if temp_string[-1] == '\n':
        temp_string = temp_string[:-1]
    for item in re.split(r"([+-=()*])", temp_string):
        if item == "+" or item == "-" or item == "*" or item == "(" or item == ")":
            operators.append(item)
        elif item != "=" and item != "":
            operands.append(item)
    result = operands.pop()

    post_processing_operators = break_bracket(operators)

    # close file and return result
    f.close()
    return {'operands': operands, 'operators': post_processing_operators, 'result': result} # successfully read file


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


# return value: (status, is_mark, is_removed)
# status: True or False
# is_mark: True or False
# is_removed: True or False if `is_mark` is True. Otherwise, the value is None.
def sum_column(assignment, csp, col, domains_removed):
    # sum all element in `col` column
    val = csp['constraints'][col]['carry']
    operands = csp['constraints'][col]['operands']
    val += 0 if operands[0] == '0' else assignment[operands[0]]
    for i in range(1, len(operands)):
        rhs = 0 if operands[i] == '0' else assignment[operands[i]]
        val = calculate(val, rhs, csp['operators'][i - 1])

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
            # if sum is leading, then 0 < sum < 10
            if col == len(csp['constraints']) - 1 and carry != 0:
                return (False, False, None)
            if col < len(csp['constraints']) - 1:
                csp['constraints'][col + 1]['carry'] = carry
            return (True, False, None)
        return (False, False, None)

    domains = csp['domains'][var]
    if csp['visited'][var]:
        if assignment[var] == val:
            if col == len(csp['constraints']) - 1 and carry != 0:
                return (False, False, None)
            if col < len(csp['constraints']) - 1:
                csp['constraints'][col + 1]['carry'] = carry
            return (True, False, None)
        return (False, False, None)
    if val in assignment.values() or val not in domains:  # csp['visited'][var] = false
        return (False, False, None)

    # if sum is leading, then 0 < sum < 10
    if col == len(csp['constraints']) - 1 and carry != 0:
        return (False, False, None)
    if col < len(csp['constraints']) - 1:
        csp['constraints'][col + 1]['carry'] = carry

    # apply sum to csp and infer
    assignment[var] = val
    csp['visited'][var] = True
    is_removed = False
    infer_result = inference(assignment, csp, val)

    for key, value in infer_result[0].items():  # infer_result.domains_removed
        if key not in domains_removed:
            domains_removed[key] = []
        domains_removed[key].extend(value)

    if not infer_result[1]:  # infer_result.status
        is_removed = True
        del assignment[var]

    return (infer_result[1], True, is_removed)


def backtracking(assignment, csp, col, i):
    len_result, len_longest = csp['length']['result'], csp['length']['longest_operand']
    if col == csp['length']['longest_operand'] and len_result > len_longest and csp['constraints'][col]['carry'] >= 0:
        return sum_all_rest_leading(assignment, csp)

    var = csp['constraints'][col]['operands'][i]
    is_calc = (i == len(csp['constraints'][col]['operands']) - 1)

    if var != '0' and not csp['visited'][var]:
        domains = copy.deepcopy(csp['domains'][var])

        for val in domains:
            if val not in assignment.values():
                #print(1, assignment)
                #print(1, csp['visited'])
                assignment[var] = val
                csp['visited'][var] = True
                #print(1, assignment)
                #print(1, csp['visited'])
                (domains_removed, status) = inference(assignment, csp, val)

                if status:
                    result, is_mark, is_removed = True, False, None
                    if is_calc:
                        #print(2, assignment)
                        #print(2, csp['visited'])
                        (result, is_mark, is_removed) = sum_column(assignment, csp, col, domains_removed)
                        #print(2, assignment)
                        #print(2, csp['visited'])
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

                        #print(3, assignment)
                        #print(3, csp['visited'])
                        result = backtracking(assignment, csp, col, i)
                        #print(3, assignment)
                        #print(3, csp['visited'])
                        if result:
                            return result

                        col = clone_col_i[0]
                        i = clone_col_i[1]
                        if next_var != '0':
                            csp['domains'][next_var] = copy.deepcopy(clone_domains_next_var)

                    if not result and is_mark:
                        #print(4, assignment)
                        #print(4, csp['visited'])
                        var_result = csp['constraints'][col]['result']
                        csp['visited'][var_result] = False
                        if not is_removed:
                            del assignment[var_result]
                            #print(4, assignment)
                            #print(4, csp['visited'])

                #print(5, assignment)
                #print(5, csp['visited'])
                del assignment[var]
                csp['visited'][var] = False
                #print(5, assignment)
                #print(5, csp['visited'])
                insert_domains(csp, domains_removed)
                csp['domains'][var].remove(val)
        return False

    else:
        domains_removed = {}
        result, is_mark, is_removed = True, False, None
        if is_calc:
            #print(6, assignment)
            #print(6, csp['visited'])
            (result, is_mark, is_removed) = sum_column(assignment, csp, col, domains_removed)
            #print(6, assignment)
            #print(6, csp['visited'])
        if not (col == len(csp['constraints']) - 1 and is_calc):
            if result:
                clone_col_i = (col, i)
                col += 1 if is_calc else 0
                i = 0 if is_calc else i + 1
                next_var = csp['constraints'][col]['operands'][i]
                clone_domains_next_var = []
                if next_var != '0':
                    clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

                #print(7, assignment)
                #print(7, csp['visited'])
                result = backtracking(assignment, csp, col, i)
                #print(7, assignment)
                #print(7, csp['visited'])
                if result:
                    return result

                col = clone_col_i[0]
                i = clone_col_i[1]
                if next_var != '0':
                    csp['domains'][next_var] = copy.deepcopy(clone_domains_next_var)

        if not result:
            insert_domains(csp, domains_removed)
            if is_mark:
                var_result = csp['constraints'][col]['result']
                #print(8, assignment)
                #print(8, csp['visited'])
                csp['visited'][var_result] = False
                if not is_removed:
                    del assignment[var_result]
                #print(8, assignment)
                #print(8, csp['visited'])
        return result
