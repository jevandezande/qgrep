#!/usr/bin/python

# Script that takes an output file and prints all of its geometry convergence results

import argparse
from helper import read

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-n', '--number', help='The number of steps to be output', type=int, default=0)

args = parser.parse_args()

lines, program = read( args.input )

convergence_list = []
if program == 'orca':
	from orca import checklist_convergence
	convergence_list = checklist_convergence( lines )
elif program == 'qchem':
	from qchem import checklist_convergence
	convergence_list = checklist_convergence( lines )
elif program == 'psi4':
	from psi4 import checklist_convergence
	convergence_list = checklist_convergence( lines )
else:
	print "Not yet supported"

if args.number > 0 and args.number < len(convergence_list):
	for i in range(len(convergence_list)-args.number,len(convergence_list) ):
		print convergence_list[i]
else:
	for i in convergence_list:
		print i

print 'Optimization Steps: {0}'.format(len(convergence_list))

