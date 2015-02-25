import unittest
from sys import path
import re

path.insert(0, '../..')

import orca


class TestOrca(unittest.TestCase):
    """Tests the orca class"""

    def setUp(self):
        """Read in the necessary files"""
        files = ['CH3F_Cl_scan.out', 'CH3F_Cl_scan.xyz', 'CH3F_Cl_scan.orca_zmat', 'CH3F_Cl_scan.bohr.xyz',
                 'CH3F_Cl_scan.bohr.orca_zmat', 'CH3F_Cl_scan.check', 'CH3F_Cl_scan.plot', 'CH3F_Cl_scan.zmat',
                 'Benzene_freqs.out', 'Benzene_freqs.freqs', 'H2O_hybrid_hess.out', 'H2O_hybrid_hess.freqs']
        self.files = {}
        for file in files:
            with open(file, 'r') as f:
                self.files[file] = f.readlines()

    def test_get_geom(self):
        """Testing get_geom"""
        self.assertEqual(orca.get_geom(self.files['CH3F_Cl_scan.out'], type='xyz', units='angstrom'),
                         self.files['CH3F_Cl_scan.xyz'])
        self.assertEqual(orca.get_geom(self.files['CH3F_Cl_scan.out'], type='zmat', units='angstrom'),
                         self.files['CH3F_Cl_scan.orca_zmat'])
        self.assertEqual(orca.get_geom(self.files['CH3F_Cl_scan.out'], type='xyz', units='bohr'),
                         self.files['CH3F_Cl_scan.bohr.xyz'])
        self.assertEqual(orca.get_geom(self.files['CH3F_Cl_scan.out'], type='zmat', units='bohr'),
                         self.files['CH3F_Cl_scan.bohr.orca_zmat'])

    def test_check_convergence(self):
        """Testing check_convergence"""
        checklist = orca.check_convergence(self.files['CH3F_Cl_scan.out'])
        self.assertEqual(len(checklist), 74)
        self.assertEqual(checklist[-1], ''.join(self.files['CH3F_Cl_scan.check']))

    def test_get_energy(self):
        """Testing get_energy"""
        energy = orca.get_energy(self.files['CH3F_Cl_scan.out'])
        self.assertEqual('-33.930452726594', energy)
        energy = orca.get_energy(self.files['Benzene_freqs.out'], 'sp')
        self.assertEqual('-232.089449656962', energy)
        energy = orca.get_energy(self.files['Benzene_freqs.out'], 'gibbs')
        self.assertEqual('-232.01547613', energy)
        energy = orca.get_energy(self.files['Benzene_freqs.out'], 'enthalpy')
        self.assertEqual('-231.98366000', energy)
        energy = orca.get_energy(self.files['Benzene_freqs.out'], 'entropy')
        self.assertEqual('-0.03181612', energy)


    def test_get_freqs(self):
        """Testing get_freqs"""
        benzene_freqs = orca.get_freqs(self.files['Benzene_freqs.out'])
        H2O_freqs = orca.get_freqs(self.files['H2O_hybrid_hess.out'])
        self.assertEqual(benzene_freqs, ''.join(self.files['Benzene_freqs.freqs']))
        self.assertEqual(H2O_freqs, ''.join(self.files['H2O_hybrid_hess.freqs']))

    def test_plot(self):
        """Testing plot"""
        geoms = orca.plot(self.files['CH3F_Cl_scan.out'])
        self.assertEqual('\n'.join(geoms), ''.join(self.files['CH3F_Cl_scan.plot']))

    def test_convert_zmatrix(self):
        zmat = orca.convert_zmatrix(self.files['CH3F_Cl_scan.out'], 'angstrom')
        self.assertEqual(['\t'.join(line) + '\n' for line in zmat],
                         self.files['CH3F_Cl_scan.zmat'])

    def test_convert_to_orca_zmatrix(self):
        zmat = self.files['CH3F_Cl_scan.zmat']
        orca_zmat = orca.convert_to_orca_zmatrix(zmat)
        match = [['C', '0', '0', '0', '0', '0', '0'],
                 ['Cl', '1', '0', '0', '3.023917', '0', '0'],
                 ['H', '1', '2', '0', '1.101881', '67.866', '0'],
                 ['H', '1', '2', '3', '1.101892', '67.921', '239.994'],
                 ['H', '1', '2', '3', '1.101887', '67.906', '120.019'],
                 ['F', '1', '2', '3', '1.200000', '179.969', '15.700']]
        self.assertEqual(orca_zmat, match)

    def test_get_molecule(self):
        """Testing get_molecule"""
        molecule = '''\
C            -2.56433400     -0.44012300      0.02117400
Cl            0.45928100     -0.43465300     -0.02124300
H            -2.13859100     -1.22065300      0.67206200
H            -2.16397700     -0.61749900     -0.98997300
H            -2.14677300      0.52045900      0.36334300
F            -3.76420600     -0.44266200      0.03854700'''
        self.assertEqual(molecule, str(orca.get_molecule(self.files['CH3F_Cl_scan.out'])))

if __name__ == '__main__':
    unittest.main()
