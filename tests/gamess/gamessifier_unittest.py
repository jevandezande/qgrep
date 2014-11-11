import unittest
from collections import OrderedDict
from sys import path
path.append('../..')
from gamess import Gamessifier
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

    def test_read_options(self):
        """Testing read options"""
        self.g.read_options({})
        self.assertEqual({}, self.g.options_dict)
        self.assertEqual('', self.g.options_str)
        options_dir = OrderedDict([
            ['CONTRL', OrderedDict([['SCFTYP', 'RHF']])],
            ['SCF', OrderedDict([['DIRSCF', '.TRUE.']])]
        ])
        options_str = ' $CONTRL\n    SCFTYP=RHF\n $END\n\n $SCF\n    DIRSCF=.TRUE.\n $END\n\n'
        self.g.read_options(options_dir)
        self.assertEqual(options_str, self.g.options_str)

        tmp_options_file = 'options.dat.tmp'
        open(tmp_options_file, 'w').write(options_str)
        self.g.read_options(tmp_options_file)

    def test_read_other_data(self):
        """Testing read_other_data"""
        tmp_dat_file = 'dat.tmp'
        vec = ' $VEC\n12 23 31\n33241 32523 11.0\n $END'
        hess = ' $HESS\n32 43 987\n453 443 11.0\n $END'
        data = 'Hey\n' + vec + ' \n random other text\n' + hess + '\n more text\n122\n'
        open(tmp_dat_file, 'w').write(data)
        self.g.read_data(tmp_dat_file)
        self.assertEqual(vec, self.g.vec)
        self.assertEqual(hess, self.g.hess)

        os.remove(tmp_dat_file)

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
        tmp_options_file = 'options.dat.tmp'
        options_str = ' $CONTRL\n    SCFTYP=RHF\n $END\n\n $SCF\n    DIRSCF=.TRUE.\n $END\n\n'
        open(tmp_options_file, 'w').write(options_str)
        tmp_dat_file = 'dat.tmp'
        vec = ' $VEC\n12 23 31\n33241 32523 11.0\n $END'
        hess = ' $HESS\n32 43 987\n453 443 11.0\n $END'
        data = 'Hey\n' + vec + ' \n random other text\n' + hess + '\n more text\n122\n'
        open(tmp_dat_file, 'w').write(data)

        self.g.read(tmp_geom_file, tmp_basis_file, tmp_ecp_file, tmp_options_file, tmp_dat_file)

        tmp_input_file = 'input.inp.tmp'
        self.g.write_input(tmp_input_file)

        os.remove(tmp_geom_file)
        os.remove(tmp_basis_file)
        os.remove(tmp_ecp_file)
        os.remove(tmp_options_file)
        os.remove(tmp_input_file)
        os.remove(tmp_dat_file)


