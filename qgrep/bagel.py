"""Source for all orca related functions"""
import numpy as np

from .helper import BOHR_TO_ANGSTROM
from operator import itemgetter


def get_geom(lines, style='xyz', units='angstrom'):
    """
    Takes the lines of a bagel output file and returns its last geometry in the specified format
    :param lines: lines of a bagel output file
    :param style: output style for geom
    :param units: units for geometry
    """
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

    scale = 1
    units = units.lower()
    if units == 'angstrom':
        scale = BOHR_TO_ANGSTROM
    elif units != 'bohr':
        raise ValueError('Invalid Units')

    geom = []
    for line in lines[geom_start: geom_end]:
        atom, *xyz = [q.strip('",') for q in itemgetter(3, 7, 8, 9)(line.split())]
        x, y, z = [scale*float(q) for q in xyz]
        geom.append(f'{atom} {x} {y} {z}')

    return geom


def plot(lines, style='xyz'):
    """
    Plots the geometries from the optimization steps
    :param lines: lines of a bagel output file
    """

    return get_geom(lines, style)


def check_convergence(lines):
    """
    Returns all the geometry convergence results
    :param lines: lines of a bagel output file
    """
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


def template(geom='', jobtype='optimize', basis='svp'):
    """
    Returns a template with the specified geometry and other variables
    :param geom: geometry
    :param jobtype: type of job to run (single point, optimization, frequencies)
    :param basis: basis set to use
    """
    return f"""{{ "bagel" : [

{{
  "title" : "molecule",
  "symmetry" : "C1",
  "basis" : "{basis}",
  "df_basis" : "svp-jkfit",
  "angstrom" : false,
  "geometry" : [
  {geom}
  ]
}},

{{
  "title" : "{jobtype}",
  "method" : [ {{
    "title" : "rohf",
    "nact" : 0,
    "thresh" : 1.0e-10
  }} ]
}}

]}}
"""


def convert_to_bagel_geom(geom_str):
    """
    Converts an xyz geometry sting to a bagel formatted geometry (json format)
    :param geom_str: xyz geometry to convert
    """
    bagel_geom = ''
    for line in geom_str.strip().splitlines():
        atom, *xyz = line.split()
        bagel_geom += f'{{"atom" : "{atom:s}", '
        if len(atom) == 1:
            bagel_geom += ' '
        x, y, z = map(float, xyz)
        bagel_geom = f'[{x:>15.10f},{y:>15.10f},{z:>15.10f}] }},\n'

    return bagel_geom[:-2]
