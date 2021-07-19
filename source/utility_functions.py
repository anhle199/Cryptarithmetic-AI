def read_file(filename):
    ## open input file
    try:
        f = open("../files/input.txt", "r")
    except FileNotFoundError:
        return None ## return None if there is an error in opening input file

    ## variables for returning
    operands = []
    operators = []
    result = ""

    ## process input string
    import re
    temp_string = f.readline()
    for item in re.split(r"([+-=*])", temp_string):
        if item == "+" or item == "-" or item == "*":
            operators.append(item)
        elif item != "=":
            operands.append(item)
    result = operands.pop()

    ## close file and return result
    f.close()
    return operands, operators, result ## successfully read file

def degree_heuristic(csp):
    var = None
    count_constraint = 0

    for key, value in csp['variables_in_operand'].items():
        if not value['visited'] and value['count_constraint'] > count_constraint:
            var = key
            count_constraint = value['count_constraint']

    if var != None:
        csp['variables_in_operand'][var]['visited'] = True

    return var


def inference(assignment, csp, var, val):
    domains_removed = { var: val }
    status = True

    # remove `val` in domain of all of variables
    for variable in csp['domains']:
        if val in csp['domains'][variable]:
            domains_removed[variable] = val
            csp['domains'][variable].remove(val)

            if (
                len(csp['domains'][variable]) == 0 and
                not csp['variables_in_operand'][variable]['visited']
            ):
                status = False
                break

    return (domains_removed, status)
