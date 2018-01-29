"""Source for all orca related functions"""
import numpy as np

from .helper import BOHR_TO_ANGSTROM
from operator import itemgetter


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

    scale = 1
    units = units.lower()
    if units == 'angstrom':
        scale = BOHR_TO_ANGSTROM
    elif units != 'bohr':
        raise Exception('Invalid Units')

    geom = []
    line_form = '{:s} {} {} {}\n'
    for line in lines[geom_start: geom_end]:
        atom, *xyz = [q.strip('",') for q in itemgetter(3, 7, 8, 9)(line.split())]
        xyz = [scale*float(q) for q in xyz]
        geom.append(line_form.format(atom, *xyz))

    return geom


def plot(lines, type='xyz'):
    """Plots the geometries from the optimization steps"""

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


def template(geom='', jobtype='optimize', functional='B3LYP', basis='svp'):
    """Returns a template with the specified geometry and other variables"""
    template_style = """{{ "bagel" : [

{{
  "title" : "molecule",
  "symmetry" : "C1",
  "basis" : "{1}",
  "df_basis" : "svp-jkfit",
  "angstrom" : false,
  "geometry" : [
  {2}
  ]
}},

{{
  "title" : "{0}",
  "method" : [ {{
    "title" : "rohf",
    "nact" : 0,
    "thresh" : 1.0e-10
  }} ]
}}

]}}
"""
    return template_style.format(jobtype, basis, geom)


def convert_to_bagel_geom(geom_str):
    """
    Converts to a bagel formatted geometry (json format)
    """
    bagel_geom = ''
    geom_form = '[{:>15.10f},{:>15.10f},{:>15.10f}] }},\n'
    for line in geom_str.strip().split('\n'):
        atom, *xyz = line.split()
        bagel_geom += f'{{"atom" : "{atom:s}", '
        if len(atom) == 1:
            bagel_geom += ' '
        bagel_geom += geom_form.format(*map(float, xyz))

    return bagel_geom[:-2]
