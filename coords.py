#!/usr/bin/env python

# Script that takes a geometry in zmatrix or cartesian coordinates and converts it to the other

import argparse
from coordinate_converter import CoordinateConverter
from sys import exit

parser = argparse.ArgumentParser( description='Convert coordinates between cartesian and zmatrix.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='geom.xyz' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str )
parser.add_argument( '-t', '--type', help='Type of input geometry', type=str )

args = parser.parse_args()

if not ( args.type == 'xyz' or args.type == 'zmat' ):
	if args.input[-3:] == 'xyz':
		args.type = 'xyz'
	elif args.input[-4:] == 'zmat':
		args.type = 'zmat'
	else:
		print "Please specify a type"
		exit( 1 )

if not args.output:
	if args.type == 'xyz':
		args.output = 'geom.zmat'
	elif args.type == 'zmat':
		args.output = 'geom.xyz'

conv = CoordinateConverter()
if args.type == 'xyz':
	conv.convert_cartesian( args.input, args.output )
elif args.type == 'zmat':
	conv.convert_zmatrix( args.input, args.output )
else:
	print "Invalid type. Please specify either a zmatrix (zmat) or cartesian (xyz) geoetry"
	exit( 1 )
