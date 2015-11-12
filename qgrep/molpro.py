"""Molpro functions"""

import re
from qgrep.atom import Atom

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
        idx, atom, charge, x, y, z = line.split()
        geom.append('{:<2s} {} {} {}'.format(atom, x, y, z))

    return geom

def get_energy(lines):
    """Get the energy"""
    # The energy will always be on the third line from the end, zeroth element
    energy = lines[-3].split()[0]

    return energy
