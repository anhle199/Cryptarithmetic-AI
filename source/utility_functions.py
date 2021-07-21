import re
import copy


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
def write_file(filename, assignment):
    # create output file
    try:
        f = open(filename, "w")
    except:
        return False # return False if there is an error in creating output file

    result = []
    for key, value in assignment.items():
        result.append((key, value))

    def sort_with_key(item): # define sorting criteria
        return item[0]

    result.sort(key=sort_with_key)

    # write file
    for item in result:
        f.write(str(item[1]))

    # close file
    f.close()
    return True # return True if creating file successfully


def find_index_of_element_less_than(a, val):
    for i in range(len(a)):
        if a[i] >= val:
            return i
    return len(a)


def insert_domains(csp, domains):
    for key, value in domains.items():
        index = find_index_of_element_less_than(csp['domains'][key], value)
        csp['domains'][key].insert(index, value)


# removes all `val` values in `csp.domains`.
# validate remaining domains of all variables in the csp.
# if the rest domains is valid, then `status` is `True`;
# otherwise `status` is `False`.
def inference(assignment, csp, val):
    domains_removed = {}

    for var in csp['domains'].keys():
        if val in csp['domains'][var].values():
            csp['domains'][var].remove(val)
            domains_removed[var].append(val)
            if not csp['visited'][var] and len(csp['domains'][var]) == 0:
                return (domains_removed, False)

    return (domains_removed, True)


def sum_column(assignment, csp, col, domains_removed):
    # sum all element in `col` column
    val = csp['constraints'][col]['carry']
    for operand in csp['constraints'][col]['operands']:
        val += int(operand)

    # calculate the carry
    carrt = val // 10
    csp['constraints'][col]['carry'] = carry
    val %= 10

    # if sum is leading, then 0 < sum < 10
    if col == len(csp['constraints']) - 1 and carry != 0:
        return False

    var = csp['constraints'][col]['result']
    if csp['visited'][var]:
        return assignment[var] == val
    elif val in assignment.values():  # csp['visited'][var] = false
        return False

    # apply sum to csp and infer
    assignment[var] = val
    infer_result = inference(assignment, csp, val)

    for key, value in infer_result[0].items():  # infer_result.domains_removed
        domains_removed[key].append(value)

    if not infer_result[1]:  # infer_result.status
        del assignment[var]

    return infer_result[1]


def backtracking(assginment, csp, col, i):
    var = csp['constraints'][col]['operands'][i]
    is_calc = (i == len(csp['constraints'][col]['operands']))

    if var != '0' and not csp['visited'][var]:
        csp['visited'][var] = True
        domains = copy.deepopy(csp['domains'][var])

        for val in domains:
            if val not in assginment.values():
                assignment[var] = val
                (domains_removed, status) = inference(assignment, csp, val)

                if status:
                    result = True
                    if is_calc:
                        result = sum_column(assignment, csp, col, domains_removed)
                        if result:
                            csp['visited'][csp['constraints'][col]['result']] = True

                    if result:
                        if col == len(csp['constraints']) - 1 and is_calc:
                            return result

                        col += 1 if is_calc else 0
                        i = 0 if is_calc else i + 1
                        next_var = csp['constraints'][col]['operands'][i]
                        clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

                        result = backtracking(assginment, csp, col, i)
                        if result:
                            return result

                        csp['domains'][next_var] = copy.deepcopy(clone_domains_next_var)
                        if is_calc:
                            csp['visited'][csp['constraints'][col + 1]['result']] = False

                del assignment[var]
                insert_domains(csp, domains_removed)
                csp['domains'][var].remove(val)

        csp['visited'][var] = False
        return False

    else:
        domains_removed = {}
        result = True

        if is_calc:
            result = sum_column(assignment, csp, col, domains_removed)
        if not (col == len(csp['constraints']) - 1 and is_calc) and result:
            col += 1 if is_calc esle 0
            i = 0 if is_calc else i + 1
            next_var = csp['constraints'][col]['operands'][i]
            clone_domains_next_var = copy.deepcopy(csp['domains'][next_var])

            if is_calc:
                csp['visited'][csp['constraints'][col]['result']] = True

            result = backtracking(assginment, csp, col, i)
            csp['domains'][next_var] = copy.deepcopy(clone_domains_next_var)
            if is_calc and not result:
                csp['visited'][csp['constraints'][col]['result']] = False

        if is_calc and not result:
            insert_domains(csp, domains_removed)

        return result
