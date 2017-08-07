import re


class RedundantInternals:
    """Redundant Internal Coordinates"""
    def __init__(self, lines):
        self.bond_vals, self.angle_vals = RedundantInternals.read(lines)

    def diffs(self, other, thresh=(3, 2, 2)):
        """
        Difference between two sets of redundant internals
        Warning, must be exactly the same numbering of the geometry
        :param thresh: list of threshold values for comparison printing
                        if thresh[i] = None, no cutting will be done
        """
        mismatch = 0
        def check(vals1, vals2, thresh=3):
            mismatch = 0
            for (*atoms1, final1), (*atoms2, final2) in zip(vals1, vals2):
                if atoms1 != atoms2:
                    mismatch += 1
                    continue
                if thresh is None or abs(final2 - final1) > 10**-thresh:
                    f = '-'.join(['{:>3} {:<2}']*int(len(atoms1)/2)) + f' = {final2 - final1:> 5.3f}'
                    print(f.format(*atoms1))
            return mismatch
        print('Bonds')
        mismatch = check(self.bond_vals, other.bond_vals, thresh=thresh[0])
        print(f'Bond Mismatch: {mismatch}')
        #print('\nAngles')
        #mistmatch = check(self.angle_vals, other.angle_vals, thresh=thresh[1])
        #print(f'Angle Mismatch: {mismatch}')


    def read(lines):
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
                t, idx1, atom1, idx2, atom2, atom_idx3, atom_idx4, other, old, slope, step, final = re.search(regex, line).groups()
            except AttributeError as e:
                pass

            if atom_idx3:
                atom3, idx3 = atom_idx3[1:].split()
                if atom_idx4:
                    atom4, idx4 = atom_idx4[1:].split()
                    if other:
                        other = other[1:].strip()

            if t == 'B':
                bond_vals.append([idx1, atom1, idx2, atom2, float(final)])
            elif t == 'A':
                angle_vals.append([idx1, atom1, idx2, atom2, idx3, atom3, float(final)])
            elif t == 'L':
                linear_vals.append([idx1, atom1, idx2, atom2, idx3, atom3, atom4, idx4, other, float(final)])
            elif t == 'D':
                dihedral_vals.append([idx1, atom1, idx2, atom2, idx3, atom3, atom4, idx4, float(final)])
            else:
                raise ValueError('Cannot identify coordinate type')

        return bond_vals, angle_vals