"""Source for all Löwdin orbital analysis related functions"""
import re
import numpy as np

from re import search
from copy import deepcopy

am_types = 'spdfghi'


class OrbitalPopulation:
    """Löwdin Orbital Population class (OP for short)"""

    def __init__(self, file_name='', orb_list=None, method='lowdin'):
        if file_name:
            self.orb_list = self.read(file_name)
        elif orb_list is not None:
            self.orb_list = orb_list
        else:
            self.orb_list = []

    def __eq__(self, other):
        return self.orb_list == other.orb_list

    def __iter__(self):
        for orb in self.orb_list:
            yield orb

    def __len__(self):
        return len(self.orb_list)

    def __getitem__(self, index):
        return self.orb_list[index]

    def __setitem__(self, index, value):
        if not isinstance(value, Orbital):
            raise SyntaxError(f'Must be an Orbital, got: {type(value)}')
        self.orb_list[index] = value

    def __str__(self):
        return '\n\n'.join([f'{orb}' for orb in self.orb_list])

    def __sub__(self, other):
        # TODO: Fix MOrbital indexing problem
        if len(self) != len(other):
            Warning(f'Differing number of orbitals ({len(self)} != {len(other)}), '
                     'output will be truncated')

        min_len = min(len(self), len(other))
        orb_list = [s - o for s, o in zip(self[:min_len], other[:min_len][:min_len])]

        return OrbitalPopulation(orb_list=orb_list)

    def csv(self):
        return '\n\n'.join([orb.csv() for orb in self.orb_list])

    def write(self, file_name, format='str'):
        """
        Write to a file
        """
        if format == 'str':
            out = f'{self}'
        elif format == 'csv':
            out = self.csv()
        elif format == 'latex':
            out = '\n\n'.join([orb.latex() for orb in self.orb_list])
        else:
            raise SyntaxError(f'Invalid write format: {format}')

        if file_name == 'stdout':
            print(out)
        else:
            with open(file_name, 'w') as f:
                f.write(out)

    def sorted(self, key='contribution'):
        """
        Generates a sorted ROP
        """
        if key == 'index':
            sort_key = lambda x: x.index
        elif key == 'atom':
            sort_key = lambda x: x.atom
        elif key == 'ao':
            sort_key = lambda x: x.ao
        elif key == 'contribution':
            sort_key = lambda x: x.val
        elif key == 'spin':
            sort_key = lambda x: x.spin
        else:
            raise SyntaxError(f'Invalid key given to sorted: {key}')

        orb_list = []
        for mo in self.orb_list:
            contribs = sorted(mo.contributions, key=sort_key, reverse=True)
            orb_list.append(MOrbital(mo.index, mo.spin, mo.energy, mo.occupation, contribs))

        return OrbitalPopulation(orb_list=orb_list)

    @property
    def homo(self):
        """
        Returns the index of the HOMO
        Does not work for UHF (the HOMO is not well defined)

        WARNING: 0-indexed
        """
        for i, orb in enumerate(self):
            if orb.occupation < 2:
                return i - 1

        return None

    @property
    def lumo(self):
        """
        Returns the index of the LUMO

        WARNING: 0-indexed
        """
        for i, orb in enumerate(self):
            if orb.occupation == 0:
                return i

        return None

    @property
    def somo(self):
        """
        Returns the indices of the SOMO's

        WARNING: 0-indexed
        """
        somos = []
        for i, orb in enumerate(self):
            if orb.occupation == 1:
                somos.append(i)

        return somos

    def append(self, orbital):
        """
        Append another orbital
        """
        if not isinstance(orbital, MOrbital):
            raise SyntaxError(f'You may only append Orbitals, got: type{orbital}')
        self.orb_list.append(orbital)

    def atom_contract(self):
        """
        Contracts all atom AO_Contributions together (i.e. adds)
        """
        return OrbitalPopulation(orb_list=[orb.atom_contract() for orb in self])

    def am_contract(self):
        """
        Contracts all AO_Contributions of the same am together (i.e. adds)
        """
        return OrbitalPopulation(orb_list=[orb.am_contract() for orb in self])

    def crop(self, max_num=5, min_num=2, cutoff=5):
        """
        Make an ROP that removes the smallest contributors
        """
        orb_list = []
        for mo in self.orb_list:
            contribs = []
            for contrib in sorted(mo.contributions, key=lambda x: x.val, reverse=True):
                if contrib.val < cutoff and len(contribs) >= min_num:
                    break

                contribs.append(contrib)

                if len(contribs) == max_num:
                    break
            orb_list.append(MOrbital(mo.index, mo.spin, mo.energy, mo.occupation, contribs))

        return OrbitalPopulation(orb_list=orb_list)

    def range(self, low, high):
        """
        Make an OP with a restricted range of orbitals
        """
        return OrbitalPopulation(orb_list=self.orb_list[low:high])

    @staticmethod
    def read(file_name, method='lowdin'):
        """Read the orbital populations"""
        if file_name.split('.')[-1] == 'csv':
            return OrbitalPopulation._read_csv(file_name, method=method)
        else:
            return OrbitalPopulation._read_orca(file_name, method=method)

    @staticmethod
    def _read_orca(file_name, method='lowdin'):
        """Löwdin
------------------------------------------
LOEWDIN REDUCED ORBITAL POPULATIONS PER MO
-------------------------------------------
THRESHOLD FOR PRINTING IS 0.1%
SPIN UP
                      0         1         2         3         4         5
                 -482.78209 -235.47558 -62.42906 -56.24347 -56.24238 -56.24235
                   1.00000   1.00000   1.00000   1.00000   1.00000   1.00000
                  --------  --------  --------  --------  --------  --------
 0 Mn s               0.0     100.0       0.0       0.0       0.0       0.0
25 Br s             100.0       0.0     100.0       0.0       0.0       0.0
25 Br pz              0.0       0.0       0.0       0.0     100.0       0.0
25 Br px              0.0       0.0       0.0       1.5       0.0      98.5
25 Br py              0.0       0.0       0.0      98.5       0.0       1.5

...
Three blank lines
"""
        orb_list = []
        spin = None

        lowdin_re = r'''LOEWDIN REDUCED ORBITAL POPULATIONS PER MO.*?\n\n\n'''
        if method == 'lowdin':
            orb_pop_re = lowdin_re
        else:
            raise NotImplementedError('Only Löwdin Reduced Orbital Population Analysis is implemented')

        with open(file_name) as f:
            output = f.read()
        matches = re.findall(orb_pop_re, output, re.MULTILINE + re.DOTALL)

        first = True
        if matches:
            match = matches[-1].strip()

            blocks = match.split('\n\n')
            for block in blocks:
                lines = block.splitlines()

                # Remove excess from the first block
                if first:
                    lines = lines[3:]
                    first = False
                # If open shell, an extra line is printed
                if lines[0] == 'SPIN UP':
                    spin = 1
                    lines = lines[1:]
                elif lines[0] == 'SPIN DOWN':
                    spin = -1
                    lines = lines[1:]

                # Parse out the header
                indexes = map(int, lines[0].split())
                orb_es = map(float, lines[1].split())
                occs = map(float, lines[2].split())

                # Generate orbitals (occupations added in next section)
                orbs = [MOrbital(idx, spin, orb_e, occ) for idx, orb_e, occ in zip(indexes, orb_es, occs)]

                # Parse out the orbital contributions
                for line in lines[4:]:
                    index, atom, ao, *vals = line.split()
                    index = int(index)
                    vals = map(float, vals)
                    for i, val in enumerate(vals):
                        # If there is occupation, this deletes all the appearances of 0.0
                        # Due to rounding, the occupations will not add up to 100
                        if val > 0:
                            orbs[i].contributions.append(AO_Contrib(index, atom, ao, val, spin))

                orb_list += orbs
        else:
            raise Exception('Unable to find the start of Reduced Orbital Population analysis')
        return orb_list

    @staticmethod
    def _read_csv(file_name, method='lowdin'):
        """Read the CSV output by the OrbitalPopulation class"""
        with open(file_name) as f:
            csv = f.read()
        orb_list = []
        for block in csv.split('\n\n'):
            lines = block.strip().splitlines()
            mo_index, spin, orb_e, occ = lines[0].split(',')
            mo_index, orb_e, occ = int(mo_index), float(orb_e), round(float(occ))
            aocs = []
            for line in lines[1:]:
                index, atom, ao, val = line.split(',')
                aocs.append(AO_Contrib(int(index), atom.strip(), ao.strip(), float(val), spin))
            orb_list.append(MOrbital(mo_index, spin, orb_e, occ, aocs))

        return orb_list


class MOrbital:
    """
    Simple orbital class that holds the contributions from AOs as well as a
    little more necessary information
    """
    def __init__(self, index=0, spin=None, energy=0, occupation=0, contributions=None):
        self.index = index
        self.spin = spin
        self.energy = energy
        self.occupation = occupation
        self.contributions = contributions if contributions is not None else []

    def __eq__(self, other):
        """
        Checks if all values are equal
        """
        if self.index == other.index \
                and np.isclose(self.energy, other.energy) \
                and np.isclose(self.occupation, other.occupation) \
                and len(self) == len(other):
            for s, o in zip(self.contributions, other.contributions):
                if not s == o:
                    return False
            return True
        return False

    def __len__(self):
        return len(self.contributions)

    def __repr__(self):
        return f'<MO {self.index}{self.gspin} {self.energy: >8.5f} [{self.occupation}]>'

    def __str__(self):
        contrib_str = '\n'.join([f'{contrib}' for contrib in self.contributions])
        return f'{self.index: >2d}{self.gspin} {self.energy: >8.5f} {self.occupation:>3.2f}\n{contrib_str}'

    def __sub__(self, other):
        if len(self) != len(other):
            Warning('The MOrbitals are of different lengths.')
            # raise ValueError('The MOrbitals are of different lengths.')
        min_len = min(len(self), len(other))

        index = self.index if self.index == other.index else 0
        energy = self.energy - other.energy
        occupation = self.occupation - other.occupation
        contributions = []
        for s, o in zip(self.contributions[:min_len], other.contributions[:min_len]):
            contributions.append(s - o)

        # Only appends from one list (the other is maxed out and returns an empty list)
        contributions += self.contributions[min_len:] + other.contributions[min_len:]

        spin = self.spin if self.spin == other.spin else None
        return MOrbital(index, spin, energy, occupation, contributions)

    @property
    def gspin(self):
        if self.spin == 1:
            return 'α'
        elif self.spin == -1:
            return 'β'
        return ''

    def csv(self):
        ao_contrib_str = '\n'.join([ao_contrib.csv() for ao_contrib in self.contributions])
        return f'{self.index: >2d}, {self.gspin}, {self.energy: > 7.5f}, {self.occupation:>3.2f}\n{ao_contrib_str}'

    def latex(self):
        """
        Make into a latex tabular
        """
        aoc_latex = f'{self.index:>2d} {self.energy: > 6.4f} {self.occupation:>3.2f}\n'
        aoc_latex += '\\begin{tabular}{r l r r}\n Index & Atom & AO  &  val \\\\ \\hline\n'
        for aoc in self.contributions:
            aoc_latex += f'{aoc.index:>6d} & {aoc.atom:<4s} & {aoc.ao:<3s} & {aoc.val:>4.1f} \\\\\n'
        aoc_latex += '\\end{tabular}'

        return aoc_latex

    def atom_contract(self):
        """
        Contracts all atom AO_Contributions together (i.e. adds)
        """
        # Dictionary of contracted ao_contributions
        atoms = {}
        for aoc in self.contributions:
            index, val = aoc.index, aoc.val
            if index in atoms:
                atoms[index].val += val
            else:
                aoc = deepcopy(aoc)
                aoc.ao = ''
                atoms[index] = aoc

        # Sort by atom index
        contribs = sorted(atoms.values(), key=lambda x: x.index)
        return MOrbital(self.index, None, self.energy, self.occupation, contribs)

    def am_contract(self):
        """
        Contracts all AO_Contributions of the same am together (i.e. adds)
        """
        # Dictionary of contracted ao_contributions
        atoms = {}
        for aoc in self.contributions:
            # First non-number corresponds to the am
            index, am, val = aoc.index, aoc.ao[0], aoc.val
            if (index, am) in atoms:
                atoms[(index, am)].val += val
            else:
                aoc = deepcopy(aoc)
                aoc.ao = am
                atoms[(index, am)] = aoc

        # Sort by atom index and then am_type
        key = lambda x: (x.index, am_types.index(x.ao[0]))
        contribs = sorted(atoms.values(), key=key)
        return MOrbital(self.index, None, self.energy, self.occupation, contribs)

    def atom_sum(self, atom):
        """
        Sum over all the contributions from an atom
        """
        val = 0
        if isinstance(atom, str):
            for ao_contrib in self.contributions:
                if ao_contrib.atom == atom:
                    val += ao_contrib.val
        elif isinstance(atom, int):
            for ao_contrib in self.contributions:
                if ao_contrib.index == atom:
                    val += ao_contrib.val
        else:
            raise SyntaxError(f'Atom specifier must be either an int or str, got: {type(atom)}')

        return val

    def orbital_type_sum(self, atom, am_type):
        """
        Sum over all the contributions from am_type on the specified atom
        """
        if am_type not in am_types:
            raise Exception(f'Invalid am_type, got: {am_type}, expected {am_types}')
        val = 0
        if isinstance(atom, str):
            for ao_contrib in self.contributions:
                if ao_contrib.atom == atom and ao_contrib.ao[0] == am_type:
                    val += ao_contrib.val
        elif isinstance(atom, int):
            for ao_contrib in self.contributions:
                if ao_contrib.index == atom and ao_contrib.ao[0] == am_type:
                    val += ao_contrib.val
        else:
            raise SyntaxError('Atom specifier must be either an int or str.')

        return val


class AO_Contrib:
    """
    Simple class containing an AO and its contribution to an MOrbital
    """
    def __init__(self, index, atom, ao, val, spin=None):
        self.index = index
        self.atom = atom
        self.ao = ao
        self.val = val
        self.spin = spin

    def __repr__(self):
        return f'<AOC {self.index}{self.gspin} {self.atom} {self.ao} [{self.val}]>'

    def __eq__(self, other):
        """
        Use np.allclose or almost_equal???
        """
        if not isinstance(other, AO_Contrib):
            return False
        if self.index == other.index \
                and self.atom == other.atom \
                and self.ao == other.ao \
                and self.val == other.val:
            return True
        return False

    def __str__(self):
        return f'{self.index:>2d} {self.atom:<2s} {self.ao:<4s}: {self.val:>4.1f}'

    @property
    def am(self):
        return search('[a-z]', self.ao).group()

    @property
    def gspin(self):
        if self.spin == 1:
            return 'α'
        elif self.spin == -1:
            return 'β'
        return ''

    def __sub__(self, other):
        index = self.index if self.index == other.index else 0
        atom  = self.atom  if self.atom  == other.atom  else ''
        ao    = self.ao    if self.ao    == other.ao    else ''
        val   = self.val - other.val

        return AO_Contrib(index, atom, ao, val)

    def csv(self):
        return f'{self.index:>2d}, {self.atom:<2s}, {self.ao:<4s}, {self.val:>4.1f}'


class Group_Contrib:
    """
    Simple class containing a group of atoms and their contribution to a MOrbital
    """
    def __init__(self, index, group, val):
        self.index = index
        self.group = group
        self.val = val

    def __eq__(self, other):
        """
        Use np.allclose or almost_equal???
        """
        if not isinstance(other, Group_Contrib):
            return False
        if self.index == other.index \
                and self.group == other.group \
                and self.val == other.val:
            return True
        return False

    def __str__(self):
        return f'{self.index:>2d} {self.group:<10}: {self.val:>4.1f}'

    def __sub__(self, other):
        index = self.index if self.index == other.index else 0
        group = self.group if self.group == other.group else ''
        val = self.val - other.val

        return Group_Contrib(index, atom, ao, val)
