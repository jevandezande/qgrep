import re

from more_itertools import collapse


class RedundantInternals:
    """Redundant Internal Coordinates"""
    def __init__(self, lines):
        self.bond_vals, self.angle_vals, self.linear_vals, self.dihredal_vals = RedundantInternals.read(lines)

    def print(self, bonds=True, angles=False, dihedrals=False):
        """ Print values """
        out = ''
        if bonds:
            for *atoms, final in self.bond_vals:
                f = '-'.join(['{:>3} {:<2}']*int(len(atoms))) + f' = {final:> 5.4f}\n'
                out += f.format(*collapse(atoms))

        if angles:
            for val in self.angle_vals + self.linear_vals:
                pass
        if dihedrals:
            for val in self.dihedral_vals:
                pass

        return out


    def diffs(self, other, thresh=(3, 2, 2)):
        """
        Difference between two sets of redundant internals
        Warning, must be exactly the same numbering of the geometry
        :param thresh: list of threshold values for comparison printing
                        if thresh[i] = None, no cutting will be done
        """
        def check(vals1, vals2, thresh=3):
            mismatch = 0
            for (*atoms1, final1), (*atoms2, final2) in zip(vals1, vals2):
                if atoms1 != atoms2:
                    mismatch += 1
                    continue
                if thresh is None or abs(final2 - final1) > 10**-thresh:
                    f = '-'.join(['{:>3} {:<2}']*int(len(atoms1))) + (' = {:> 5.' + str(thresh) + 'f}').format(final2 - final1)
                    print(f.format(*collapse(atoms1)))
            return mismatch
        print('Bonds')
        mismatch = check(self.bond_vals, other.bond_vals, thresh=thresh[0])
        print(f'Bond Mismatch: {mismatch}')
        #print('\nAngles')
        #mistmatch = check(self.angle_vals, other.angle_vals, thresh=thresh[1])
        #print(f'Angle Mismatch: {mismatch}')

    def diff_metric(self, other, metric='sad'):
        mismatch = 0
        diff = 0
        for (*atoms1, final1), (*atoms2, final2) in zip(self.bond_vals, other.bond_vals):
            if atoms1 != atoms2:
                mismatch += 1
                continue
            # Sum of absolute deviation
            if metric == 'sad':
                diff += abs(final2 - final1)
        print(diff)
        print(f'Bond Mismatch: {mismatch}')


    def read(lines, sort=True):
        """
        Parse the Redundant Internal Coordinates from an Orca output file
        TODO: Make work for Dihedrals
        """
        """
    ---------------------------------------------------------------------------
                         Redundant Internal Coordinates

                          --- Optimized Parameters ---
                            (Angstroem and degrees)

        Definition                    OldVal   dE/dq     Step     FinalVal
    ----------------------------------------------------------------------------
     1. B(O   1,C   0)                1.4658 -0.000017  0.0000    1.4658
    37. A(C   4,C   0,C  17)          113.60 -0.000000   -0.00    113.60
    92. L(C  21,C  22,N  23,C  24, 2) 179.99 -0.000002    0.00    179.99
    97. D(C   2,O   1,C   0,C   4)     -0.02 -0.000001    0.00     -0.02
"""

        start = -1
        for i, line in enumerate(reversed(lines)):
            if line.strip() == '--- Optimized Parameters ---':
                start = len(lines) - i + 4
                break
        if start == -1:
            raise Exception('Cannot find the start of the redundant internals')

        regex = r'\d+\.\s+(\w)\((\w+)\s+(\d+),(\w+)\s+(\d+)(,\w+\s+\d+)?(,\w+\s+\d+)?(,\s*\d+)?\)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+\.\d+)'

        bond_vals = []
        angle_vals = []
        linear_vals = []
        dihedral_vals = []
        for line in lines[start:]:
            line = line.strip()
            if line[0] == '-':
                break

            try:
                t, atom1, idx1, atom2, idx2, atom_idx3, atom_idx4, other, old, slope, step, final = re.search(regex, line).groups()
            except AttributeError as e:
                pass

            if atom_idx3:
                atom3, idx3 = atom_idx3[1:].split()
                if atom_idx4:
                    atom4, idx4 = atom_idx4[1:].split()
                    if other:
                        other = other[1:].strip()

            if t == 'B':
                pair1, pair2 = sorted(((int(idx1), atom1), (int(idx2), atom2)))
                bond_vals.append([pair1, pair2, float(final)])
            elif t == 'A':
                pair1, pair2, pair3 = sorted(((int(idx1), atom1), (int(idx2), atom2), (int(idx3), atom3)))
                angle_vals.append([pair1, pair2, pair3, float(final)])
            elif t == 'L':
                pair1, pair2, pair3, pair4 = sorted(((int(idx1), atom1), (int(idx2), atom2), (int(idx3), atom3), (int(idx4), atom4)))
                linear_vals.append([pair1, pair2, pair3, pair4, other, float(final)])
            elif t == 'D':
                pair1, pair2, pair3, pair4 = sorted(((int(idx1), atom1), (int(idx2), atom2), (int(idx3), atom3), (int(idx4), atom4)))
                dihedral_vals.append([pair1, pair2, pair3, pair4, float(final)])
            else:
                raise ValueError('Cannot identify coordinate type')

        #bond_vals = sorted(bond_vals)
        #angle_vals = sorted(angle_vals)
        #linear_vals = sorted(linear_vals)
        #dihedral_vals = sorted(dihedral_vals)

        return bond_vals, angle_vals, linear_vals, dihedral_vals
