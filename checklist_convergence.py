#!/usr/bin/python

# Script that takes an output file and prints all of its geometry convergence results

import argparse
from check_type import check_type

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )

args = parser.parse_args()

with open( args.input, 'r' ) as f:
	lines = f.readlines()

args = parser.parse_args()

program = check_type( lines )

convergence_list = []
if program == 'orca':
	import orca
	convergence_list = orca.checklist_convergence( lines )
elif program == 'qchem':
	import qchem
	convergence_list = qchem.checklist_convergence( lines )
elif program == 'psi4':
	import psi4
	convergence_list = psi4.checklist_convergence( lines )
else:
	print "Not yet supported"

for i in convergence_list:
	print i

