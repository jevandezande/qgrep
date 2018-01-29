import os
import re

from collections import OrderedDict

from .atom import Atom
from .basis import BasisSet
from .molecule import Molecule


def check_convergence(lines):
    """Returns all the geometry convergence results"""
    convergence_result = 'MAXIMUM GRADIENT'
    convergence_list = []
    for i in range(len(lines)):
        if convergence_result in lines[i]:
            convergence_list.append(''.join(lines[i + 2].strip()))

    return convergence_list


def get_geom(lines, geom_type='xyz', units='angstrom'):
    """
    Takes the lines of an output file and returns its last geometry in the
    specified format
    """
    start = ' COORDINATES OF ALL ATOMS ARE (ANGS)\n'
    end = '\n'
    if geom_type == 'zmat' or units == 'bohr':
        raise SyntaxError(
            "Currently only supports Angstroms and xyz coordinates")

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

    geom = []
    for line in lines[geom_start: geom_end]:
        atom, an, x, y, z = line.split()
        geom.append('\t'.join([atom, x, y, z]))

    return geom


def plot(lines, geom_type='xyz'):
    """Plots the geometries from the optimization steps"""
    start = ' COORDINATES OF ALL ATOMS ARE (ANGS)\n'
    end = '\n'
    geoms = []
    i = 0
    step = 0
    while i < len(lines):
        if lines[i] == start:
            i += 3
            start_num = i
            while lines[i] != end:
                i += 1
            end_num = i
            geom = f'{end_num - start_num}\nStep {step}\n'
            for line in lines[start_num:end_num]:
                atom, num, x, y, z = line.split()
                geom += '\t'.join([atom, x, y, z]) + '\n'

            geoms.append(geom)
            step += 1
        i += 1

    return geoms


def get_energy(lines, energy_type='sp'):
    """Returns the energy"""
    energy = 0
    if energy_type != 'sp':
        raise SyntaxError("Invalid energy type")
    energy_line = ' ' * 23 + 'TOTAL ENERGY'
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
        self.options_dict = {}
        self.vec = ''
        self.hess = ''
        self.vec_re = re.compile("^ \$VEC.*?^ \$END", re.MULTILINE + re.DOTALL)
        self.hess_re = re.compile("^ \$HESS.*?^ \$END",
                                  re.MULTILINE + re.DOTALL)

    def read_mol(self, geom_file='geom.xyz'):
        """Reads a geometry file and generates a molecule"""
        self.mol = Molecule()
        if not geom_file:
            return
        if not os.path.isfile(geom_file):
            print("Couldn't find geom file: " + geom_file)
            return

        self.mol = Molecule.read_from(geom_file)

    def read_basis_set(self, basis_file='basis.gbs'):
        """
        Reads a basis file and makes a dictionary with the form
        atom:basis_functions
        """
        self.basis_set = BasisSet()
        if not basis_file or not os.path.isfile(basis_file):
            raise Exception("Couldn't find basis file: " + basis_file)

        self.basis_set = BasisSet.read(basis_file, style='gamess')

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
                raise SyntaxError('Invalid ecp type, only GEN and NONE are'
                                  'currently accepted.')

    def write_options_str(self):
        """
        Make a string out of the options
        options_dict is of the form
        {
            block1:((option1, value1), (option2,value2)),
            block2:((option1, value1))
        }
        """
        options_str = ''
        for block, values in self.options_dict.items():
            block_options = '\n'.join(
                [f'    {key}={value}' for key, value in values.items()])
            options_str += f' ${block.upper()}\n{block_options}\n $END\n\n'
        return options_str

    def read_options(self, options='options.dat'):
        """Reads options that will be prepended to the input file"""
        self.options_dict = OrderedDict()
        if isinstance(options, str):
            if os.path.isfile(options):
                options_str = open(options).read()
                matches = re.findall('^ \$\w+.*?\$END', options_str,
                                     re.DOTALL + re.MULTILINE)
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
            self.options_dict = options
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

    def read(self, geom_file='geom.xyz', basis_file='basis.gbs',
             ecp_file='ecp.dat',
             options='options.dat', dat_file='input.dat'):
        """Quick method to read eveything"""
        self.read_mol(geom_file)
        self.read_basis_set(basis_file)
        self.read_ecp(ecp_file)
        self.read_options(options)
        if os.path.isfile(dat_file):
            self.read_data(dat_file)

    def update_options(self):
        """Update options based on available data"""
        if self.vec:
            if not 'GUESS' in self.options_dict:
                self.options_dict['GUESS'] = OrderedDict()
            self.options_dict['GUESS']['GUESS'] = 'MOREAD'
        else:
            # If no vector, make sure that the guess is not MOREAD
            try:
                if self.options_dict['GUESS']['GUESS'] == 'MOREAD':
                    self.options_dict['GUESS']['GUESS'] = 'HUCKEL'
                print('No scf guess MOs available, switching to HUCKEL.')
            except KeyError:
                pass
        if self.hess:
            if not 'STATPT' in self.options_dict:
                self.options_dict['STATPT'] = OrderedDict()
            self.options_dict['STATPT']['HESS'] = 'READ'
        else:
            # If no hessian, make sure that the guess is not READ
            try:
                del self.options_dict['STATPT']['HESS']
                print('No guess hessian, removing HESS=READ from STATPT')
            except KeyError:
                pass
        del_ecp = True
        if self.ecp:
            for key, value in self.ecp.items():
                if value.split()[1] != 'NONE':
                    del_ecp = False
                    break
        if del_ecp:
            try:
                del self.options_dict['STATPT']['HESS']
            except KeyError:
                pass

    def write_input(self, input_file='input.inp', comment=''):
        """Makes an input file with the given geometry and basis"""
        data = f' $DATA\n{comment}\nC1\n'
        ecp = ' $ECP\n'
        for name, (x, y, z) in self.mol:
            if len(name) > 1:
                name = name[0].upper() + name[1:].lower()
            an = Atom.atomic_number(name)
            atom_basis = self.basis_set[name].print(style='gamess',
                                                    print_name=False)
            data += f'{name} {an}     {x}  {y}  {z}\n{atom_basis}\n'
            if name in self.ecp:
                ecp += self.ecp[name].strip() + '\n'
            else:
                ecp += f'{name}-ECP NONE\n'
        data += ' $END\n'
        ecp += ' $END\n'

        self.update_options()

        input_data = f'{self.write_options_str()}\n{data}\n{ecp}\n{self.vec}\n{self.hess}'
        open(input_file, 'w').write(input_data)
