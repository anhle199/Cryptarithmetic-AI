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

