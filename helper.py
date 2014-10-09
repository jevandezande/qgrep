"""A repository for various helper functions"""


def read(file):
    """Reads the given file and returns its lines and the type of program that uses it"""
    with open(file, 'r') as f:
        lines = f.readlines()
    program = check_program(lines)

    return lines, program


def check_program(lines):
    """Takes the lines of an output file and determines what program wrote (or reads) them"""
    programs = {
        '* O   R   C   A *': 'orca',
        'Welcome to Q-Chem': 'qchem',
        'PSI4: An Open-Source Ab Initio Electronic Structure Package': 'psi4',
        'Northwest Computational Chemistry Package (NWChem)': 'nwchem',
        '#ZMATRIX': 'zmatrix',
        '* CFOUR Coupled-Cluster techniques for Computational Chemistry *': 'cfour',
        '***  PROGRAM SYSTEM MOLPRO  ***': 'molpro',
        "----- GAMESS execution script 'rungms' -----": 'gamess'
    }

    program = None
    for line in lines:
        line = line.strip()
        if line in programs:
            program = programs[line]
            break

    return program
