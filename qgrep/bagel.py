"""Source for all orca related functions"""
from qgrep.molecule import Molecule
from operator import itemgetter

import numpy as np


def get_geom(lines, type='xyz', units='angstrom'):
    """Takes the lines of a bagel output file and returns its last geometry in the specified format"""
    start = '  *** Geometry ***'
    end = '\n'
    geom_start = -1
    geom_end = -1
    for i, line in reversed(list(enumerate(lines))):
        if line[:18] == start:
            geom_start = i + 4
            break
    if geom_start == -1:
        raise Exception('Could not find start of geometry')

    for i, line in enumerate(lines[geom_start:], start=geom_start):
        if line == end:
            geom_end = i
            break
    if geom_end == -1:
        raise Exception('Could not find end of geometry')

    geom = []
    line_form = '{:s} {} {} {}'
    for line in lines[geom_start: geom_end]:
        atom, x, y, z = [q.strip('",') for q in itemgetter(3, 7, 8, 9)(line.split())]
        geom.append(line_form.format(atom, x, y, z))

    return geom


def plot(lines, type='xyz'):
    """Plots the the geometries from the optimization steps"""

    return get_geom(lines)


def check_convergence(lines):
    """Returns all the geometry convergence results"""
    convergence_start = '  *** Geometry optimization started ***'
    for i, line in enumerate(lines):
        if line[:39] == convergence_start:
            convergence_list = []
            for line in lines[i+3:]:
                line = line.strip()
                if not line:
                    break
                convergence_list.append(line)
            return convergence_list
    raise Exception('Could not find convergence')


def template(geom='', jobtype='Opt', functional='B3LYP', basis='sto-3g'):
    """Returns a template with the specified geometry and other variables"""

    return template_style.format(jobtype, functional, basis, geom)


def get_freqs(lines):
    return output


def get_ir(lines):
    """
    Returns all of the vibrational frequencies
    """
    return vib_freqs


def get_energy(lines, energy_type='sp'):
    """Returns the last calculated energy
    WARNING: It returns as a string in order to prevent python from rounding"""
    return energy


def get_molecule(lines):
    """
    Make a molecule object from the last geometry
    """
    return mol
