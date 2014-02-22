#!/usr/bin/python

# Script that takes an output file and prints its last geometry convergence results

import argparse
import orca

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-p', '--program', help='The program that produced the output file.', type=str, default='orca' )

args = parser.parse_args()

with open( args.input ) as f:
	lines = f.readlines()

if args.program == 'orca':
	print orca.check_convergence( lines )
else:
	print "Not yet supported"

