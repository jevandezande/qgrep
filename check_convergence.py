#!/usr/bin/python

# Script that takes an output file and prints its last geometry convergence results

import argparse

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-p', '--program', help='The program that produced the output file.', type=str, default='orca' )

args = parser.parse_args()

with open( args.input ) as f:
	lines = f.readlines()

if args.program == 'orca':
<<<<<<< HEAD
	print orca.check_convergence( lines )
=======
	import orca
	print orca.check_convergence( args.input )
>>>>>>> a329a6aa5284d7dc7440aef07f099d24ee7b8d1b
else:
	print "Not yet supported"

