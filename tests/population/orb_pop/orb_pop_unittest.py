import unittest
from sys import path
import os
import numpy as np
from numpy.testing import assert_almost_equal
path.insert(0, '../../../')
from qgrep.population.orbital_pop import OrbitalPopulation as OP, MOrbital, AO_Contrib, Group_Contrib


class TestOrbPop(unittest.TestCase):

    def test_read_write(self):
        op = OP('H2O.dat')
        ao_contrib = AO_Contrib(1, 'O', 'px', 100.0)
        self.assertEqual(op.orb_list[4].contributions[0], ao_contrib)

        c1 = AO_Contrib(0, 'H', 's', 19.6)
        c2 = AO_Contrib(1, 'O', 'pz', 30.4)
        c3 = AO_Contrib(1, 'O', 'py', 30.4)
        c4 = AO_Contrib(2, 'H', 's', 19.6)
        contributions = [c1, c2, c3, c4]
        mo = MOrbital(2, None, -0.49905, 2, contributions)
        self.assertEqual(op[2], mo)

        op.write('tmp.csv', 'csv')
        op_dup = OP('tmp.csv')
        self.assertEqual(op, op_dup)
        os.remove('tmp.csv')

        # Test UKS open shell
        op = OP('H2O+.dat')
        ao_contrib = AO_Contrib(1, 'O', 'px', 100.0, 1)
        self.assertEqual(op.orb_list[3].contributions[0], ao_contrib)

    def test_homo_lumo_somo(self):
        op = OP('H2O.dat')
        self.assertEqual(op.homo, 4)
        self.assertEqual(op.lumo, 5)
        self.assertEqual(op.somo, [])

    def test_atom_contract(self):
        op = OP('H2O.dat')
        atom_contract = op.atom_contract()
        self.assertEqual(atom_contract[5].contributions[0].val, 34.1)
        self.assertEqual(atom_contract[8].contributions[1].val, 11.5)

    def test_am_contract(self):
        op = OP('H2O.dat')
        am_contract = op.am_contract()
        self.assertEqual(am_contract[5].contributions[0].val, 34.1)
        self.assertEqual(am_contract[8].contributions[2].val,  9.8)

    def test_sub(self):
        # Blank - Blank == Blank
        self.assertEqual(OP() - OP(), OP())

        # A - Blank == A
        h2o = OP('H2O.dat')
        # Uses blank list of properly indexed orbitals
        blank = OP(orb_list=[MOrbital(i, None, 0, 0, []) for i in range(13)])
        self.assertEqual(h2o - blank, h2o)

        # A - B
        h2s = OP('H2S.dat')
        # TODO: fix indexing problem for subtraction
        #(h2o.atom_contract() - h2s.atom_contract()).write('h2o_h2s.csv')


class TestOrbital(unittest.TestCase):
    def setUp(self):
        self.orb1 = MOrbital()
        self.orb1_dup = MOrbital()

        self.aoc1 = AO_Contrib(1, 'Mn', 'px', 0.3)
        self.aoc1_dup = AO_Contrib(1, 'Mn', 'px', 0.3)
        self.aoc2 = AO_Contrib(2, 'O', 'f-1', 0.5)
        self.aoc3 = AO_Contrib(2, 'O', 'f+2', 0.2)
        self.orb2 = MOrbital(1, None, -0.34, 1.00, [self.aoc1, self.aoc2, self.aoc3])
        self.orb3 = MOrbital(1, None, -0.14, 0.50, [self.aoc2, self.aoc1, self.aoc3])

    def test_init(self):
        self.assertTrue(self.orb1 == self.orb1_dup)
        self.assertFalse(self.orb1 == self.orb2)

        self.assertEqual(self.orb2.atom_sum(2), 0.7)
        self.assertEqual(self.orb2.atom_sum('F'), 0.0)

        self.assertEqual(self.orb2.orbital_type_sum(1, 'd'), 0)
        self.assertEqual(self.orb2.orbital_type_sum(9, 'p'), 0)
        self.assertEqual(self.orb2.orbital_type_sum(2, 'f'), 0.7)

    def test_sub(self):
        # Blank - Blank == Blank
        self.assertEqual(self.orb1 - self.orb1_dup, self.orb1)

        # A - Blank == A
        self.assertEqual((self.orb2 - self.orb1).contributions, self.orb2.contributions)

        # A - B
        aoc_1_2 = self.aoc1 - self.aoc2
        aoc_2_1 = self.aoc2 - self.aoc1
        aoc_3_3 = self.aoc3 - self.aoc3
        orb_2_3 = MOrbital(1, None, -0.20, 0.50, [aoc_1_2, aoc_2_1, aoc_3_3])
        self.assertEqual((self.orb2 - self.orb3).contributions, orb_2_3.contributions)


class TestAO_Contrib(unittest.TestCase):
    def setUp(self):
        self.aoc1 = AO_Contrib(1, 'Mn', 'px', 0.3)
        self.aoc1_dup = AO_Contrib(1, 'Mn', 'px', 0.3)
        self.aoc2 = AO_Contrib(2, 'O', 'f-1', 0.5)
        self.aoc3 = AO_Contrib(2, 'O', 'f+2', 0.2)

    def test_init(self):
        self.assertTrue(self.aoc1 == self.aoc1_dup)
        self.assertFalse(self.aoc1 == self.aoc2)

    def test_sub(self):
        # A - A = O contribution
        aoc0 = AO_Contrib(1, 'Mn', 'px', 0.0)
        self.assertEqual(self.aoc1 - self.aoc1_dup, aoc0)
        aoc_1_2 = AO_Contrib(0, '', '',  -0.2)
        self.assertEqual(self.aoc1 - self.aoc2, aoc_1_2)


class TestGroup_Contrib(unittest.TestCase):
    def test_Group_Contrib(self):
        group_contrib1 = Group_Contrib(1, ['Mn', 'Br'], 0.3)
        group_contrib1_dup = Group_Contrib(1, ['Mn', 'Br'], 0.3)
        group_contrib2 = Group_Contrib(2, [], 0.5)
        group_contrib3 = Group_Contrib(2, ['Mn', 'Cs', 'Mo'], 0.2)

        self.assertTrue(group_contrib1 == group_contrib1_dup)
        self.assertFalse(group_contrib1 == group_contrib2)

if __name__ == '__main__':
    unittest.main()
