#!/usr/bin/python

# Script that takes an output file and gets the last geometry

import argparse
from check_type import check_type

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str, default='ZMAT' )
parser.add_argument( '-u', '--units', help='What units to output the geometry in.', type=str, default='angstrom' )

args = parser.parse_args()

# Read in the file
with open( args.input, 'r' ) as f:
	lines = f.readlines()

program = check_type( lines )

if program == 'orca':
	import orca
	zmat = orca.convert_zmatrix( lines, args.units )
else:
	print "Not yet supported"

with open( args.output, 'w' ) as f:
	for line in zmat:
		f.write( '\t'.join( line ) + '\n' )
