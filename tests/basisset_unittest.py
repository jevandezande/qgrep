import unittest
from sys import path
path.append('../..')
from basis import Contraction, Basis, BasisSet
import numpy as np
from collections import OrderedDict
import os


class TestContraction(unittest.TestCase):
    """Tests a basis contraction"""
    def setUp(self):
        self.cons = Contraction('S', [1, 2], [0.5, 0.5])
        self.conp = Contraction('P', [0.01, 0.2, 1], [0.3, 0.4, 0.3])
        self.cond = Contraction('D', [1, 2], [0.3, 0.7], [0.4, 0.6])
        self.consp = Contraction('SP', [0.1, 0.4, 3], [0.2, 0.3, 0.5], [0.1, 0.3, 0.6])

    def test_len(self):
        """Test __len__"""
        self.assertEqual(2, len(self.cons))
        self.assertEqual(3, len(self.conp))
        self.assertEqual(2, len(self.cond))
        self.assertEqual(3, len(self.consp))

    def test_getset(self):
        """Test __getitem__ and __setitem__"""
        # Convert np.array to list to prevent error in case.py as the truth value of an array is ambiguous
        self.assertEqual([1.0, 0.5], list(self.cons[0]))
        # Convert to a list of lists
        self.assertEqual([[0.01, 0.3], [1.0, 0.3]], list(map(list, self.conp[::2])))

        self.cons[0] = [1, 2]
        self.assertEqual([1.0, 2], list(self.cons[0]))
        self.assertRaises(ValueError, self.cons.__setitem__, 1, [1, 2, 4])
        self.cond[0] = [1, 0.2, 0.3]
        self.assertEqual([1.0, 0.2, 0.3], list(self.cond[0]))
        self.consp[0] = [1, 2, 4]
        self.assertEqual([1, 2, 4], list(self.consp[0]))
        self.assertRaises(ValueError, self.consp.__setitem__, 1, [1, 2])

    def test_exps_coeffs_coeffs2(self):
        """Test exps, coeffs, and coeffs2"""
        self.assertEqual([1, 2], list(self.cons.exps))
        self.assertEqual([0.3, 0.4, 0.3], list(self.conp.coeffs))
        self.assertEqual([0.4, 0.6], list(self.cond.coeffs2))

    def test_print(self):
        """Test print"""
        s_gamess = '''S     2
  1      1.0000000   0.5000000
  2      2.0000000   0.5000000
'''
        p_gaussian94 = '''P     3
        0.0100000   0.3000000
        0.2000000   0.4000000
        1.0000000   0.3000000
'''
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

    def test_getset(self):
        """Test __getitem__ and __setitem__"""
        con = Contraction('F', [4, 9], [0.1, 0.9])
        self.basis[0] = con
        self.assertEqual(con, self.basis[0])
        self.assertRaises(SyntaxError, self.basis.__setitem__, 0, 1)

    def test_print(self):
        """Test print"""
        c_gamess = '''CARBON
S     2
  1      1.0000000   0.5000000
  2      2.0000000   0.5000000
P     3
  1      0.0100000   0.3000000
  2      0.2000000   0.4000000
  3      1.0000000   0.3000000
'''
        c_gaussian94 = '''C    0
S     2
        1.0000000   0.5000000
        2.0000000   0.5000000
P     3
        0.0100000   0.3000000
        0.2000000   0.4000000
        1.0000000   0.3000000
'''
        self.assertEqual(c_gaussian94, self.basis.print())
        self.assertEqual(c_gamess, self.basis.print('gamess'))


class TestBasisSet(unittest.TestCase):
    """Test the BasisSet class"""
    def setUp(self):
        cons = Contraction('S', [1, 2], [0.5, 0.5])
        conp = Contraction('P', [0.01, 0.2, 1], [0.3, 0.4, 0.3])
        h = Basis('H', [cons, conp])
        cons = Contraction('S', [0.1, 0.4], [0.6, 0.4])
        consp = Contraction('SP', [0.1, 0.4, 3], [0.2, 0.3, 0.5], [0.1, 0.3, 0.6])
        c = Basis('C', [cons, consp])

        atoms = OrderedDict([('H', h), ('C', c)])
        self.basis_set = BasisSet(atoms)

    def test_check_basis_set(self):
        """Test check_basis_set"""
        self.assertRaises(SyntaxError, BasisSet.check_basis_set, ({'H': 1}))
        self.assertRaises(SyntaxError, BasisSet.check_basis_set, (OrderedDict([('H', 1)])))

    def test_change_basis_set(self):
        """Test change_basis_set"""
        atoms = OrderedDict([('C', Basis('C', [Contraction('S', [1], [1])]))])
        self.basis_set.change_basis_set(atoms)
        bad_bs = OrderedDict([('H', 1)])
        self.assertRaises(SyntaxError, self.basis_set.change_basis_set, (bad_bs,))

    def test_readprint_basis(self):
        """Test read_basis and print_basis"""
        test_file = 'basis.gbs.tmp'
        open(test_file, 'w').write(self.basis_set.print_basis_set('gaussian94'))
        self.basis_set.read_basis_set(test_file, 'gaussian94')
        open(test_file, 'w').write(self.basis_set.print_basis_set('gamess'))
        self.basis_set.read_basis_set(test_file, 'gamess')

        os.remove(test_file)

    def test_values(self):
        """Test values"""
        vals = [[np.array([[1.0,  0.5], [2.0,  0.5]]), np.array([[0.01,  0.3], [0.2,  0.4], [1.0,  0.3]])],
                [np.array([[0.1,  0.6], [0.4,  0.4]]), np.array([[0.1,  0.2], [0.4,  0.3], [3.0,  0.5]])]]
        self.assertEqual(vals[0][0][0][1], self.basis_set.values()[0][0][0][1])
        self.assertEqual(vals[0][1][1][0], self.basis_set.values()[0][1][1][0])

if __name__ == '__main__':
    unittest.main()
