import unittest
from sys import path
import numpy as np
from numpy.testing import assert_almost_equal
path.insert(0, '../../')
from qgrep.population.orbital_pop import OrbitalPopulation as OP, MOrbital, AO_Contrib, Group_Contrib


class TestReducedOrbPop(unittest.TestCase):

    def test_read(self):
        rop = OP('h2o.dat')
        ao_contrib = AO_Contrib(1, 'O', 'px', 100.0)
        orb = MOrbital()
        self.assertEqual(rop.orb_list[4].contributions[0], ao_contrib)

        c1 = AO_Contrib(0, 'H', 's', 19.6)
        c2 = AO_Contrib(1, 'O', 'pz', 30.4)
        c3 = AO_Contrib(1, 'O', 'py', 30.4)
        c4 = AO_Contrib(2, 'H', 's', 19.6)
        contributions = [c1, c2, c3, c4]
        mo = MOrbital(2, -0.49905, 2, contributions)
        self.assertEqual(rop[2], mo)

    def test_homo_lumo_somo(self):
        rop = OP('h2o.dat')
        self.assertEqual(rop.homo, 4)
        self.assertEqual(rop.lumo, 5)
        self.assertEqual(rop.somo, [])
        
    def test_atom_contract(self):
        rop = OP('h2o.dat')
        atom_contract = rop.atom_contract()
        self.assertEqual(atom_contract[5].contributions[0].val, 34.1)
        self.assertEqual(atom_contract[8].contributions[1].val, 11.5)
        
    def test_am_contract(self):
        rop = OP('h2o.dat')
        am_contract = rop.am_contract()
        self.assertEqual(am_contract[5].contributions[0].val, 34.1)
        self.assertEqual(am_contract[8].contributions[2].val,  9.8)


class TestOrbital(unittest.TestCase):
    def test_Orbital(self):
        orb1 = MOrbital()
        orb1_dup = MOrbital()
        self.assertTrue(orb1 == orb1_dup)

        ao_contrib1 = AO_Contrib(1, 'Mn', 'px', 0.3)
        ao_contrib1_dup = AO_Contrib(1, 'Mn', 'px', 0.3)
        ao_contrib2 = AO_Contrib(2, 'O', 'f-1', 0.5)
        ao_contrib3 = AO_Contrib(2, 'O', 'f+2', 0.2)
        orb2 = MOrbital(1, -0.34, 1.00, [ao_contrib1, ao_contrib2, ao_contrib3])
        self.assertFalse(orb1 == orb2)

        self.assertEqual(orb2.atom_sum(2), 0.7)
        self.assertEqual(orb2.atom_sum('F'), 0.0)

        self.assertEqual(orb2.orbital_type_sum(1, 'd'), 0)
        self.assertEqual(orb2.orbital_type_sum(9, 'p'), 0)
        self.assertEqual(orb2.orbital_type_sum(2, 'f'), 0.7)


class TestAO_Contrib(unittest.TestCase):
    def test_AO_Contrib(self):
        ao_contrib1 = AO_Contrib(1, 'Mn', 'px', 0.3)
        ao_contrib1_dup = AO_Contrib(1, 'Mn', 'px', 0.3)
        ao_contrib2 = AO_Contrib(2, 'O', 'f-1', 0.5)
        ao_contrib3 = AO_Contrib(2, 'O', 'f+2', 0.2)
        
        self.assertTrue(ao_contrib1 == ao_contrib1_dup)
        self.assertFalse(ao_contrib1 == ao_contrib2)


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
