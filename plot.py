#!/usr/bin/python

# Script that takes an orca output file and outputs the geometries of the individual optimization steps

import argparse
import orca

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz' )
parser.add_argument( '-p', '--program', help='The program that produced the output file.', type=str, default='orca' )
parser.add_argument( '-m', '--multi', help='Indicates that there are muliple different molecules in the molecule', type=bool, default=False )
parser.add_argument( '-t', '--type', help='The geometry style', type=str, default='xyz' )

args = parser.parse_args()

if args.program == 'orca':
	orca.plot( args.input, args.output, args.type )
else:
	print "Not yet supported"
