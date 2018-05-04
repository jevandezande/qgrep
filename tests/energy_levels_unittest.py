import unittest
import numpy as np

from sys import path
from numpy.testing import assert_array_almost_equal as aaa_equal

path.insert(0, '..')

from qgrep.energy_levels import read_energy_levels


class EnergyLevels(unittest.TestCase):
    def test_read_energy_levels(self):
        levels, homos = read_energy_levels('orca/H2O_hybrid_hess.out', 'eV')
        print(levels)
        orbs = [-520.02709244, -26.6515108, -14.03756442, -9.86790946, -7.8383211, 1.14181693,
                3.3152991, 15.49399938, 17.86340352, 25.16813657, 25.50144882, 29.48546771,
                32.01141895, 70.07769761, 70.51667167, 71.32400626, 79.69918077, 83.61895358]
        aaa_equal(levels[0], orbs)


if __name__ == '__main__':
    unittest.main()
