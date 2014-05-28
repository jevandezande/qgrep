#!/usr/bin/python

# Script that takes an orca output file and outputs the geometries of the individual optimization steps

import argparse
from helper import read

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz' )
parser.add_argument( '-t', '--type', help='The geometry style', type=str, default='xyz' )

args = parser.parse_args()

lines, program = read( args.input )

geoms = []
if program == 'orca':
	import orca
	geoms = orca.plot( lines, args.type )
elif program == 'qchem':
	import qchem
	geoms = qchem.plot( lines )
elif program == 'psi4':
	import psi4
	geoms = psi4.plot( lines )
else:
	print "Not yet supported"

if not args.output == '':
	with open( args.output, 'w' ) as f:
		f.write( '\n'.join(geoms) )
