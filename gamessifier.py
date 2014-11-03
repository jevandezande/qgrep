#!/usr/bin/env python3

import os
from molecule import Molecule
from helper import atomic_number, convert_name
from basis import BasisSet


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
                self.ecp[name] = ''
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
            atom_basis = self.basis_set[name].print(print_name=False)
            data += '{} {}     {}  {}  {}\n{}\n'.format(name, an, x, y, z, atom_basis)
            ecp += self.ecp[name].strip() + '\n'
        data += ' $END\n'
        ecp += ' $END\n'
        input_data = '{}\n{}\n{}'.format(self.other, data, ecp)
        open(input_file, 'w').write(input_data)


if __name__ == "__main__":
    g = Gamessifier()
    g.read_mol()
    g.read_basis()
    g.write_input()
