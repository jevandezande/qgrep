"""Source for all nbo relate functions"""
import re
import numpy as np
from itertools import zip_longest


class NAOs:
    """Natural Atomic Orbitals"""
    def __init__(self, lines):
        """
        """
        self.vals = NAOs.read(lines)

    def __len__(self):
        return len(self.vals)

    def __iter__(self):
        for ao_vals in self.vals:
            yield ao_vals

    def __sub__(self, other):
        """
        Difference of two NAO objects
        """
        raise NotImplementedError

    @staticmethod
    def read(lines):
        """ Reads the lines of a NAO output
  NAO Atom No lang   Type(AO)    Occupancy      Energy
 ---------------------------------------------------------
   1    C  1  s      Cor( 1s)     1.99916     -10.15626
   2    C  1  s      Val( 2s)     0.94193      -0.30622
"""
        start = -1
        for i, line in enumerate(lines):
            if line.strip() == 'NAO Atom No lang   Type(AO)    Occupancy      Energy':
                start = i + 2
        if start == -1:
            raise Exception('Cannot find the start of NAO')

        vals = []
        atom = ''
        for line in lines[start:]:
            if not line.strip():
                continue
            try:
                idx, atom, num, orb, orb_type, *shell, occupancy, energy = line.split()
            except ValueError as e:
                break
            if not shell:
                orb_type, shell = orb_type.split('(')
            else:
                shell = shell[0]
                orb_type = orb_type.strip('(')
            shell = shell.strip(')')
            vals.append([atom, int(num), orb, orb_type, shell, float(occupancy), float(energy)])

        return vals


class NPA:
    """Natural Population Analysis class"""

    def __init__(self, atoms=None, charges=None, lines=''):
        """
        :param atoms: a list of atoms
        :param charges: numpy array of charges per atom (charge, core, valence, rydberg, total)
        :param lines: line of an output file to read
        """
        if atoms is None and charges is None and lines:
            self.atoms, self.charges = self.read(lines)
        else:
            self.atoms = atoms
            self.charges = charges

    def __eq__(self, other):
        """
        Uses np.allclose
        """
        return self.atoms == other.atoms and np.allclose(self.charges, other.charges)

    def __iter__(self):
        """
        Iterate over atoms and charges, each time returning an array of a single atom with charges
        """
        for atom, atom_charges in zip(self.atoms, self.charges):
            yield atom, atom_charges

    def __len__(self):
        """
        Number of atoms
        """
        return len(self.atoms)

    def __getitem__(self, index):
        """
        Get the atom and charges corresponding to the index
        """
        return [self.atoms[index]] + self.charges[index]

    def __setitem__(self, index, value):
        """
        Set the atom and charges corresponding to the index
        """
        if len(value) != 6:
            raise SyntaxError('Invalid number of charges')
        self.atoms[index] = value[0]
        self.charges[index] = value[1:]

    def __str__(self):
        """
        Return a string resmbling the NPA output
        """
        ret = 'Atom   Charge    Core    Valence  Rydberg   Total\n'
        line_form = '{:<5}' + ' {: >8.5f}' * 5 + '\n'
        for atom, charge in zip(self.atoms, self.charges):
            ret += line_form.format(atom, *charge)
        return ret

    def __sub__(self, other):
        """
        Subtract two NPA objects of different sizes
        """
        return self._combine(other, '-')

    def __add__(self, other):
        """
        Add two NPA objects
        """
        return self._combine(other, '+')

    def _combine(self, other, form):
        """
        Add or subtract two NPA objects
        """
        if form not in ['+', '-']:
            raise ValueError("form must be '+' or '-'")
        atoms = []
        charges = []
        # Allow combination even if the dimensions don't match
        for (atom1, charges1), (atom2, charges2) in zip_longest(self, other, fillvalue=['', np.zeros(5)]):
            atoms.append('{:>2}{:}{:<2}'.format(atom1, form, atom2))

            if form == '-':
                charges.append(charges1 - charges2)
            else:
                charges.append(charges1 + charges2)

        if form == '-':
            return NPA_Diff(atoms, charges)
        return NPA_Sum(atoms, charges)


    def append(self, atom, *vals):
        """
        Append an atom and charges to the population analysis
        """
        self.atoms.append(atom)
        if not len(vals) == 5:
            raise SyntaxError('Invalid number of charges')
        self.charges = np.array(list(self.charges).append(list(vals)))

    @staticmethod
    def read(lines):
        """Read the natural population analysis from an output file

 Summary of Natural Population Analysis:
                                     Natural Population
             Natural    ---------------------------------------------
  Atom No    Charge        Core      Valence    Rydberg      Total
 --------------------------------------------------------------------
   Fe  1   -0.57877     17.97641     8.54310    0.05926    26.57877
    C  2    0.60637      1.99951     3.34225    0.05187     5.39363
    O  3   -0.42097      1.99976     6.38932    0.03189     8.42097
...
"""

        # Find the NPA Section
        start = -1
        for i, line in enumerate(lines):
            if line == '  Atom No    Charge        Core      Valence    Rydberg      Total\n':
                start = i + 2
                break
        if start == -1:
            raise Exception('Unable to find the start of NPA analysis')

        npa = []
        atoms = []
        # Interpret the NPA
        for line in lines[start:]:
            if line[:50] == " " + "=" * 49:
                break
            atom, num, *others = line.split()
            atoms.append(atom)
            num = int(num)
            charge, core, valence, rydberg, total, *ns = map(float, others)
            npa.append([charge, core, valence, rydberg, total])
        return atoms, np.array(npa)

class NPA_Diff(NPA):
    """
    NPA class without restrictions on population
    Currently exactly the same
    """

class NPA_Sum(NPA):
    """
    NPA class without restrictions on population
    Currently exactly the same
    """

class NBO():
    """Natural Bond Orbital class"""

    def __init__(self, lines):
        """
        :param lines: lines to be read from an output file
        """
        self.nbos = self.read(lines)

    def __str__(self):
        ret = 'Bond #, Bond Order, type, sub bond #, atom1, atom1 #, atom2,' \
              'atom2 #\n'
        nbo_form = ' {:>3d}     {:6.5f}     {:<3s}      {:d}        {:<2s}' \
                   '     {:>3d}       {:<2s}    {:>3d}\n'
        for nbo in self.nbos:
            ret += nbo_form.format(*nbo)
        return ret

    @staticmethod
    def read(lines):
        """
        Read the Natural Bond Orbital Analysis

   1. (1.92050) BD ( 1)Fe  1- C  2
               ( 32.17%)   0.5672*Fe  1 s( 33.10%)p 0.00(  0.02%)d 2.02( 66.88%)
                                                  f 0.00(  0.00%)
                                         0.0000  0.0000 -0.0044  0.5753  0.0022
    ...
  36. (2.00000) CR ( 1)Fe  1             s(100.00%)
                                         1.0000 -0.0000  0.0000 -0.0000  0.0000
    ...
  72. (1.79971) LP ( 1)Fe  1             s(  0.00%)p 0.00(  0.00%)d 1.00(100.00%)
                                                  f 0.00(  0.00%)
                                         0.0000  0.0000 -0.0000  0.0001 -0.0001
    ...
  90. (0.01241) RY*( 1)Fe  1             s(  0.00%)p 1.00(  3.05%)d31.77( 96.89%)
                                                  f 0.02(  0.06%)
                                         0.0000  0.0000  0.0000  0.0000  0.0005
    ...
 618. (0.67669) BD*( 1)Fe  1- C  2
               ( 67.83%)   0.8236*Fe  1 s( 33.10%)p 0.00(  0.02%)d 2.02( 66.88%)
                                                  f 0.00(  0.00%)
    ...
        """
        for i, line in enumerate(lines):
            if line == '     (Occupancy)   Bond orbital/ Coefficients/ Hybrids\n':
                start = i + 2
                break

        atom1 = 'C'
        num1 = 26
        atom2 = 'O'
        num2 = 27
        types = '(BD |BD\*|CR |LP |RY |RY\*)'

        #atom_label_1 = atom1.rjust(2) + str(num1).rjust(3)
        atom_label = ' ?(\w+) +(\d+)'
        #atom_label_2 = atom2.rjust(2) + str(num2).rjust(3)

        regex = r'(\d+)\. \((\d\.\d*)\) {}\( ?(\d+)\){}-{}'

        regex = regex.format(types, atom_label, atom_label)

        # TODO: Actually use starting coordinates
        out_string = open('output.dat').read()
        results = re.findall(regex, out_string)

        nbos = []
        for nbo in results:
            bond_num, b_order, b_type, b_sub, a1, a1_n, a2, a2_n = nbo
            nbos.append([int(bond_num), float(b_order), str(b_type), int(b_sub),
                         str(a1), int(a1_n), str(a2), int(a2_n)])

        return nbos

