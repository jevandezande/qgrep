"""Source for all Löwdin orbital analysis related functions"""
import re
import numpy as np


class ReducedOrbitalPopulation:
    """Löwdin Reduced Orbital Population class (ROP for short)"""

    def __init__(self, file_name='', orb_list=None, method='lowdin'):
        if file_name:
            self.orb_list = self.read(file_name)
        elif orb_list is not None:
            self.orb_list = orb_list
        else:
            sel.orb_list = []
    
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
            raise SyntaxError('Must be an Orbital.')
        self.orb_list[index] = value

    def __str__(self):
        return '\n\n'.join([str(orb) for orb in self.orb_list])

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
        Returns the indeces of the SOMO's

        WARNING: 0-indexed
        """
        somos = []
        for i, orb in enumerate(self):
            if orb.occupation == 1:
               somos.append(i)

        return somos

    #def __sub__(self, other):
    #    if self.atoms != other.atoms:
    #        raise SyntaxError('Atoms do not match')
    #    npa_diff = NPA_Diff()
    #    npa_diff.atoms = self.atoms
    #    npa_diff.charges = self.charges - other.charges
    #    return npa_diff

    #def __add__(self, other):
    #    if self.atoms != other.atoms:
    #        raise SyntaxError('Atoms do not match')
    #    npa = NPA()
    #    npa.atoms = self.atoms
    #    npa.charges = self.charges + other.charges
    #    return npa

    def append(self, orbital):
        """
        Append another orbital
        """
        if not isinstance(orbital, MOrbital):
            raise SyntaxError('You may only append Orbitals.')
        self.orb_list.append(orbital)

    def crop(self, max_num=5, min_num=2, cutoff=5):
        """
        Make an ROP that removes the smallest contributors
        """
        orb_list = []
        for mo in self.orb_list:
            aos = []
            for ao_contrib in sorted(mo.contributions, key=lambda x: x.val):
                if ao_contrib.val < cutoff and len(aos) >= min_num:
                    break

                aos.append(ao_contrib)

                if len(aos) == max_num:
                    break
            orb_list.append(MOrbital(mo.number, mo.energy, mo.occupation, aos))

        return ReducedOrbitalPopulation(orb_list=orb_list)

    def range(self, low, high):
        """
        Make an ROP with a restricted range of orbitals
        """
        return ReducedOrbitalPopulation(orb_list=self.orb_list[low:high])
            
    @staticmethod
    def read(file_name, program='orca', method='lowdin'):
        """Read the reduced Löwdin orbital populations
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
                lines = block.split('\n')

                # Remove excess from the first block
                if first:
                    # If open shell, an extra line is printed
                    if lines[3] == 'SPIN UP':
                        lines = lines[4:]
                    else:
                        lines = lines[3:]
                    first = False

                # Parse out the header
                nums = lines[0].split()
                orb_es = lines[1].split()
                occs = lines[2].split()
                orbs = []
                for i in range(len(nums)):
                    num, orb_e, occ = int(nums[i]), float(orb_es[i]), round(float(occs[i]))
                    # Add orbitals without occupations (added in next section)
                    orbs.append(MOrbital(num, orb_e, occ))

                # Parse out the orbital contributions
                for line in lines[4:]:
                    num, atom, ao, *vals = line.split()
                    num = int(num)
                    for i, val in enumerate(vals):
                        # If there is occupation, this deletes all the appearances of 0.0
                        # Due to rounding, the occupations will not add up to 100
                        val = float(val)
                        if val > 0:
                            ao_contrib = AO_Contrib(num, atom, ao, val)
                            orbs[i].contributions.append(ao_contrib)

                orb_list += orbs
        else:
            raise Exception('Unable to find the start of Reduced Orbital Population analysis')

        return orb_list


class MOrbital:
    """
    Simple orbital class that holds the contributions from AOs as well as a
    little more necessary information
    """
    def __init__(self, number=0, energy=0, occupation=0, contributions=None):
        self.number = number
        self.energy = energy
        self.occupation = occupation
        self.contributions = []
        if contributions is not None:
            self.contributions = contributions

    def __eq__(self, other):
        """
        Checks if all values are equal
        """
        if self.number == other.number \
                and np.isclose(self.energy, other.energy) \
                and np.isclose(self.occupation, other.occupation):
            for s, o in zip(self.contributions, other.contributions):
                if not s == o:
                    return False
            return True
        return False

    def __str__(self):
        ao_contrib_str = '\n'.join([str(ao_contrib) for ao_contrib in self.contributions])
        return '{: >2d} {: > 6.4f} {:>3.2f}\n{}'.format(self.number, self.energy, self.occupation, ao_contrib_str)

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
                if ao_contrib.num == atom:
                    val += ao_contrib.val
        else:
            raise SyntaxError('Atom specifiewr must be either an int or str.')
        
        return val

    def orbital_type_sum(self, atom, ao_type):
        """
        Sum over all the contributions from an orbital type on the specified atom
        """
        if not ao_type in ['s', 'p', 'd', 'f', 'g', 'h']:
            raise Exception('Invalid ao_type')
        val = 0
        if isinstance(atom, str):
            for ao_contrib in self.contributions:
                if ao_contrib.atom == atom and ao_contrib.ao[0] == ao_type:
                    val += ao_contrib.val
        elif isinstance(atom, int):
            for ao_contrib in self.contributions:
                if ao_contrib.num == atom and ao_contrib.ao[0] == ao_type:
                    val += ao_contrib.val
        else:
            raise SyntaxError('Atom specifiewr must be either an int or str.')

        return val


class AO_Contrib:
    """
    Simple class containing an AO and its contribution to an orbital
    """
    def __init__(self, num, atom, ao, val):
        self.num = num
        self.atom = atom
        self.ao = ao
        self.val = val

    def __eq__(self, other):
        """
        Use np.allclose or almost_equal???
        """
        if self.num == other.num \
                and self.atom == other.atom \
                and self.ao == other.ao \
                and self.val == other.val:
            return True
        return False

    def __str__(self):
        return '{:>2d} {:<2s} {:<4s}: {:>4.1f}'.format(self.num, self.atom, self.ao, self.val)
