import copy

def degree_heuristic(csp):
    var = None
    count_constraint = 0

    for key, value in csp['operands'].items():
        if not value['visited'] and value['count_constraint'] > count_constraint:
            var = key
            count_constraint = value['count_constraint']

    if var != None:
        csp['operands'][var]['visited'] = True

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
                not csp['operands'][variable]['visited']
            ):
                status = False
                break

    return (domains_removed, status)

# def isFull(assignment, csp)
# def sum_cryptarithmetic(data, assignment)

def backtracking(data, assignment, csp, var):
    if var == None:
        return isFull(csp, assignment) and sum_cryptarithmetic(data, assignment):
    else:
        csp['operands'][var]['visited'] = True
        domains = copy.deepcopy(csp['domains'][var])  # set

        for val in domains:
            if val not in assignment.values():
                assignment[var] = val
                (domains_removed, status) = inference(assignment, csp, var, val)

                if status:
                    next_var = degree_heuristic(csp)
                    clone_domain_next_char = copy.deepcopy(csp['domains'][next_var])
                    result = backtracking(data, assignment, csp, next_var)
                    csp['domains'][next_var] = copy.deepcopy(clone_domain_next_char)

                    if result:
                        return result

                del assignment[var]
                for key, value in domains_removed.items():
                    if key != var:
                        csp['domains'][key].add(value)

        csp['operands'][var]['visited'] = False
        return False
