from collections import OrderedDict
from helper import convert_name, atomic_number
import numpy as np


class Contraction:
    """A contraction of basis functions"""
    def __init__(self, func_type, exps, coeffs, c2=None):
        func_type = func_type.upper()
        if not func_type in 'SPDFGHIKLMN':
            raise SyntaxError("Invalid angular momentum.")
        self.func_type = func_type

        if len(exps) == 0 or len(exps) != len(coeffs):
            raise SyntaxError('Need coefficients and exponents of the same length, got: \n{}\n{}'.format(exps, coeffs))
        Contraction.check_exps(exps)
        Contraction.check_coeffs(coeffs)
        if not c2 is None and len(c2) != len(coeffs):
            raise SyntaxError('Second set of coefficients must have the same number as the first set')
        self.c2 = True
        if c2 is None:
            self.values = np.array(list(zip(exps, coeffs)))
            self.c2 = False
        else:
            self.values = np.array(list(zip(exps, coeffs, c2)))

    def __len__(self):
        return len(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, item, value):
        if len(value) != len(self.values[0]):
            raise SyntaxError("Incorrect size, expected {} elements.".format(len(self.values[0])))
        self.values[item] = value

    @staticmethod
    def check_exps(exps):
        """Check to make sure that the exponents are valid"""
        for exp in exps:
            if not exp > 0:
                raise SyntaxError("Exponents must be greater than 0.")

    @staticmethod
    def check_coeffs(coeffs):
        """Check to make sure that the coefficients are valid"""
        pass

    @property
    def exps(self):
        return self.values[:, 0]

    @exps.setter
    def exps(self, value):
        self.values[:, 0] = value

    @property
    def coeffs(self):
        return self.values[:, 1]

    @coeffs.setter
    def coeffs(self, value):
        self.values[:, 1] = value

    @property
    def coeffs2(self):
        return self.values[:, 2]

    @coeffs2.setter
    def coeffs2(self, value):
        self.values[:, 2] = value

    def print(self, print_format='gaussian94', atom=''):
        """Print the contraction to a string"""
        out = '{:<2}    {}'.format(self.func_type, len(self))
        if print_format == 'gaussian94':
            if self.c2:
                return out + '\n' + '\n'.join(('{:>17.7f}' + ' {:> 11.7f}'*2).format(*trip) for trip in self.values)
            return out + '\n' + '\n'.join('{:>17.7f} {:> 11.7f}'.format(*pair) for pair in self.values)
        elif print_format == 'gamess':
            if self.c2:
                for i, trip in enumerate(self.values, start=1):
                    out += ('\n {:>2} {:>14.7f}' + ' {:> 11.7f}'*2).format(i, *trip)
            else:
                for i, pair in enumerate(self.values, start=1):
                    out += '\n {:>2} {:>14.7f} {:> 11.7f}'.format(i, *pair)
            return out
        else:
            raise SyntaxError('Only gaussian94 and gamess are currently supported.')


class Basis:
    """A basis for an atom"""
    def __init__(self, atom='', funcs=[]):
        self.atom = atom
        self.funcs = funcs

    def __len__(self):
        return len(self.funcs)

    def print(self, print_format='gaussian94'):
        if print_format == 'gaussian94':
            out = '{}    0\n'.format(self.atom)
        elif print_format == 'gamess':
            out = '{}\n'.format(convert_name(self.atom).upper(), len(self))
        else:
            raise SyntaxError('Only gaussian94 and gamess currently supported')
        return out + '\n'.join([c.print(print_format, self.atom) for c in self.funcs])


class BasisSet:
    """A BasisSet, which consists of the basis for multiple atoms"""
    def __init__(self, atoms=OrderedDict):
        """Atoms is a dictionary of atom:Basis"""
        if isinstance(atoms, OrderedDict):
            BasisSet.check_basis_set(atoms)
            self.atoms = atoms
            self.am = 'spherical'
        elif isinstance(atoms, str):
            self.read_basis(atoms)
        else:
            raise SyntaxError("Invalid input basis set")

    @staticmethod
    def check_basis_set(atoms):
        """Check a BasisSet"""
        if isinstance(atoms, dict):
            for atom, basis in atoms.items():
                if not isinstance(basis, Basis):
                    raise SyntaxError('Expecting a dictionary of atom:Basis.')
        else:
            raise SyntaxError('Expecting a dictionary (of form atom:Basis).')

    def change_basis(self, basis):
        """Change to a new basis"""
        BasisSet.check_basis_set(basis)
        self.atoms = basis

    def read_basis(self, in_file, style='gaussian94'):
        """Read a gaussian94 style basis set"""
        if style != 'gaussian94':
            raise NotImplementedError("Only gaussian94 style basis sets are currently supported.")
        lines = open(in_file, 'r').readlines()
        start = []
        self.atoms = OrderedDict()
        for i in range(len(lines)):
            line = lines[i]
            if line.strip() == '****':
                start.append(i)
        self.am = 'spherical'
        for i in range(start[0]):
            line = lines[i].strip()
            if line == '!' or line == '':
                continue
            elif line == 'spherical' or line == 'cartesian':
                self.am = line
            else:
                raise Exception("Invalid angular momentum type.")

        for atom_num in range(len(start[:-1])):
            atom_start = start[atom_num]
            atom, charge = lines[atom_start+1].split()
            self.atoms[atom] = []
            offset = 2
            # while not starting the next atom
            while atom_start + offset < start[atom_num + 1]:
                func, num_primitives, norm = lines[atom_start + offset].split()
                num_primitives = int(num_primitives)
                contraction = [func.upper(), [], []]
                for j in range(num_primitives):
                    exp, coeff = lines[atom_start + offset + j + 1].split()
                    contraction[1].append(float(exp))
                    contraction[2].append(float(coeff))
                self.atoms[atom].append(contraction)

                offset += num_primitives + 1

    def print_basis(self, out_file):
        out = '{}\n****\n'.format(self.am)
        # Ideally would be sorted according to periodic table
        for atom in self.atoms:
            out += atom + '    0\n'
            for func in self.atoms[atom]:
                num_primitives = len(func[1])
                out += '{}   {}   1.00\n'.format(func[0], num_primitives)
                for i in range(num_primitives):
                    exp = func[1][i]
                    coeff = func[2][i]
                    out += '  {:15.8f}    {:15.8f}\n'.format(exp, coeff)
            out += '****\n'
        if out_file is None:
            return out
        if out_file == 'terminal':
            print(out)
        else:
            with open(out_file, 'w') as f:
                f.write(out)

    @property
    def exps(self):
        exps = []
        for atom in self.atoms:
            for contraction in self.atoms[atom]:
                for exp in contraction[1]:
                    exps.append(exp)
        return exps

    def exp_subset(self, subset):
        """"
        Select a subset of basis function exponents based on the angular momentum of the function.
        """
        subset = subset.upper()
        if not isinstance(subset, str):
            raise SyntaxError("Only strings are currently allowed to specify subsets.")
        plus = (subset[-1] == '+')
        if plus:
            subset = subset[:-1]
        for am in subset:
            if not am in self.am_types:
                raise SyntaxError("{} is an invalid angular momentum.".format(am))
        if plus:
            subset += self.am_types[self.am_types.index(subset[-1]) + 1:]
        exps = []
        for atom in self.atoms:
            for contraction in self.atoms[atom]:
                if contraction[0] in subset:
                    for exp in contraction[1]:
                        exps.append(exp)
        return exps

    def set_exps(self, exps):
        """
        Warning!!! Everything must be placed in perfect order. Be careful if changing basis.
        :param exps: a list of exponents ordered by atom, contraction, and function
        """
        if not len(self.exps) == len(exps):
            raise SyntaxError('Incorrect number of exponents. {} given while {} were expected'.format(
                              len(exps), len(self.exps)))
        i = 0
        for atom in self.atoms:
            for contraction in self.atoms[atom]:
                num_exps = len(contraction[1])
                contraction[1] = exps[i:i+num_exps]
                i += num_exps

    def set_exp_subset(self, subset, exps):
        """"
        Set a subset of basis function exponents based on the angular momentum of the function.
        Warning!!! Everything must be placed in perfect order. Be careful if changing basis.
        """
        if not len(self.exp_subset(subset)) == len(exps):
            raise SyntaxError('Incorrect number of exponents. {} given while {} were expected'.format(
                len(exps), len(self.exp_subset(subset))))
        subset = subset.upper()
        plus = (subset[-1] == '+')
        if plus:
            subset = subset[:-1] + self.am_types[self.am_types.index(subset[-2]) + 1:]
        i = 0
        for atom in self.atoms:
            for contraction in self.atoms[atom]:
                if contraction[0] in subset:
                    num_exps = len(contraction[1])
                    contraction[1] = exps[i:i+num_exps]
                    i += num_exps

    def sort(self):
        """
        Sort the primitives in each contraction by exponent in descending order
        """
        for atom in self.atoms:
            for contraction in self.atoms[atom]:
                zipped = zip(contraction[1], contraction[2])
                contraction[1], contraction[2] = zip(*sorted(zipped, reverse=True))