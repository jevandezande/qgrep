import os
import re
from collections import OrderedDict
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
        self.options_str = ''
        self.options_dict = {}
        self.vec = ''
        self.hess = ''
        self.vec_re = re.compile("^ \$VEC.*?^ \$END", re.MULTILINE + re.DOTALL)
        self.hess_re = re.compile("^ \$HESS.*?^ \$END", re.MULTILINE + re.DOTALL)

    def read_mol(self, geom_file='geom.xyz'):
        """Reads a geometry file and generates a molecule"""
        self.mol = Molecule()
        if not geom_file:
            return
        if not os.path.isfile(geom_file):
            print("Couldn't find geom file: " + geom_file)
            return

        self.mol.read(geom_file)

    def read_basis_set(self, basis_file='basis.gbs'):
        """Reads a basis file and makes a dictionary with the form atom:basis_functions"""
        self.basis_set = BasisSet()
        if not basis_file:
            return
        if not os.path.isfile(basis_file):
            print("Couldn't find basis file: " + basis_file)
            return

        self.basis_set.read_basis_set(basis_file, style='gamess')

    def read_ecp(self, ecp_file='ecp.dat'):
        """Reads an ecp file and makes a dictionary with the form atom:ecp"""
        self.ecp = ''
        if not ecp_file:
            return
        if not os.path.isfile(ecp_file):
            print("Couldn't find ecp file: " + ecp_file)
            return

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

    def read_options(self, options):
        """Reads options that will be prepended to the input file"""
        self.options_str = ''
        self.options_dict = OrderedDict()
        if isinstance(options, str):
            if os.path.isfile(options):
                self.options_str = open(options).read()
                matches = re.findall('^ \$\w+.*?\$END', self.options_str, re.DOTALL + re.MULTILINE)
                for match in matches:
                    lines = match.split('\n')
                    block = lines[0][2:].strip()
                    self.options_dict[block] = OrderedDict()
                    for line in lines[1:-1]:
                        key, value = line.split('=')
                        self.options_dict[block][key.strip()] = value.strip()
            else:
                print('Could not read options.')
        elif isinstance(options, dict):
            # Dictionary of form
            # { block1:((option1, value1), (option2,value2)), block2:((option1, value1)) }
            for block, values in options.items():
                self.options_str += ' ${}\n'.format(block.upper())
                self.options_str += '\n'.join(['    {}={}'.format(key, value) for key, value in values.items()])
                self.options_str += '\n $END\n\n'
        else:
            raise SyntaxError('Invalid options format, must be either a string or a dictionary.')

    def read_data(self, dat_file='input.dat'):
        """Read vec and hess from .dat file that gamess makes"""
        self.vec = ''
        self.hess = ''
        if not dat_file:
            return
        if not os.path.isfile(dat_file):
            print("Couldn't find dat file: " + dat_file)
        data = open(dat_file).read()
        vec_result = re.findall(self.vec_re, data)
        hess_result = re.findall(self.hess_re, data)
        if vec_result:
            self.vec = vec_result[-1]
        if hess_result:
            self.hess = hess_result[-1]

    def read(self, geom_file='geom.xyz', basis_file='basis.gbs', ecp_file='ecp.dat',
             options='other.dat', dat_file='input.dat'):
        """Quick method to read eveything"""
        self.read_mol(geom_file)
        self.read_basis_set(basis_file)
        self.read_ecp(ecp_file)
        self.read_options(options)
        self.read_data(dat_file)

    def write_input(self, input_file='input.inp', comment=''):
        """Makes an input file with the given geometry and basis"""
        data = ' $DATA\n{}\nC1\n'.format(comment)
        ecp = ' $ECP\n'
        for name, x, y, z in self.mol:
            if len(name) > 1:
                name = name[0].upper() + name[1:].lower()
            an = atomic_number(name)
            atom_basis = self.basis_set[name].print(style='gamess', print_name=False)
            data += '{} {}     {}  {}  {}\n{}\n'.format(name, an, x, y, z, atom_basis)
            if name in self.ecp:
                ecp += self.ecp[name].strip() + '\n'
            else:
                ecp += '{}-ECP NONE\n'.format(name)
        data += ' $END\n'
        ecp += ' $END\n'
        input_data = '{}\n{}\n{}\n{}\n{}'.format(self.options_str, data, ecp, self.vec, self.hess)
        open(input_file, 'w').write(input_data)
