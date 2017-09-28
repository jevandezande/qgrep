import os
import unittest
import numpy as np

from sys import path

path.insert(0, '..')

from qgrep.molecule import Molecule


class TestMolecule(unittest.TestCase):
    """Tests the Molecule class"""

    def setUp(self):
        """Set up for every test"""
        self.water_geom = [['H', [0, 0, 0]],
                           ['O', [0, 0, 1]],
                           ['H', [0, 1, 1]]]
        self.water = Molecule(self.water_geom)

    def test_len(self):
        """Testing __len__"""
        self.assertEqual(len(self.water), 3)

    def test_getsetdeleqinsert(self):
        """Test getting, setting and deleting atoms"""
        self.assertEqual(self.water[0][0], 'H')
        self.assertTrue(all(self.water[0][1] == np.array([0, 0, 0])))
        del self.water[1]
        self.assertEqual(self.water[1][0], 'H')
        self.assertTrue(all(self.water[1][1] == np.array([0, 1, 1])))
        self.water[0] = ['H', [0, 0, 0]]
        self.water[1] = ['H', [0, -1, 1]]
        self.assertEqual(self.water[1][0], 'H')
        self.assertTrue(all(self.water[1][1] == np.array([0, -1, 1])))
        self.water.insert(1, 'O', [0, 0, 1])
        self.assertEqual(self.water[1][0], 'O')
        self.assertTrue(all(self.water[1][1] == np.array([0, 0, 1])))
        self.assertEqual(self.water[2][0], 'H')
        self.assertTrue(all(self.water[2][1] == np.array([0, -1, 1])))
        new_water = Molecule([['H', [0, 0, 0]], ['O', [0, 0, 1]], ['H', [0, -1, 1]]])
        self.assertEqual(self.water, new_water)

    def test_str(self):
        """Testing __str__"""
        water_string = """\
H       0.00000000    0.00000000    0.00000000
O       0.00000000    0.00000000    1.00000000
H       0.00000000    1.00000000    1.00000000"""
        self.assertEqual(str(self.water), water_string)

    def test_check_atom(self):
        """Test check_atom throws errors correctly"""
        atom, xyz = ['H', [0, 1, 2]]
        self.assertTrue(Molecule.check_atom(atom, xyz))
        self.assertRaises(SyntaxError, Molecule.check_atom, [[]], 'a')
        self.assertRaises(TypeError, Molecule.check_atom, [[1, 2, 3]])
        self.assertRaises(SyntaxError, Molecule.check_atom, [[0, 1, 2, 3]], 'a')
        self.assertRaises(SyntaxError, Molecule.check_atom, ['H', [1]], ['a', [3]])

    def test_check_geom(self):
        """Test check_geom throws errors correctly"""
        self.assertTrue(Molecule.check_geom(self.water_geom))
        # Zero-length geometries are valid
        self.assertTrue(Molecule.check_geom([]))
        self.assertRaises(ValueError, Molecule.check_geom, [[[1, 2, 3]]])
        self.assertRaises(TypeError, Molecule.check_geom, ['H'], [[[0, 1, 2, 3]]])
        self.assertRaises(SyntaxError, Molecule.check_geom, [['H', [1, 'a', 3]]])

    def test_read_write_geometry(self):
        """Testing read and write"""
        test_file = 'geom.xyz.tmp'
        self.water.write(test_file, True)
        mol = Molecule.read_from(test_file)
        mol.name = 'H2O'
        self.assertEqual(mol.geom, self.water.geom)
        mol.write(test_file, style='latex')
        latex_geom = '''\
\\begin{verbatim}
H       0.000000      0.000000      0.000000
O       0.000000      0.000000      1.000000
H       0.000000      1.000000      1.000000
\\end{verbatim}'''
        with open(test_file) as f:
            out_tex = f.read()
        self.assertEqual(latex_geom, out_tex)

        os.remove(test_file)


if __name__ == '__main__':
    unittest.main()
