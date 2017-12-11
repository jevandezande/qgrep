import json
import numpy as np

from collections import Iterable, OrderedDict

SUPPORTED = ['gaussian94', 'gamess', 'bagel', 'cfour', 'molpro']
AM = 'SPDFGHIKLMN'

class BasisFunction:
    """A primitive or a contraction of primitives"""

    def __init__(self, func_type, exps, coeffs):
        exps, coeffs = np.array(exps), np.array(coeffs)
        self.num_coeffs = 1 if len(coeffs.shape) == 1 else coeffs.shape[0]
        self.func_type = func_type.upper()
        if not self.func_type in 'SPDFGHIKLMN':
            raise SyntaxError("Invalid angular momentum.")
        if self.func_type == 'SP' and coeffs.shape[0] != 2:
            raise SyntaxError('Expected exactly two sets of coefficients for combined BasisFunction.')

        if len(exps) == 0 or len(coeffs) == 0:
            raise SyntaxError('Cannot create an empty BasisFunction')
        elif len(exps) != coeffs.shape[-1]:
            raise SyntaxError(('Need coefficients and exponents of the same'
                              'length, got: \n{}\n{}').format(exps, coeffs))

        BasisFunction.check_exps(exps)
        BasisFunction.check_coeffs(coeffs)

        if self.num_coeffs == 1:
            coeffs = coeffs[np.newaxis, :]
        self.values = np.append(exps[:, np.newaxis], coeffs.T, axis=1)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, item):
        return self.values[item]

    def __setitem__(self, item, value):
        if len(value) != len(self.values[0]):
            raise ValueError("Incorrect size, expected {} elements.".format(len(self.values[0])))
        if not value[0] > 0:
            raise ValueError("All exponents must be greater than 0")
        self.values[item] = value

    def __repr__(self):
        """Make a nice representation of the BasisFunction"""
        mult_str = '' if self.num_coeffs == 1 else 'x' + str(self.coeffs.shape[1])
        return "<BasisFunction {:s} {:d}{}>".format(self.func_type, len(self.exps), mult_str)

    def __str__(self):
        """Return a string of the BasisFunction"""
        return self.print()

    def __eq__(self, other):
        """Check if the two BasisFunctions are the same"""
        # TODO: Change this to exact equality and make inexact a separate function?
        return self.func_type == other.func_type and \
            np.isclose(self.values, other.values).all()

    def __hash__(self):
        """
        Hash the BasisFunction
        WARNING: Hashing floats only checks for exact equality
        """
        return hash((self.func_type, self.values.data.tobytes()))

    @staticmethod
    def check_exps(exps):
        """Check to make sure that the exponents are valid"""
        for exp in exps:
            if not exp > 0:
                raise ValueError("Exponents must be greater than 0.")

    @staticmethod
    def check_coeffs(coeffs):
        """Check to make sure that the coefficients are valid"""
        if len(coeffs.shape) not in [1, 2]:
            raise SyntaxError('Wrong dimension of coeffs array.')

    @property
    def exps(self):
        return self.values[:, 0]

    @exps.setter
    def exps(self, values):
        BasisFunction.check_exps(values)
        self.values[:, 0] = values

    @property
    def coeffs(self):
        """Returns a np.array of values of shape (n_exps) or (n_exps, n_coeffs)"""
        return self.values[:, 1:]

    @coeffs.setter
    def coeffs(self, cs):
        BasisFunction.check_coeffs(cs)
        if self.coeffs.shape != cs.shape:
            raise SyntaxError('Incorrect number of coeffs: expected {}, got {}'.format(self.coeffs.shape, cs.shape))
        self.values[:, 1:] = cs

    @property
    def am(self):
        if self.func_type != 'L' and self.func_type != 'SP':
            return AM.index(self.func_type)
        else:
            return -1

    def decontracted(self):
        """
        Creates individual BasisFunctions with only a single Gaussian
        :yield: BasisFunctions with a single element
        """
        func_type, exps, coeffs = self.func_type, self.exps, self.coeffs

        if func_type == 'SP':
            yield from BasisFunction('S', np.array(exps), coeffs[:, 0]).decontracted()
            yield from BasisFunction('P', np.array(exps), coeffs[:, 1]).decontracted()
        else:
            # Note: Only needs exp as all different coeffs will produce same BasisFunction
            for exp in exps:
                yield BasisFunction(func_type, [exp], [1])

    def print(self, style='gaussian94', atom=''):
        """Print the BasisFunction to a string"""
        num_coeffs = self.num_coeffs
        out = ''
        form = '{:>17.7f}' + ' {:> 11.7f}' * num_coeffs
        if style == 'gaussian94':
            out += '{:<2}    {}\n'.format(self.func_type, len(self))
            for group in self.values:
                out += form.format(*group) + '\n'
        elif style == 'gamess':
            out += '{:<2}    {}\n'.format(self.func_type, len(self))
            form = ' {:>2} ' + form
            for i, group in enumerate(self.values, start=1):
                out += form.format(i, *group) + '\n'
        elif style == 'bagel':
            vals_form = ','.join(['{:>15.8f}']*len(self))
            c_form = ', '.join(['[' + vals_form  + ']']*num_coeffs)
            bagel_form = '{{\n    "angular" : "{:s}",\n       "prim" :  [' + vals_form + '],\n       "cont" : [' + c_form + ']\n}}\n'
            out += bagel_form.format(self.func_type.lower(), *self.exps, *self.coeffs.flatten())
        elif style == 'cfour':
            # Print exponents
            for i, exp in enumerate(self.exps):
                if not i % 6:
                    out += '\n'
                out += ' {:>12.7g}'.format(exp)
            out += '\n\n'
            # Print coefficients
            for c_line in self.coeffs:
                out += (' {:>12.7g}'*self.num_coeffs).format(*c_line) + '\n'
        elif style == 'molpro':
            # TODO: print basis function in Molpro format
        else:
            raise SyntaxError('Only [{}] currently supported'.format(', '.join(SUPPORTED)))
        return out


class Basis:
    """A basis for an atom"""

    def __init__(self, atom='', basis_functions=None, name=''):
        if basis_functions is None:
            basis_functions = []
        self.atom = atom
        if not isinstance(basis_functions, list) or not all(
                map(lambda x: isinstance(x, BasisFunction), basis_functions)):
            raise SyntaxError("Expected a list of BasisFunctions")
        self.basis_functions = basis_functions
        self.name = name

    def __len__(self):
        """Return the number of BasisFunctions"""
        return len(self.basis_functions)

    def __getitem__(self, i):
        """Return the ith BasisFunction"""
        return self.basis_functions[i]

    def __setitem__(self, i, value):
        """Sets the ith BasisFunction"""
        if not isinstance(value, BasisFunction):
            raise SyntaxError(
                "Expecting a BasisFunction object, instead got: {}".format(
                    type(value)))
        self.basis_functions[i] = value

    def __delitem__(self, key):
        """Delete the selected key"""
        del self.basis_functions[key]

    def __eq__(self, other):
        """Check if the two basis are equivalent"""
        if not len(self.basis_functions) == len(other.basis_functions):
            return False
        for s, o in zip(self.basis_functions, other.basis_functions):
            if not s == o:
                return False
        return True

    def __iter__(self):
        for c in self.basis_functions:
            yield c

    def __repr__(self):
        return "<Basis {:s} {:d}>".format(self.atom, len(self.basis_functions))

    def __str__(self):
        return self.print()

    def decontracted(self):
        """
        Generates a decontracted Basis. See BasisFunction.decontracted()
        :return: Basis with all BasisFunctions decontracted (duplicates removed)
        """
        basis_functions = []
        basis_functions_set = set()
        for con in self.basis_functions:
            for f in con.decontracted():
                if f not in basis_functions_set:
                    basis_functions_set.add(f)
                    basis_functions.append(f)
        return Basis(self.atom, basis_functions, self.name)

    def print(self, style='gaussian94', print_name=True):
        """Print all BasisFunctions in the specified format"""
        out = ''
        if style not in SUPPORTED:
            raise SyntaxError('Only [{}] currently supported'.format(', '.join(SUPPORTED)))
        if print_name:
            if style == 'gaussian94':
                out += '{}    0\n'.format(self.atom)
            elif style == 'gamess':
                out += '{}\n'.format(self.atom, len(self))
            elif style == 'bagel':
                out += '"{:s}" : ['.format(self.atom)
            elif style == 'cfour':
                out += '{:s}:{:s}\nComment Line\n\n'.format(self.atom, self.name)
            elif style == 'molpro':
                out += 'basis={\n!\n! {:s}\n! {:s}\n'.format(self.name, self.name)
            else:
                raise SyntaxError('Only [{}] currently supported'.format(', '.join(SUPPORTED)))
        if style == 'bagel':
            out += ',\n'.join([c.print(style, self.atom) for c in self]) + ']'
        elif style == 'cfour':
            out += ' {:>2d}\n'.format(len(self))
            # Find values for header
            vals = []
            for bf in self:
                shape = bf.coeffs.shape
                con_length = shape[1] if len(shape) == 2 else 1
                exp_length = shape[0]
                vals.append([bf.am, con_length, exp_length])
            vals = np.array(vals).T
            # Make header
            for xs in vals:
                out += (' {:>2d}'*len(vals.T)).format(*xs) + '\n'
            # Print basis functions
            for bf in self:
                out += bf.print(style)
        elif style == 'molpro':
            # TODO: Print Basis in Molpro format
        else:
            out += ''.join([c.print(style, self.atom) for c in self])
        return out


class BasisSet:
    """A BasisSet, which consists of the basis for multiple atoms"""

    def __init__(self, atoms=None, name=''):
        """Atoms is a dictionary of atom:Basis"""
        self.am = 'spherical'
        self.name = name
        if atoms is None:
            self.atoms = OrderedDict()
        elif isinstance(atoms, OrderedDict):
            BasisSet.check_basis_set(atoms)
            self.atoms = atoms
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

    def __repr__(self):
        return '<BasisSet {:s}>'.format(self.name)

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
    def read(in_file="basis.gbs", style='gaussian94', debug=False):
        """Read a gaussian94 style basis set"""
        # assume spherical
        basis_name = in_file.split('/')[-1].split('.')[0]
        bs = BasisSet(name=basis_name)
        num_skip = 0

        if style == 'cfour':
            with open(in_file) as f:
                lines = f.readlines()
            block_starts = [i for i, line in enumerate(lines) if ':' in line]
            for start in block_starts:
                # Ignore comments
                if lines[start][0] == '!':
                    continue
                """ Read Numbering section, i.e.
                nsections
                    am          am              am          am
                ncontractions ncontractions ncontractions ncontractions
                    nexp        nexp            nexp        nexp
                """
                try:
                    atom, basis_name = lines[start].strip().split(':')
                    num_parts = lines[start + 3].strip()
                    ams = lines[start + 4].split()
                    con_lengths = lines[start + 5].split()
                    exp_lengths = lines[start + 6].split()
                    j = start + 8
                    bfs = []
                    for am, con_length, exp_length in zip(ams, con_lengths, exp_lengths):
                        am, con_length, exp_length = int(am), int(con_length), int(exp_length)
                        # Read exponents, 5 per line in official format
                        exp_end = j + (exp_length - 1)//5
                        exps = []
                        good_exp_num = True
                        for k, line in enumerate(lines[j:exp_end + 1], start=j):
                            if not line.strip():
                                good_exp_num = False
                                exp_end = k - 1
                                break

                            xs = line.split()
                            exps += list(map(float, xs))
                            if len(xs) > 5:
                                good_exp_num = False

                        if not good_exp_num:
                            print('Incorrectly formatted GENBAS exponent section: proceed with caution (section starting on line {})'.format(start))

                        if len(exps) != exp_length:
                            raise Exception('The number of exponents in the header ({}) does not match the number of exponents read ({}).'.format(exp_length, len(exps)))

                        con_start = exp_end + 2
                        con_end = con_start + exp_length
                        coeffs = []
                        if con_length > 6:
                            print('CFour format does not allow more than 6 contracted coefficients: proceed with caution.')

                        for line in lines[con_start:con_end]:
                            coeffs.append([float(c) for c in line.split()])
                        coeffs = np.array(coeffs).T
                        if len(coeffs) != con_length:
                            print(coeffs)
                            if len(coeffs) > con_length and not coeffs[con_length:].any():
                                coeffs = coeffs[:con_length]
                            else:
                                if debug:
                                    print('Line {} -- {}:{} section -- {},{},{}'.format(start, atom, basis_name, am, con_length, exp_length))
                                raise Exception('The number of contractions in the header ({}) does not match the number of contractions read ({}).'.format(con_length, len(coeffs)))
                        if len(coeffs.T) != exp_length:
                            if debug:
                                print('Line {} -- {}:{} section -- {},{},{}'.format(start, atom, basis_name, am, con_length, exp_length))
                            raise Exception('The number of coefficients in the header ({}) does not match the number of exponents read ({}).'.format(exp_length, len(coeffs.T)))
                        if con_length > 1:
                            bfs += [BasisFunction(AM[am], exps, c) for c in coeffs]
                        else:
                            bfs.append(BasisFunction(AM[am], exps, coeffs[0]))
                        j = con_end + 1
                except:
                    if debug:
                        print('Failed to parse section starting on line {}.'.format(start))
                    raise
                bs.atoms[atom] = Basis(atom, bfs, basis_name)

        elif style == 'bagel':
            with open(in_file) as f:
                in_file_dict = json.load(f)
            for atom, basis_list in in_file_dict.items():
                bfs = []
                for c in basis_list:
                    am, coeffs, exps = c['angular'], c['cont'], c['prim']
                    coeffs = np.squeeze(np.array(coeffs))
                    if len(coeffs.shape) == 1:
                        bfs.append(BasisFunction(am, exps, coeffs))
                    else:
                        bfs += [BasisFunction(am, exps, cs) for cs in coeffs]
                bs.atoms[atom] = Basis(atom, bfs, basis_name)

        elif style == 'molpro':
            with open(in_file) as f:
                lines = [line.strip() for line in f.readlines() if len(line.strip())]
            atom_old = ''
            for line in lines:
                # Ignore start and end
                if line[:7] == 'basis={' or line[0] == '}':
                    continue
                # Comments start with an '!'
                if line[0] == '!':
                    continue
                # Exponent line
                if line[0].upper() in AM:
                    am, atom, *exps = line.split(',')
                    am, atom = am.strip(), atom.strip()
                    if atom != atom_old:
                        if atom_old != '':
                            bs[atom_old] = Basis(atom_old, bfs)
                        atom_old = atom
                        bfs = []
                    exps = [*map(float, exps)]
                # Coefficient line
                elif line[0] == 'c':
                    c, c_range, *coeffs = line.split(',')
                    coeffs = [*map(float, coeffs)]
                    c_start, c_end = map(int, c_range.split('.'))
                    c_exps = exps[c_start - 1:c_end]
                    bfs.append(BasisFunction(am, c_exps, coeffs))
                else:
                    raise SyntaxError('Not sure what to with line:\n{}'.format(line))
                bs[atom] = Basis(atom, bfs)
        else:
            if style == 'gaussian94':
                atom_separator = '****'
            elif style == 'gamess':
                num_skip = 1
                atom_separator = '\n\n'
            else:
                raise SyntaxError('Only [{}] currently supported'.format(', '.join(SUPPORTED)))
            with open(in_file) as f:
                basis_set_str = f.read().strip()
            # Split into atoms
            for chunk in basis_set_str.split(atom_separator):
                if len(chunk) == 0:
                    continue
                try:
                    atom, *basis_chunk = chunk.strip().split('\n')
                    atom = atom.split()[0]
                    i = 0
                    con_list = []
                    while i < len(basis_chunk):
                        # Split into basis functions
                        am, num = basis_chunk[i].split()[:2]
                        num = int(num)
                        con = []
                        for line in basis_chunk[i + 1:i + num + 1]:
                            con.append([float(x) for x in line.split()[num_skip:]])
                        exps, *coeffs = zip(*con)
                        # Remove extra list
                        coeffs = np.array(coeffs[0])
                        con_list.append(BasisFunction(am, exps, coeffs))
                        i += num + 1
                    bs.atoms[atom] = Basis(atom, con_list)
                except:
                    if debug:
                        print('Failed to parse section starting with\n{}'.format('\n'.join(chunk.splitlines()[:5])))
                    raise

        return bs

    def decontracted(self):
        """
        Generates a decontracted BasisSet. See BasisFunction.decontracted()
        :return: BasisSet with all BasisFunctions decontracted (duplicates removed)
        """
        atoms = OrderedDict()
        for atom, basis in self.atoms.items():
            atoms[atom] = basis.decontracted()

        return BasisSet(atoms, self.name)

    def print(self, style='gaussian94'):
        """Print the Basis to a string"""
        out = ''
        if style == 'bagel':
            out += ',\n\n'.join([basis.print('bagel').replace('\n', '\n    ') for basis in self])
            return '{\n' + out + '\n}'

        elif style == 'molpro':
            pass
            # TODO: Print decontracted Molpro basis set
        elif style in ['gaussian94', 'gamess', 'cfour']:
            if style == 'gaussian94':
                separator = '****\n'
                out = separator
            elif style in ['gamess', 'cfour']:
                separator = '\n'
            # TODO: sort according to periodic table
            out += separator.join(
                [basis.print(style) for basis in self])
            return out + separator
        else:
            raise SyntaxError('Only [{}] currently supported'.format(', '.join(SUPPORTED)))

    def values(self):
        """Returns a list of list of np.array(exp, coeff)"""
        vals = [[con.values for con in basis] for basis in self]
        return vals
