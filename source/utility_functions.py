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
