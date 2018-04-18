"""Molpro functions"""
from .helper import BOHR_TO_ANGSTROM


def get_geom(lines, geom_type='xyz', units='angstrom'):
    """
    Takes the lines of a Molpro output file and returns its last geometry in the
    specified format
    """
    end = '\n'
    if geom_type == 'xyz' and units == 'angstrom':
        start = ' ATOMIC COORDINATES\n'
    else:
        raise ValueError('Unsupported format or geom_type')

    geom_start = -1
    # Iterate backwards until the start of the last set of coordinates is found
    for i in reversed(list(range(len(lines)))):
        if start == lines[i]:
            geom_start = i + 4
            break
    if geom_start == -1:
        print("Could not find start of geometry")
        return ''

    geom = []
    for line in lines[geom_start:]:
        if line == end:
            break
        idx, atom, charge, *xyz = line.split()
        x, y, z = map(lambda q: float(q)*BOHR_TO_ANGSTROM, xyz)
        geom.append(f'{atom:<2s} {x} {y} {z}')

    return geom


def get_energy(lines, energy_type=''):
    """Get the energy"""
    energy = lines[-3].split()[0]

    return energy


def check_convergence(lines):
    """
    Check the convergence
    """
    starts = []
    for i, line in enumerate(lines):
        if line[:19] == ' Optimization point':
            starts.append(i)

    convs = []
    for start in starts:
        for line in lines[:start]:
            if line[:12] == ' Convergence':
                n, grad, hessian = line.split()[-3:]
                convs.append(f'{n}  {grad}')
    return convs
