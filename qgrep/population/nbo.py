"""Source for all nbo relate functions"""
import re
import numpy as np
from itertools import zip_longest
from more_itertools import peekable


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
        ret = 'Idx Atom   Charge    Core    Valence  Rydberg   Total\n'
        line_form = '{:>3} {:<5}' + ' {: >8.5f}' * 5 + '\n'
        for i, (atom, charge) in enumerate(zip(self.atoms, self.charges)):
            ret += line_form.format(i, atom, *charge)
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

class NBO:
    """Natural Bond Orbital class"""

    def __init__(self, file_iter):
        """
        :param file_iter: file to be read from an output file
        """
        self.nbos = self.read(file_iter)

    def __str__(self):
        ret      = 'Index  Order  type  sub  atom1  #  Other info \n'
        nbo_form = '{:>4d}  {:>7.5f}  {:3}   {:>2d}    {:2} {:>3}    {}\n'
        for nbo in self.nbos:
            ret += nbo_form.format(*nbo[:6], nbo[6:])
        return ret

    @staticmethod
    def read(file_iter):
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
        file_iter = peekable(iter(file_iter))
        for line in file_iter:
            if line == '     (Occupancy)   Bond orbital / Coefficients / Hybrids\n':
                break
        try:
            file_iter.peek()
        except StopIteration:
            raise Exception('Could not find NBO section.')

        nbos = []
        while line:
            # Start of a new block for parsing
            if re.search('\s*\d+\. \(', line):
                idx, occup, nbo_type, *other = line.split()
                idx = int(idx[:-1])
                occup = float(occup[1:-1])
                nbo_type = nbo_type.strip('(')

                atom_re = ' ?(\w{1,2})\s+(\d+)'
                hybridicity_regex = '(\w)\s*(\d+\.\d+)\(\s*(\d+\.\d+)'

                if nbo_type in ['BD', 'BD*']:
                    """
   4. (1.99999) BD ( 1) H  1- O  2
               ( 41.34%)   0.6429* H  1 s(100.00%)
                                         1.0000
               ( 58.66%)   0.7659* O  2 s( 12.16%)p 7.22( 87.84%)
                                         0.0000  0.3487  0.0000 -0.0650 -0.9350
"""
                    regex = fr'\( ?(\d+)\){atom_re}-{atom_re}'
                    number, atom1, atom1_n, atom2, atom2_n = re.search(regex, line).groups()

                    regex = fr'\(\s*(\d+\.\d+)%\)\s+(-?\d\.\d+)\*{atom_re}\s+(\w)\(\s*(\d+\.\d+)'
                    # For each atom block within the BD/BD*
                    #while not re.search('\s*\d+\.\s', file_iter.peek()):
                    for i in range(2):
                        line = next(file_iter)
                        percent, val, atom, atom_n, orbital1, percent = re.search(regex, line).groups()
                        assert (atom in [atom1, atom2]) and (atom_n in [atom1_n, atom2_n])

                        hybrids = [(orbital1, 1.0, float(percent))]
                        finder = lambda l: re.findall(hybridicity_regex, l)
                        matches = finder(line) + finder(file_iter.peek())
                        for orbital, hybridicity, percent in matches:
                            hybrids.append((orbital, float(hybridicity), float(percent)))

                        matches = []
                        line = file_iter.peek()
                        while line[:40] != ' '*40:
                            matches += map(float, re.findall('-?\d\.\d+', line))
                            next(file_iter)
                            line = file_iter.peek()

                    nbos.append([idx, occup, nbo_type, int(number), atom1, int(atom1_n), atom2, int(atom2_n), hybrids, matches])

                elif nbo_type in ['CR', 'LP', 'LV', 'RY', 'RY*']:
                    """90. (0.01241) RY*( 1)Fe  1             s(  0.00%)p 1.00(  3.05%)d31.77( 96.89%)"""
                    regex = fr'\( ?(\d+)\){atom_re}\s+(\w)\(\s*(\d+\.\d+)'
                    try:
                        number, atom, atom_n, orbital1, percent = re.search(regex, line).groups()
                        hybrids = [(orbital1, 1.0, float(percent))]
                        finder = lambda l: re.findall(hybridicity_regex, l)
                        matches = finder(line) + finder(file_iter.peek())
                        for orbital, hybridicity, percent in matches:
                            hybrids.append((orbital, float(hybridicity), float(percent)))
                    except Exception as e:
                        raise ValueError from e
                    nbos.append([idx, occup, nbo_type, int(number), atom, int(atom_n), *hybrids])
                else:
                    raise Exception(f'Cannot parse nbo type {nbo_type}')
            line = next(file_iter).strip()

        return nbos

