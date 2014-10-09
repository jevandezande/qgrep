"""Source for all orca related functions"""


def check_convergence(lines):
    """Returns all the geometry convergence results"""
    convergence_result = 'MAXIMUM GRADIENT'
    convergence_list = []
    for i in range(len(lines)):
        if convergence_result in lines[i]:
            convergence_list.append(''.join(lines[i:i+3:2]))

    return convergence_list
