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
    return True  # return True if creating file successfully


def insert_domains(csp, domains):
    for key, value in domains.items():
        csp['domains'][key].extend(value)
        csp['domains'][key].sort()


# removes all `val` values in `csp.domains`.
# validate remaining domains of all variables in the csp.
# if the rest domains is valid, then `status` is `True`;
# otherwise `status` is `False`.
def inference(csp, val):
    domains_removed = {}

    for var in csp['domains']:
        if val in csp['domains'][var]:
            csp['domains'][var].remove(val)
            domains_removed[var] = []
            domains_removed[var].append(val)
            if not csp['visited'][var] and len(csp['domains'][var]) == 0:
                return (domains_removed, False)

    return (domains_removed, True)
