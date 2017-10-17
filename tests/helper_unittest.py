import unittest
import numpy as np

from sys import path

path.insert(0, '..')

from qgrep import helper


class TestHelper(unittest.TestCase):

    def test_convert_energy(self):
        self.assertEqual(627.509, helper.convert_energy(1, 'hartree', 'kcal/mol'))
        self.assertAlmostEqual(0.0251223, helper.convert_energy(2.1, '1/cm', 'kJ/mol'), 5)
        self.assertRaises(SyntaxError, helper.convert_energy, 1, 'hart', '1/cm')
        self.assertAlmostEqual(0, sum(np.array([27.21138602, 54.42277204]) - helper.convert_energy([1, 2], 'hartree', 'eV')), 5)
        self.assertAlmostEqual(0, sum([11.7152, 16.3176]) -
                               sum(helper.convert_energy([2.8, 3.9], 'kcal/mol', 'kJ/mol')), 5)

if __name__ == '__main__':
    unittest.main()
