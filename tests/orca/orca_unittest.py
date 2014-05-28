import unittest
from glob import glob
from sys import path
path.append('../..')

import orca

class TestOrca( unittest.TestCase ):
	'''Tests the orca class'''
	def setUp( self ):
		'''Read in the necessary files'''
		files = [ 'CH3F_Cl_scan.out', 'CH3F_Cl_scan.xyz', 'CH3F_Cl_scan.zmat', 'CH3F_Cl_scan.bohr.xyz', 'CH3F_Cl_scan.bohr.zmat', 'CH3F_Cl_scan.plot' ]
		self.files = {}
		for file in files:
			with open( file, 'r' ) as f:
				self.files[file] = f.readlines()

	def test_get_geom( self ):
		'''Testing get_geom'''
		self.assertEqual( orca.get_geom( self.files['CH3F_Cl_scan.out'], type='xyz', units='angstrom' ), self.files['CH3F_Cl_scan.xyz'] )
		self.assertEqual( orca.get_geom( self.files['CH3F_Cl_scan.out'], type='zmat', units='angstrom' ), self.files['CH3F_Cl_scan.zmat'] )
		self.assertEqual( orca.get_geom( self.files['CH3F_Cl_scan.out'], type='xyz', units='bohr' ), self.files['CH3F_Cl_scan.bohr.xyz'] )
		self.assertEqual( orca.get_geom( self.files['CH3F_Cl_scan.out'], type='zmat', units='bohr' ), self.files['CH3F_Cl_scan.bohr.zmat'] )

		

if __name__ == '__main__':
	unittest.main()
