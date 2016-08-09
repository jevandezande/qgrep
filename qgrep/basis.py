from collections import OrderedDict
import numpy as np

SUPPORTED = ['guassian94', 'gamess', 'bagel']

class Contraction:
    """A contraction of basis functions"""

    def __init__(self, func_type, exps, coeffs, c2=None):
        if not c2:
            c2 = []
        self.func_type = func_type.upper()
        if not self.func_type in 'SPDFGHIKLMN':
            raise SyntaxError("Invalid angular momentum.")

        if len(exps) == 0 or len(exps) != len(coeffs):
            raise SyntaxError(('Need coefficients and exponents of the same'
                              'length, got: \n{}\n{}').format(exps, coeffs))
        Contraction.check_exps(exps)
        Contraction.check_coeffs(coeffs)
        if len(c2) > 0 and len(c2) != len(coeffs):
            raise SyntaxError('Second set of coefficients must have the same'
                              'number as the first set')
        self.c2 = True
        if len(c2) == 0:
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
            raise ValueError("Incorrect size, expected {} elements.".format(
                len(self.values[0])))
        if not value[0] > 0:
            raise ValueError("All exponents must be greater than 0")
        self.values[item] = value

    def __str__(self):
        """Return a string of the contraction"""
        return self.print()

    def __eq__(self, other):
        """Check if the two contractions are the same"""
        return self.func_type == other.func_type and \
            np.isclose(self.values, other.values).all()

    @staticmethod
    def check_exps(exps):
        """Check to make sure that the exponents are valid"""
        for exp in exps:
            if not exp > 0:
                raise ValueError("Exponents must be greater than 0.")

    @staticmethod
    def check_coeffs(coeffs):
        """Check to make sure that the coefficients are valid"""
        pass

    @property
    def exps(self):
        return self.values[:, 0]

    @exps.setter
    def exps(self, values):
        Contraction.check_exps(values)
        self.values[:, 0] = values

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

    def print(self, style='gaussian94', atom=''):
        """Print the contraction to a string"""
        num_coeffs = 1 + int(self.c2)
        form = '{:>17.7f}' + ' {:> 11.7f}' * num_coeffs
        out = '{:<2}    {}\n'.format(self.func_type, len(self))
        if style == 'gaussian94':
            out += '\n'.join([form.format(*group) for group in self.values])
        elif style == 'gamess':
            form = ' {:>2} ' + form
            out += '\n'.join([form.format(i, *group) for i, group in
                              enumerate(self.values, start=1)])
        else:
            raise SyntaxError(
                'Only gaussian94 and gamess are currently supported.')
        return out + '\n'


class Basis:
    """A basis for an atom"""

    def __init__(self, atom='', contractions=None):
        if contractions is None:
            contractions = []
        self.atom = atom
        if not isinstance(contractions, list) or not all(
                map(lambda x: isinstance(x, Contraction), contractions)):
            raise SyntaxError("Expected a list of contractions")
        self.cons = contractions

    def __len__(self):
        """Return the number of contractions"""
        return len(self.cons)

    def __getitem__(self, i):
        """Return the ith contraction"""
        return self.cons[i]

    def __setitem__(self, i, value):
        """Sets the ith contraction"""
        if not isinstance(value, Contraction):
            raise SyntaxError(
                "Expecting a Contraction object, instead got: {}".format(
                    type(value)))
        self.cons[i] = value

    def __delitem__(self, key):
        """Delete the selected key"""
        del self.cons[key]

    def __eq__(self, other):
        """Check if the two basis are equivalent"""
        if not len(self.cons) == len(other.cons):
            return False
        for s, o in zip(self.cons, other.cons):
            if not s == o:
                return False
        return True

    def print(self, style='gaussian94', print_name=True):
        """Print all contractions in the specified format"""
        out = ''
        if style == 'gaussian94':
            if print_name:
                out += '{}    0\n'.format(self.atom)
        elif style == 'gamess':
            if print_name:
                out += '{}\n'.format(self.atom, len(self))
        else:
            raise SyntaxError('Only gaussian94 and gamess currently supported')
        return out + ''.join([c.print(style, self.atom) for c in self.cons])


class BasisSet:
    """A BasisSet, which consists of the basis for multiple atoms"""

    def __init__(self, atoms=OrderedDict()):
        """Atoms is a dictionary of atom:Basis"""
        if isinstance(atoms, OrderedDict):
            BasisSet.check_basis_set(atoms)
            self.atoms = atoms
            self.am = 'spherical'
        else:
            raise SyntaxError("Invalid input basis set, must use an OrderedDict")

    def __getitem__(self, item):
        """Return the basis for the specified atom"""
        return self.atoms[item]

    def __setitem__(self, item, value):
        """Return the basis for the specified atom"""
        if not isinstance(value, Basis):
            raise SyntaxError(
                "Expecting a Basis object, got a: {}".format(Basis))
        self.atoms[item] = value

    def __delitem__(self, key):
        """Delete the specified key"""
        del self.atoms[key]

    def __eq__(self, other):
        """Check if the two basis sets are equal"""
        for atom, basis in self.atoms.items():
            b2 = other[atom]
            if not atom in other or not basis == b2:
                return False
        return True

    def __contains__(self, item):
        """Check if the item (atom) is in atoms"""
        return item in self.atoms

    def __str__(self):
        """Print the basis in gaussian94 style"""
        return self.print(style='gaussian94')

    def __iter__(self):
        for basis in self.atoms.values():
            yield basis

    @staticmethod
    def check_basis_set(atoms):
        """Check a BasisSet"""
        if isinstance(atoms, OrderedDict):
            for atom, basis in atoms.items():
                # Assume that the Basis was made correctly
                if not isinstance(basis, Basis):
                    raise SyntaxError('Expecting a dictionary of atom:Basis.')
        else:
            raise SyntaxError('Expecting a dictionary (of form atom:Basis).')

    def change_basis_set(self, basis_set):
        """Change to a new basis"""
        BasisSet.check_basis_set(basis_set)
        self.atoms = basis_set

    @staticmethod
    def read_basis_set(in_file="basis.gbs", style='gaussian94'):
        """Read a gaussian94 style basis set"""
        # assume spherical
        bs = BasisSet()
        bs.am = 'spherical'
        bs.atoms = OrderedDict()
        num_skip = 0
        if style == 'gaussian94':
            atom_separator = '****'
        elif style == 'gamess':
            num_skip = 1
            atom_separator = '\n\n'
        else:
            raise SyntaxError(
                "Only gaussian94 style basis sets are currently supported.")
        with open(in_file) as f:
            basis_set_str = f.read().strip()
        # Split into atoms
        for chunk in basis_set_str.split(atom_separator):
            if len(chunk) == 0:
                continue
            name, *basis_chunk = chunk.strip().split('\n')
            name = name.split()[0]
            i = 0
            con_list = []
            while i < len(basis_chunk):
                # Split into contractions
                am, num = basis_chunk[i].split()
                num = int(num)
                con = []
                for line in basis_chunk[i + 1:i + num + 1]:
                    con.append([float(x) for x in line.split()[num_skip:]])
                # Makes an empty list if no elements for coeffs2
                exps, coeffs, *coeffs2 = zip(*con)
                if coeffs2:
                    # Remove extra list
                    coeffs2 = coeffs2[0]
                con_list.append(Contraction(am, exps, coeffs, coeffs2))
                i += num + 1
            bs.atoms[name] = Basis(name, con_list)

        return bs

    def print(self, style='gaussian94'):
        """Print the basis to a string"""
        out = ''
        if style == 'bagel':
            out = OrderedDict()
            for atom in self.values:
                for contraction in atom:
                    pass
            out = json.dumps(out)
            pass
        elif style in ['gaussian94', 'gamess']:
            if style == 'gaussian94':
                separator = '****\n'
                out = separator
            elif style == 'gamess':
                separator = '\n'
            # TODO: sort according to periodic table
            out += separator.join(
                [basis.print(style) for basis in self])

            return out + separator
        else:
            raise SyntaxError('Only {} currently supported'.format(', '.join(SUPPORTED)))

    def values(self):
        """Returns a list of list of np.array(exp, coeff, *coeff2)"""
        vals = [[con.values for con in basis] for basis in self]
        return vals
