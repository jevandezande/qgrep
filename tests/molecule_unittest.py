import unittest
from sys import path
path.append('../..')
from molecule import Molecule
import os


class TestMolecule(unittest.TestCase):
    """Tests the Molecule class"""

    def setUp(self):
        """Set up for every test"""
        self.water = Molecule([['H', 0, 0, 10], ['O', 0, 0, 11], ['H', 0, -1, 11]])

    def test_len(self):
        """Testing __len__"""
        self.assertEqual(len(self.water), 3)

    def test_getsetdeleqinsert(self):
        """Test getting, setting and deleting atoms"""
        self.assertEqual(self.water[0], ['H', 0, 0, 10])
        del self.water[1]
        self.assertEqual(self.water[1], ['H', 0, -1, 11])
        self.water[0] = ['H', 0, 0, 0]
        self.water[1] = ['H', 0, 1, 1]
        self.assertEqual(self.water[1], ['H', 0, 1, 1])
        self.water.insert(1, ['O', 0, 0, 1])
        self.assertEqual(self.water[1], ['O', 0, 0, 1])
        self.assertEqual(self.water[2], ['H', 0, 1, 1])
        self.assertEqual(self.water, Molecule([['H', 0, 0, 0], ['O', 0, 0, 1], ['H', 0, 1, 1]]))

    def test_str(self):
        """Testing __str__"""
        water_string = """H             0.00000000      0.00000000     10.00000000
O             0.00000000      0.00000000     11.00000000
H             0.00000000     -1.00000000     11.00000000"""
        self.assertEqual(str(self.water), water_string)

    def test_check_atom(self):
        """Test check_atom throws errors correctly"""
        atom = ['H', 0, 1, 2]
        self.assertTrue(Molecule.check_atom(atom))
        self.assertRaises(SyntaxError, Molecule.check_atom, [[]])
        self.assertRaises(SyntaxError, Molecule.check_atom, [[1, 2, 3]])
        self.assertRaises(SyntaxError, Molecule.check_atom, [[0, 1, 2, 3]])
        self.assertRaises(SyntaxError, Molecule.check_atom, [['H', 1, 'a', 3]])

    def test_check_geom(self):
        """Test check_geom throws errors correctly"""
        water = [['H', 0, 0, 0], ['O', 0, 0, 1], ['H', 0, 1, 1]]
        self.assertTrue(Molecule.check_geom(water))
        # Zero-length geometries are valid
        self.assertTrue(Molecule.check_geom([]))
        self.assertRaises(SyntaxError, Molecule.check_geom, [[[1, 2, 3]]])
        self.assertRaises(SyntaxError, Molecule.check_geom, [[[0, 1, 2, 3]]])
        self.assertRaises(SyntaxError, Molecule.check_geom, [[['H', 1, 'a', 3]]])

    def test_read_write_geometry(self):
        """Testing read and write"""
        test_file = 'geom.xyz.tmp'
        self.water.write(test_file, True)
        mol = Molecule()
        mol.read(test_file)
        self.assertEqual(mol.geometry, self.water.geometry)

        os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
