#!/usr/bin/python

# Script that takes an output file and gets the last geometry

import argparse

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz' )
parser.add_argument( '-p', '--program', help='The program that produced the output file.', type=str, default='orca' )
parser.add_argument( '-t', '--type', help='The geometry style', type=str, default='xyz' )

args = parser.parse_args()

if args.program == 'orca':
	import orca
	orca.get_geom( args.input, args.output, args.type )
else:
	print "Not yet supported"
