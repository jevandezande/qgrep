import unittest
from sys import path
path.append('../..')
from gamessifier import Gamessifier
from molecule import Molecule
from basis import Contraction, Basis, BasisSet
import os


class TestGamessifier(unittest.TestCase):
    """Tests the Molecule class"""

    def setUp(self):
        """Set up for every test"""
        self.g = Gamessifier()
        self.formaldehyde_xyz = Molecule([['O', 0, 1.394, 0], ['C', 0, 0, 0], ['H', 0.994, -0.492, 0], ['H', -0.994, -0.492, 0]])

    def test_read_mol(self):
        """Test reading a molecule from a file"""
        tmp_geom_file = 'geom.xyz.tmp'
        self.formaldehyde_xyz.write(tmp_geom_file)
        self.g.read_mol(tmp_geom_file)
        self.assertEqual(str(self.g.mol), str(self.formaldehyde_xyz))

        os.remove(tmp_geom_file)

    def test_read_basis_set(self):
        """Test reading a basis from a file"""
        tmp_basis_file = 'basis.gbs.tmp'
        basis_set = BasisSet()
        basis_set['B'] = Basis('B', [Contraction('S', [0.2, 0.4], [0.3, 0.7])])
        open(tmp_basis_file, 'w').write(basis_set.print('gamess'))
        self.g.read_basis_set(tmp_basis_file)
        self.assertEqual(basis_set, self.g.basis_set)

        os.remove(tmp_basis_file)

    def test_read_ecp(self):
        """Testing reading an ecp file"""
        tmp_ecp_file = 'ecp.dat.tmp'
        ecp = """\
H-ECP NONE
C-ECP GEN   10  2
    3      ----- d-ul potential     -----
      -10.0000000        1    357.3914469
      -60.2990287        2     64.6477389
      -10.4217834        2     16.0960833
O-ECP NONE"""
        open(tmp_ecp_file, 'w').write(ecp)
        self.g.read_ecp(tmp_ecp_file)
        os.remove(tmp_ecp_file)

    def test_write_input(self):
        """Test writing an input to a basis file"""
        tmp_basis_file = 'basis.gbs.tmp'
        basis_set = BasisSet()
        basis_set['H'] = Basis('H', [Contraction('S', [1], [1])])
        basis_set['O'] = Basis('O', [Contraction('S', [1], [1]), Contraction('S', [2], [1])])
        basis_set['C'] = Basis('C', [Contraction('S', [1], [1]), Contraction('SP', [1, 2], [0.4, 0.6], [0.1, 0.9])])
        open(tmp_basis_file, 'w').write(basis_set.print('gamess'))
        tmp_geom_file = 'geom.xyz.tmp'
        self.formaldehyde_xyz.write(tmp_geom_file)
        tmp_ecp_file = 'ecp.dat.tmp'
        ecp = """\
C-ECP GEN   10  2
    3      ----- d-ul potential     -----
      -10.0000000        1    357.3914469
      -60.2990287        2     64.6477389
      -10.4217834        2     16.0960833
O-ECP NONE"""
        open(tmp_ecp_file, 'w').write(ecp)
        tmp_other_file = 'other.dat'
        open(tmp_other_file, 'w').write('Hello\n')

        self.g.read_mol(tmp_geom_file)
        self.g.read_basis_set(tmp_basis_file)
        self.g.read_ecp(tmp_ecp_file)
        self.g.read_other(tmp_other_file)

        tmp_input_file = 'input.inp.tmp'
        self.g.write_input(tmp_input_file)

        os.remove(tmp_geom_file)
        os.remove(tmp_basis_file)
        os.remove(tmp_ecp_file)
        os.remove(tmp_other_file)
        os.remove(tmp_input_file)


