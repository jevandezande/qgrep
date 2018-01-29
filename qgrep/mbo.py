import re
from more_itertools import collapse


class MBO:
    """Mayer bond order class"""
    def __init__(self, file_iter):
        self.bond_orders = MBO.read(file_iter)

    def __str__(self):
        strs = []
        for (idx1, atom1), (idx2, atom2), val in self.bond_orders:
            strs.append(f'{idx1:>3} {atom1:<2} - {idx2:>3} {atom2:<2} = {val:5.4f}')
        return '\n'.join(strs)

    def diffs(self, other, thresh=4):
        """Compare two MBOs"""
        mismatch = 0
        def check(vals1, vals2, thresh=4):
            mismatch = 0
            for (*atoms1, final1), (*atoms2, final2) in zip(vals1, vals2):
                if atoms1 != atoms2:
                    mismatch += 1
                    continue
                if thresh is None or abs(final2 - final1) > 10**-thresh:
                    f = '-'.join(['{:>3} {:<2}']*int(len(atoms1))) + (' = {:> 5.' + f'{thresh}' + 'f}').format(final2 - final1)
                    print(f.format(*collapse(atoms1)))
            return mismatch
        mismatch = check(self.bond_orders, other.bond_orders, thresh=thresh)
        print(f'Bond Order Mismatch: {mismatch}')

    @staticmethod
    def read(file_iter):
        """Read from file"""
        for line in file_iter:
            if line == '  Mayer bond orders larger than 0.1\n':
                break
        regex = '(\d+)-(\w\w?)\s?,\s*(\d+)-(\w\w?)\s?\) :\s*(\d\.\d+)'
        bond_orders = []
        for line in file_iter:
            matches = re.findall(regex, line)
            if not matches:
                break
            for match in matches:
                idx1, atom1, idx2, atom2, val = match
                bond_orders.append([(int(idx1), atom1), (int(idx2), atom2), float(val)])

        return bond_orders
