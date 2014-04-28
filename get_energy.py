#!/usr/bin/python

# Script that takes an output file and gets the last geometry

import argparse
from check_type import check_type

parser = argparse.ArgumentParser( description='Get the final energy of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-t', '--energy_type', help='Ouput the specified type of energy', type=str, default='sp' )

args = parser.parse_args()

# Read in the file
with open( args.input, 'r' ) as f:
	lines = f.readlines()

program = check_type( lines )

if program == 'orca':
	from orca import get_energy
	energy = get_energy( lines, args.energy_type )
#elif program == 'qchem':
#	from qchem import get_energy
#	geom = get_energy( lines )
#elif program == 'psi4':
#	from psi4 import get_energy
#	geom = get_energy( lines )
else:
	print "Not yet supported"

print energy
