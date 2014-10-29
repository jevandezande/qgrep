import unittest
from sys import path
path.append('../..')
from basis import Contraction, Basis, BasisSet
import numpy as np
from collections import OrderedDict


class TestContraction(unittest.TestCase):
    """Tests a basis contraction"""
    def setUp(self):
        self.cons = Contraction('S', [1, 2], [0.5, 0.5])
        self.conp = Contraction('P', [0.01, 0.2, 1], [0.3, 0.4, 0.3])
        self.cond = Contraction('D', [1, 2], [0.3, 0.7], [0.4, 0.6])

    def test_len(self):
        """Test __len__"""
        self.assertEqual(2, len(self.cons))
        self.assertEqual(3, len(self.conp))
        self.assertEqual(2, len(self.cond))

    def test_getset(self):
        """Test __getitem__ and __setitem__"""
        # Convert np.array to list to prevent error in case.py as the truth value of an array is ambiguous
        self.assertEqual([1.0, 0.5], list(self.cons[0]))
        # Convert to a list of lists
        self.assertEqual([[0.01, 0.3], [1.0, 0.3]], list(map(list, self.conp[::2])))

        self.cons[0] = [1, 2]
        self.assertEqual([1.0, 2], list(self.cons[0]))
        self.cond[0] = [1, 0.2, 0.3]
        self.assertEqual([1.0, 0.2, 0.3], list(self.cond[0]))

    def test_exps_coeffs_coeffs2(self):
        """Test exps, coeffs, and coeffs2"""
        self.assertEqual([1, 2], list(self.cons.exps))
        self.assertEqual([0.3, 0.4, 0.3], list(self.conp.coeffs))
        self.assertEqual([0.4, 0.6], list(self.cond.coeffs2))

    def test_print(self):
        """Test print"""
        s_gamess = '''S     2
  1      1.0000000   0.5000000
  2      2.0000000   0.5000000'''
        p_gaussian94 = '''P     3
        0.0100000   0.3000000
        0.2000000   0.4000000
        1.0000000   0.3000000'''
        self.assertEqual(s_gamess, self.cons.print('gamess'))
        self.assertEqual(p_gaussian94, self.conp.print())


class TestBasis(unittest.TestCase):
    """Tests a basis, which contains basis contractions"""
    def setUp(self):
        self.cons = Contraction('S', [1, 2], [0.5, 0.5])
        self.conp = Contraction('P', [0.01, 0.2, 1], [0.3, 0.4, 0.3])
        self.basis = Basis('C', [self.cons, self.conp])

    def test_len(self):
        """Test __len__"""
        self.assertEqual(2, len(self.basis))

    def test_print(self):
        """Test print"""
        c_gamess = '''CARBON
S     2
  1      1.0000000   0.5000000
  2      2.0000000   0.5000000
P     3
  1      0.0100000   0.3000000
  2      0.2000000   0.4000000
  3      1.0000000   0.3000000'''
        c_gaussian94 = '''C    0
S     2
        1.0000000   0.5000000
        2.0000000   0.5000000
P     3
        0.0100000   0.3000000
        0.2000000   0.4000000
        1.0000000   0.3000000'''
        self.assertEqual(c_gaussian94, self.basis.print())
        self.assertEqual(c_gamess, self.basis.print('gamess'))


class TestBasisSet(unittest.TestCase):
    """Test the BasisSet class"""
    def setUp(self):
        cons = Contraction('S', [1, 2], [0.5, 0.5])
        conp = Contraction('P', [0.01, 0.2, 1], [0.3, 0.4, 0.3])
        h = Basis('H', [cons, conp])
        cons = Contraction('S', [0.1, 0.4], [0.6, 0.4])
        conp = Contraction('D', [0.1, 0.4, 3], [0.2, 0.3, 0.5])
        c = Basis('C', [cons, conp])

        atoms = OrderedDict([('H', h), ('C', c)])
        self.basis = BasisSet(atoms)

    def test_check_basis_set(self):
        """Test check_basis_set"""
        self.assertRaises(SyntaxError, BasisSet.check_basis_set, ({'H': 1}))
        self.assertRaises(SyntaxError, BasisSet.check_basis_set, (OrderedDict([('H', 1)])))

    def test_change_basis(self):
        """Test change_basis"""
        atoms = OrderedDict([('C', Basis('C', [Contraction('S', [1], [1])]))])
        self.basis.change_basis(atoms)
        bad_bs = OrderedDict([('H', 1)])
        self.assertRaises(SyntaxError, self.basis.change_basis, (bad_bs,))

    def test_read_basis(self):
        """Test read_basis"""
        pass


if __name__ == '__main__':
    unittest.main()
