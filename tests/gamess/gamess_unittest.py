import unittest

from sys import path

path.insert(0, '../..')

from qgrep import gamess


class TestGamess(unittest.TestCase):
    """Tests the gamess module"""

    def setUp(self):
        """Read in the necessary files"""
        files = ['CH2_opt.out', 'CH2_opt.check']
        self.files = {}
        for file in files:
            with open(file, 'r') as f:
                self.files[file] = f.readlines()

    def test_check_convergence(self):
        """Testing check_convergence"""
        checklist = gamess.check_convergence(self.files['CH2_opt.out'])
        self.assertEqual(len(checklist), 6)
        self.assertEqual('\n'.join(checklist), ''.join(self.files['CH2_opt.check']).strip())

if __name__ == '__main__':
    unittest.main()
