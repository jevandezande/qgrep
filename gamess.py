import os
from molecule import Molecule
from helper import atomic_number, convert_name
from basis import BasisSet


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
    energy = 0
    if energy_type != 'sp':
        raise SyntaxError("Invalid energy type")
    energy_line = ' '*23 + 'TOTAL ENERGY'
    for line in reversed(lines):
        if line[:35] == energy_line:
            energy = line.split()[-1]
            break

    return energy


class Gamessifier():
    """Class for making Gamess input files"""
    def __init__(self):
        self.mol = Molecule()
        self.basis_set = BasisSet()
        self.ecp = {}
        self.other = ''

    def read_mol(self, geom_file='geom.xyz'):
        """Reads a geometry file and generates a molecule"""
        self.mol.read(geom_file)

    def read_basis_set(self, basis_file='basis.gbs'):
        """Reads a basis file and makes a dictionary with the form atom:basis_functions"""
        self.basis_set.read_basis_set(basis_file, style='gamess')

    def read_ecp(self, ecp_file='ecp.dat'):
        """Reads an ecp file and makes a dictionary with the form atom:ecp"""
        lines = open(ecp_file).readlines()
        self.ecp = {}
        i = 0
        while i < len(lines):
            name, ecp_type = lines[i].split()[:2]
            name = name.split('-')[0]
            if ecp_type == 'GEN':
                self.ecp[name] = lines[i]
                done = False
                while not done:
                    i += 1
                    if lines[i][0] == ' ':
                        self.ecp[name] += lines[i]
                    else:
                        done = True
            elif ecp_type == 'NONE':
                self.ecp[name] = lines[i]
                i += 1
            else:
                raise SyntaxError('Invalid ecp type, only GEN and NONE are currently accepted.')

    def read_other(self, other_file=''):
        """Reads a file that will be prepended to the input file"""
        if other_file:
            self.other = open(other_file).read()

    def write_input(self, input_file='input.inp', comment=''):
        """Makes an input file with the given geometry and basis"""
        data = ' $DATA\n{}\nC1\n'.format(comment)
        ecp = ' $ECP\n'
        for name, x, y, z in self.mol:
            an = atomic_number(name)
            atom_basis = self.basis_set[name].print(style='gamess', print_name=False)
            data += '{} {}     {}  {}  {}\n{}\n'.format(name, an, x, y, z, atom_basis)
            if name in self.ecp:
                ecp += self.ecp[name].strip() + '\n'
            else:
                ecp += '{}-ECP NONE\n'.format(name)
        data += ' $END\n'
        ecp += ' $END\n'
        input_data = '{}\n{}\n{}'.format(self.other, data, ecp)
        open(input_file, 'w').write(input_data)
