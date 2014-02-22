#!/usr/bin/python

# Script that takes an output file and gets the last geometry

import argparse
from check_type import check_type

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz' )
parser.add_argument( '-t', '--type', help='The geometry style', type=str, default='xyz' )

args = parser.parse_args()

# Read in the file
with open( args.input, 'r' ) as f:
	lines = f.readlines()

program = check_type( lines )

if program == 'orca':
	import orca
	geom = orca.get_geom( lines, args.type )
elif program == 'qchem':
	import qchem
	geom = qchem.get_geom( lines )
else:
	print "Not yet supported"

if not args.output == '':
	out = ''
	for line in geom:
		out += '\t'.join( line.split() ) + '\n'

	with open( args.output, 'w' ) as f:
		f.write( out )
