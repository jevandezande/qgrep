import unittest
from sys import path
import numpy as np
from numpy.testing import assert_almost_equal
path.insert(0, '..')
from qgrep.nbo import NPA, NPA_Diff


class TestNPA(unittest.TestCase):
    """Tests the NPA class"""

    def test_read(self):
        with open('H2O.nbo') as f:
            lines = f.readlines()
        npa = NPA(lines=lines)

    def test_sub(self):
        with open('H2O.nbo') as f:
            lines = f.readlines()
        h2o = NPA(lines=lines)
        npa = NPA_Diff()
        npa.atoms = h2o.atoms
        npa.charges = np.zeros(h2o.charges.shape)
        self.assertEqual((h2o - h2o), npa)

        with open('H2O_stretched.nbo') as f:
            lines = f.readlines()
        h2o_stretched = NPA(lines=lines)

        diff = np.array([[ 0.31616,  0.00000, -0.31758, 0.00142, -0.31616],
                         [-0.63440, -0.00015,  0.63245, 0.00210,  0.63440],
                         [ 0.31823,  0.00000, -0.31965, 0.00142, -0.31823]])
        diff = NPA_Diff(atoms=h2o.atoms, charges=diff)

        self.assertEqual((h2o - h2o_stretched), diff)
        assert_almost_equal((h2o - h2o_stretched).charges, diff.charges)

    def test_add(self):
        with open('H2O.nbo') as f:
            lines = f.readlines()
        h2o = NPA(lines=lines)
        assert_almost_equal((h2o + h2o).charges, 2*h2o.charges)

        with open('H2O_stretched.nbo') as f:
            lines = f.readlines()
        h2o_stretched = NPA(lines=lines)

        add = np.array([[ 0.50164, 0.00000,  1.49684, 0.00152,  1.49836],
                        [-1.00122, 3.99983, 12.99917, 0.00222, 17.00122],
                        [ 0.49957, 0.00000,  1.49891, 0.00152,  1.50043]])

        assert_almost_equal((h2o + h2o_stretched).charges, add)
        

if __name__ == '__main__':
    unittest.main()
