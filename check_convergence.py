#!/usr/bin/python

# Script that takes an output file and prints its last geometry convergence results

import argparse
from helper import read

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )

args = parser.parse_args()

lines, program = read( args.input )

if program == 'orca':
	import orca
	print orca.check_convergence( lines )
elif program == 'qchem':
	import qchem
	print qchem.check_convergence( lines )
elif program == 'psi4':
	import psi4
	print psi4.check_convergence( lines )
else:
	print "Not yet supported"

