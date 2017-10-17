"""Source for all Gaussian related functions"""
import re

from .atom import Atom


def get_geom(lines, geom_type='xyz', units='angstrom'):
    """
    Takes the lines of an orca output file and returns its last geometry in the
    specified format
    """
    start = ''
    end = ' ' + '-'*69 + '\n'
    if geom_type == 'xyz' and units == 'angstrom':
        start = ' Number     Number       Type             X           Y           Z\n'
    else:
        raise ValueError('Unsupported format or geom_type')

    geom_start = -1
    # Iterate backwards until the start of the last set of coordinates is found
    for i in reversed(list(range(len(lines)))):
        if start == lines[i]:
            geom_start = i + 2
            break
    if geom_start == -1:
        print("Could not find start of geometry")
        return ''

    geom = []
    for line in lines[geom_start:]:
        if line == end:
            break
        idx, an, a_type, x, y, z = line.split()
        geom.append('{:<2s} {} {} {}'.format(Atom.atomic_number(an), x, y, z))

    return geom
