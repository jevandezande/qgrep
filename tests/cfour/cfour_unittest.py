import unittest

from sys import path

path.insert(0, '../..')

from qgrep import cfour


class TestCFour(unittest.TestCase):
    """Tests the cfour class"""

    def setUp(self):
        """Read in the necessary files"""
        files = ['h2o.out', 'h2o.xyz']
        self.files = {}
        for file in files:
            with open(file, 'r') as f:
                self.files[file] = f.readlines()

    def test_get_geom(self):
        """Testing get_geom"""
        h2o_xyz = cfour.get_geom(self.files['h2o.out'], geom_type='xyz')
        self.assertEqual(self.files['h2o.xyz'], h2o_xyz)

    def test_check_convergence(self):
        """Testing check_convergence"""
        raise NotImplementedError

    def test_get_energy(self):
        """Testing get_energy"""
        raise NotImplementedError

    def test_get_freqs(self):
        """Testing get_freqs"""
        raise NotImplementedError

    def test_plot(self):
        """Testing plot"""
        raise NotImplementedError

    def test_convert_zmatrix(self):
        """Test convert_zmatrix"""
        raise NotImplementedError

    def test_get_molecule(self):
        """Testing get_molecule"""
        raise NotImplementedError


if __name__ == '__main__':
    unittest.main()
    h2o_xyz = cfour.get_geom(open('h2o.out').readlines(), geom_type='xyz')
    print(h2o_xyz)
