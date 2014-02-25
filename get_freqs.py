#!/usr/bin/python

import argparse
from check_type import check_type

parser = argparse.ArgumentParser( description='Get the geometry of an output file.' )
parser.add_argument( '-i', '--input', help='The file to be read.', type=str, default='output.dat' )
parser.add_argument( '-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz' )
parser.add_argument( '-p', '--program', help='The program that produced the output file.', type=str, default='orca' )


args = parser.parse_args()

with open( args.input ) as f: #args.input ) as f:
	lines = f.readlines()

program = check_type( lines )

if program == 'orca':
	from orca import get_freqs
	output = get_freqs( lines )
#elif program == 'qchem':
#	from qchem import get_freqs
#	geom = get_freqs( lines )
#elif program == 'psi4':
#	from psi4 import get_freqs
#	geom = get_freqs( lines )
else:
	print "Not yet supported"

if not args.output == '':
	with open( args.output, 'w' ) as f:
		f.write( output )
