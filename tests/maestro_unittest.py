import unittest

from sys import path

path.insert(0, '..')

from qgrep import maestro


class TestMaestro(unittest.TestCase):
    def test_read_smoketest(self):
        maestro.read_mae("geom.mae")


if __name__ == "__main__":
    unittest.main()
