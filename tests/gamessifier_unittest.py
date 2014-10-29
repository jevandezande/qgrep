import unittest
from sys import path
path.append('../..')
from gamessifier import Gamessifier
from molecule import Molecule
import os


class TestMolecule(unittest.TestCase):
    """Tests the Molecule class"""

    def setUp(self):
        """Set up for every test"""
        self.g = Gamessifier()
        self.water_xyz = Molecule([['H', 0, 0, 0], ['O', 0, 0, 1], ['H', 0, 1, 1]])

    def test_read_mol(self):
        """Test reading a molecule from a file"""
        tmp_geom_file = 'geom.xyz.tmp'
        self.water_xyz.write(tmp_geom_file)
        self.g.read_mol(tmp_geom_file)
        self.assertEqual(self.g.mol, self.water_xyz)

        os.remove(tmp_geom_file)

    def test_read_basis(self, basis_file):
        tmp_basis_file = 'basis.gbs.tmp'

