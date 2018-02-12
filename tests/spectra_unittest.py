import unittest
import numpy as np

from sys import path
from numpy.testing import assert_array_almost_equal as aaa_equal

path.insert(0, '..')

from qgrep.spectra import CombinedSpectra, Spectra


class Spectra(unittest.TestCase):
    """Tests the Spectra class"""
    def setUp(self):
        pass

    def test_len(self):
        """Test __len__"""
        pass


class CombinedSpectra(unittest.TestCase):
    """Tests the CombinedSpectra class"""
    def setUp(self):
        pass

    def test_len(self):
        """Test __len__"""
        pass


if __name__ == '__main__':
    unittest.main()
