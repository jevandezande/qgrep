"""A repository for various helper functions"""
import numpy as np

BOHR_TO_ANGSTROM=0.52917721067


def read(file_name):
    """
    Reads the given file and returns its lines and the type of program that uses
    it
    """
    with open(file_name, 'r') as f:
        lines = f.readlines()
    program = check_program(file_name)

    return lines, program


def check_program(file_name):
    """
    Takes the name of an output file and determines what program wrote (or
    reads) them
    :param file_name: name of the output file
    :return: string of the program or None
    """
    programs = {
        '* O   R   C   A *': 'orca',
        'Welcome to Q-Chem': 'qchem',
        'PSI4: An Open-Source Ab Initio Electronic Structure Package': 'psi4',
        'Psi4: An Open-Source Ab Initio Electronic Structure Package': 'psi4',
        'Northwest Computational Chemistry Package (NWChem)': 'nwchem',
        '#ZMATRIX': 'zmatrix',
        '* CFOUR Coupled-Cluster techniques for Computational Chemistry *': 'cfour',
        '***  PROGRAM SYSTEM MOLPRO  ***': 'molpro',
        "----- GAMESS execution script 'rungms' -----": 'gamess',
        'N A T U R A L   A T O M I C   O R B I T A L   A N D': 'nbo',
        'Entering Gaussian System, Link 0=g09': 'gaussian',
        '***  PROGRAM SYSTEM MOLPRO  ***': 'molpro', # Printed after input file
        'BAGEL - Freshly leavened quantum chemistry': 'bagel',
    }

    program = None
    with open(file_name) as f:
        for i in range(200):
            line = f.readline().strip()
            if line in programs:
                program = programs[line]
                break

    return program


def find_input_program(in_file):
    """
    Find the type of input file based on unique identifiers

    :param: in_file: file name string
    :return: string of the program or None
    """
    lines = open(in_file).readlines()
    if '***,' == lines[0][:4]:
        return 'molpro'
    elif '% pal nprocs ' == lines[0][:13]:
        return 'orca'

    for line in lines:
        if '$NBO' == line[:4]:
            return 'nbo'
        if '$' == line[0]:
            return 'qchem'
        elif '*CFOUR(' == line[:7]:
            return 'cfour'
        elif '* xyz' == line[:5] or '* int' == line[:5]:
            return 'orca'
        elif ' $' == line[:2]:
            return 'gamess'
        elif 'molecule' == line[:8] or 'set ' == line[:4]:
            return 'psi4'
    return None


# Values from NIST
energy_conversions = {
    'hartree': {'hartree': 1, 'kJ/mol': 2625.49962, 'kcal/mol': 627.509, 'eV': 27.21138602, '1/cm': 2.194746313702e5},
    'kJ/mol': {'hartree': 3.8088e-4, 'kJ/mol': 1, 'kcal/mol': 0.23901, 'eV': 1.0364e-2, '1/cm': 83.593},
    'kcal/mol': {'hartree': 1.5936e-3, 'kJ/mol': 4.1840, 'kcal/mol': 1, 'eV': 4.3363e-2, '1/cm': 349.75},
    'eV': {'hartree': 3.6749e-2, 'kJ/mol': 96.485, 'kcal/mol': 23.061, 'eV': 1, '1/cm': 8065.5},
    '1/cm': {'hartree': 4.556335252767e-6, 'kJ/mol': 1.1963e-2, 'kcal/mol': 2.8591e-3, 'eV': 1.2398e-4, '1/cm': 1}
}


def convert_energy(data, in_type='hartree', out_type='kcal/mol'):
    if in_type not in energy_conversions or out_type not in energy_conversions[in_type]:
        raise SyntaxError("Unsupported energy type, please use {}".format(list(energy_conversions.keys())))
    conversion = energy_conversions[in_type][out_type]

    if isinstance(data, (int, float)):
        return data * conversion
    elif isinstance(data, np.ndarray):
        return data * np.full(data.shape, conversion)
    elif isinstance(data, (list, tuple)):
        try:
            return [conversion * i for i in data]
        except TypeError:
            raise SyntaxError("List may only be filled with numbers.")
    else:
        raise SyntaxError(type(data) + " is not currently supported. Please use int, float, np.ndarray, or list")


class colors:
    normal = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    purple = '\033[95m'


box_drawing = """\
┌┬─┐
││ │
├┼─┤
└┴─┘
"""
