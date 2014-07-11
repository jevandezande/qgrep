# !/usr/bin/env python

import argparse

from helper import read


parser = argparse.ArgumentParser(description='Get the geometry of an output file.')
parser.add_argument('-i', '--input', help='The file to be read.', type=str, default='output.dat')
parser.add_argument('-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz')

args = parser.parse_args()

lines, program = read(args.input)

output = ''
if program == 'orca':
    from orca import get_freqs
    output = get_freqs(lines)
#elif program == 'qchem':
#    from qchem import get_freqs
#    output = get_freqs(lines)
elif program == 'psi4':
    from psi4 import get_freqs
    output = get_freqs(lines)
else:
    print "Not yet supported"

if not args.output == '':
    with open(args.output, 'w') as f:
        f.write(output)
