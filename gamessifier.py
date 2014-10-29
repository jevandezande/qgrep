#!/usr/bin/env python3

import os
from molecule import Molecule
from helper import atomic_number, convert_name


class Gamessifier():
    """Class for making Gamess input files"""
    def __init__(self):
        self.mol = None
        self.basis = None
        self.other = None
        pass

    def read_mol(self, geom_file='geom.xyz'):
        """Reads a geometry file and generates a molecule"""
        self.mol = Molecule()
        self.mol.read_xyz(geom_file)

    def read_basis(self, basis_file='basis.gbs'):
        """Reads a basis file and makes a dictionary with the form atom:basis_functions"""
        if os.path.isfile(basis_file):
            raw_basis = open('basis.gbs', 'r').read()
        else:
            raise IOError('Cannot read basis')

        self.basis = {}
        for atom in raw_basis.split('\n\n'):
            atom_name = atom.split('\n')[0].strip()
            self.basis[atom_name] = '    ' + '\n    '.join(atom.split('\n')[1:])

    def read_other(self, other_file):
        """Reads a file that will be prepended to the input file"""
        with open(other_file, 'r') as f:
            self.other = f.read()

    def write_input(self, input_file='input.inp', comment=''):
        """Makes an input file with the given geometry and basis"""
        data = ''
        for i in range(len(self.mol)):
            name, x, y, z = self.mol[i]
            an = atomic_number(name)
            atom_basis = self.basis[convert_name(an).upper()].strip()
            data += '{} {}     {}  {}  {}\n{}\n\n'.format(name, an, x, y, z, atom_basis)

        input_data = '{}\n$DATA\n{}\nC1\n{}\n $END\n'.format(self.other, comment, data)
        open(input_file, 'w').write(input_data)


if __name__ == "__main__":
    g = Gamessifier()
    g.read_mol()
    g.read_basis()
    g.write_input()
