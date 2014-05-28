#!/usr/bin/python

# Script that takes an output file and writes a proper zmatrix or the reverse if already proper

import argparse
from helper import read

parser = argparse.ArgumentParser( description='Converts the last zmatrix to a proper zmatrix or the reverse if already proper.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str, default='ZMAT' )
parser.add_argument( '-u', '--units', help='What units to output the geometry in.', type=str, default='angstrom' )

args = parser.parse_args()

# Read in the file
lines, program = read( args.input )

zmat = ''
if program == 'orca':
	import orca
	zmat = orca.convert_zmatrix( lines, args.units )
elif program == None:
	# If already a proper zmatrix, convert to orca style
	import orca
	# Skip the first two line if they are a header
	if lines[0] == '#ZMATRIX\n':
		lines = lines[2:]
	zmat = orca.convert_to_orca_zmatrix( lines )
else:
	print "Not yet supported"

with open( args.output, 'w' ) as f:
	for line in zmat:
		f.write( '\t'.join( line ) + '\n' )
