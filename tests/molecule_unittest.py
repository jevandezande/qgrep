import unittest
from sys import path
path.append('../..')
from molecule import Molecule
import os


class TestMolecule(unittest.TestCase):
    """Tests the Molecule class"""

    def setUp(self):
        """Set up for every test"""
        self.water_xyz = Molecule([['H', 0, 0, 10], ['O', 0, 0, 11], ['H', 0, -1, 11]])
        self.water_zmatrix = Molecule([['O'], ['H', 1, 0], ['H', 1, 1, 2, 104.5]])

    def test_len(self):
        """Testing __len__"""
        self.assertEqual(len(self.water_xyz), 3)

    def test_getsetdeleqinsert_xyz(self):
        """Test getting, setting and deleting atoms"""
        self.assertEqual(self.water_xyz[0], ['H', 0, 0, 10])
        del self.water_xyz[1]
        self.assertEqual(self.water_xyz[1], ['H', 0, -1, 11])
        self.water_xyz[0] = ['H', 0, 0, 0]
        self.water_xyz[1] = ['H', 0, 1, 1]
        self.assertEqual(self.water_xyz[1], ['H', 0, 1, 1])
        self.water_xyz.insert(1, ['O', 0, 0, 1])
        self.assertEqual(self.water_xyz[1], ['O', 0, 0, 1])
        self.assertEqual(self.water_xyz[2], ['H', 0, 1, 1])
        self.assertEqual(self.water_xyz, Molecule([['H', 0, 0, 0], ['O', 0, 0, 1], ['H', 0, 1, 1]]))

    def test_getsetdeleqinsert_zmat(self):
        """Test getting, setting and deleting atoms"""
        self.assertEqual(self.water_xyz[0], ['H', 0, 0, 10])
        del self.water_xyz[1]
        self.assertEqual(self.water_xyz[1], ['H', 0, -1, 11])
        self.water_xyz[0] = ['H', 0, 0, 0]
        self.water_xyz[1] = ['H', 0, 1, 1]
        self.assertEqual(self.water_xyz[1], ['H', 0, 1, 1])
        self.water_xyz.insert(1, ['O', 0, 0, 1])
        self.assertEqual(self.water_xyz[1], ['O', 0, 0, 1])
        self.assertEqual(self.water_xyz[2], ['H', 0, 1, 1])
        self.assertEqual(self.water_xyz, Molecule([['H', 0, 0, 0], ['O', 0, 0, 1], ['H', 0, 1, 1]]))

    def test_str(self):
        """Testing __str__"""
        water_xyz_string = """H             0.00000000      0.00000000     10.00000000
O             0.00000000      0.00000000     11.00000000
H             0.00000000     -1.00000000     11.00000000"""
        self.assertEqual(str(self.water_xyz), water_xyz_string)
        water_zmatrix_string = """O
H           1      0.00000000
H           1      1.00000000    2    104.50000000"""
        print(self.water_zmatrix)
        self.assertEqual(str(self.water_zmatrix), water_zmatrix_string)

    def test_check_xyz_atom(self):
        """Test check_xyz_atom throws errors correctly"""
        atom = ['H', 0, 1, 2]
        self.assertTrue(Molecule.check_xyz_atom(atom))
        self.assertRaises(SyntaxError, Molecule.check_xyz_atom, [[]])
        self.assertRaises(SyntaxError, Molecule.check_xyz_atom, [[1, 2, 3]])
        self.assertRaises(SyntaxError, Molecule.check_xyz_atom, [[0, 1, 2, 3]])
        self.assertRaises(SyntaxError, Molecule.check_xyz_atom, [['H', 1, 'a', 3]])

    def test_check_geom(self):
        """Test check_geom throws errors correctly"""
        water_xyz = [['H', 0, 0, 0], ['O', 0, 0, 1], ['H', 0, 1, 1]]
        self.assertTrue(Molecule.check_xyz(water_xyz))
        # Zero-length geometries are valid
        self.assertTrue(Molecule.check_xyz([]))
        self.assertRaises(SyntaxError, Molecule.check_xyz, [[[1, 2, 3]]])
        self.assertRaises(SyntaxError, Molecule.check_xyz, [[[0, 1, 2, 3]]])
        self.assertRaises(SyntaxError, Molecule.check_xyz, [[['H', 1, 'a', 3]]])

    def test_check_zmatrix(self):
        """Test check_zmatrix"""
        self.assertRaises(SyntaxError, Molecule.check_zmatrix, [[]])
        self.assertRaises(SyntaxError, Molecule.check_zmatrix, [['O'], 'H'])
        self.assertRaises(SyntaxError, Molecule.check_zmatrix, [['O'], ['H', 'O', 1]])
        self.assertRaises(SyntaxError, Molecule.check_zmatrix, [['O'], ['H', 1, 1, 2]])
        bad_h2o2 = [['O'], ['H', 1, 0], ['O', 1, 1.5, 2, 109.5], ['H', 4, 1, 2, 109.5, 1, 120]]
        self.assertRaises(SyntaxError, Molecule.check_zmatrix, bad_h2o2)
        # End of errors, begin correct
        self.assertTrue(Molecule.check_zmatrix([]))
        water_zmatrix = [['O'], ['H', 1, 0], ['H', 1, 1, 2, 104.5]]
        self.assertTrue(Molecule.check_zmatrix(water_zmatrix))
        h2o2_zmatrix = [['O'], ['H', 1, 0], ['O', 1, 1.5, 2, 109.5], ['H', 3, 1, 2, 109.5, 1, 120]]
        self.assertTrue(Molecule.check_zmatrix(h2o2_zmatrix))

    def test_read_write_geometry(self):
        """Testing read and write"""
        test_file = 'geom.xyz.tmp'
        self.water_xyz.write(test_file, True)
        mol = Molecule()
        mol.read(test_file)
        mol.name = 'H2O'
        self.assertEqual(mol.geometry, self.water_xyz.geometry)
        mol.write(test_file, style='latex')
        latex_geom = '''\
H2O\\\\
3\\\\
\\begin{verbatim}
H       0.000000      0.000000     10.000000
O       0.000000      0.000000     11.000000
H       0.000000     -1.000000     11.000000
\\end{verbatim}'''
        with open(test_file) as f:
            out_tex = f.read()
        self.assertEqual(latex_geom, out_tex)

        os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
