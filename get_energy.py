#!/usr/bin/python

# Script that takes an output file and gets the last geometry

import argparse
from check_type import check_type

parser = argparse.ArgumentParser( description='Get the final energy of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )

args = parser.parse_args()

# Read in the file
with open( args.input, 'r' ) as f:
	lines = f.readlines()

program = check_type( lines )

energy = 0

if program == 'orca':
	from orca import get_energy
	energy = get_energy( lines )
#elif program == 'qchem':
#	from qchem import get_energy
#	geom = get_energy( lines )
#elif program == 'psi4':
#	from psi4 import get_energy
#	geom = get_energy( lines )
else:
	print "Not yet supported"

if not energy == 0:
	print energy
else:
	print "No energy found"
