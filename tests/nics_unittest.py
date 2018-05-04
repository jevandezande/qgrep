import unittest
import numpy as np

from sys import path
from numpy.testing import assert_array_almost_equal as aaa_equal

path.insert(0, '..')

from qgrep.nics import nics_points


class NICS(unittest.TestCase):
    def test_nics_points(self):
        water = """3
comment
H   0   0   0
O   0   0   1
H   0   1   1
"""
        benzene = """6
comment
C     0    0.0    1.4
C     0    1.2    0.7
C     0    1.2   -0.7
C     0    0.0   -1.4
C     0   -1.2   -0.7
C     0   -1.2    0.7
"""
        cubane = """6
comment
C   0.0   0.0   0.0
C   0.0   0.0   1.4
C   0.0   1.4   0.0
C   0.0   1.4   1.4
C   1.4   0.0   0.0
C   1.4   0.0   1.4
C   1.4   1.4   0.0
C   1.4   1.4   1.4
"""

        assert nics_points(water) == []
        aaa_equal([(0, 0, 0), (-1, 0, 0), (1, 0, 0)], nics_points(benzene))
        cubane_points = nics_points(cubane)
        assert len(cubane_points) == 6
        aaa_equal(cubane_points, [
            ( 0.7,  0.0, 0.7),
            ( 0.7, -1.0, 0.7),
            ( 0.7,  1.0, 0.7),
            ( 0.0,  0.7, 0.7),
            (-1.0,  0.7, 0.7),
            ( 1.0,  0.7, 0.7),
        ])


if __name__ == '__main__':
    unittest.main()
