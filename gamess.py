"""Source for all orca related functions"""


def check_convergence(lines):
    """Returns all the geometry convergence results"""
    convergence_result = 'MAXIMUM GRADIENT'
    convergence_list = []
    for i in range(len(lines)):
        if convergence_result in lines[i]:
            convergence_list.append(''.join(lines[i+2].strip()))

    return convergence_list

def get_geom(lines, type='xyz', units='angstrom'):
    """Takes the lines of an output file and returns its last geometry in the specified format"""
    start = ' COORDINATES OF ALL ATOMS ARE (ANGS)\n'
    end = '\n'
    if type=='zmat' or units=='bohr':
        raise SyntaxError("Currently only supports Angstroms and xyz coordinates")

    geom_start = -1
    # Iterate backwards until the start of the last set of coordinates is found
    for i in reversed(list(range(len(lines)))):
        if start == lines[i]:
            geom_start = i + 3
            break
    if geom_start == -1:
        print("Could not find start of geometry")
        return ''

    geom_end = -1
    for i in range(geom_start, len(lines)):
        if end == lines[i]:
            geom_end = i
            break
    if geom_end == -1:
        return ''

    geom = lines[geom_start: geom_end]

    return geom

def get_energy(lines, energy_type='sp'):
    """Returns the energy"""
    if energy_type != 'sp':
        raise SyntaxError("Invalid energy type")
    energy_line = ' '*23 + 'TOTAL ENERGY'
    for line in reversed(lines):
        if line[:35] == energy_line:
            energy = line.split()[-1]
            break

    return energy
