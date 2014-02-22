#!/usr/bin/python

# Script that takes an orca output file and outputs the geometries of the individual optimization steps

import argparse
from check_type import check_type

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz' )
parser.add_argument( '-m', '--multi', help='Indicates that there are muliple different molecules in the molecule', type=bool, default=False )
parser.add_argument( '-t', '--type', help='The geometry style', type=str, default='xyz' )

args = parser.parse_args()

with open( args.input ) as f:
	lines = f.readlines()

program = check_type( lines )

geoms = []
if program == 'orca':
	import orca
	geoms = orca.plot( lines, args.type )
elif program == 'qchem':
	import qchem
	geoms = qchem.plot( lines )
else:
	print "Not yet supported"

if not args.output == '':
	with open( args.output, 'w' ) as f:
		f.write( '\n'.join(geoms) )
