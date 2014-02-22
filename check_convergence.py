#!/usr/bin/python

# Script that takes an output file and prints its last geometry convergence results

import argparse

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-p', '--program', help='The program that produced the output file.', type=str, default='orca' )

args = parser.parse_args()

if args.program == 'orca':
	import orca
	print orca.check_convergence( args.input )
else:
	print "Not yet supported"

