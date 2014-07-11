# !/usr/bin/env python

# Script that takes an output file and returns the orbital energies

import argparse

from helper import read


parser = argparse.ArgumentParser(description='Get the final energy of an output file.')
parser.add_argument('-i', '--input', help='The file to be read.', type=str, default='output.dat')
parser.add_argument('-o', '--output', help='Where to output the orbital energies', type=str, default='energies.dat')

args = parser.parse_args()

lines, program = read(args.input)

levels = []
if program == 'orca':
    from orca import energy_levels
    levels, info = energy_levels(lines)
#elif program == 'qchem':
#    from qchem import energy_levels
#    levels = energy_levels(lines)
#elif program == 'psi4':
#    from psi4 import energy_levels
#    levels = energy_levels(lines)
else:
    print "Not yet supported"

with open(args.output, 'w') as f:
    for level in levels:
        f.write(level)

for item in info:
    print '{0}:\t{1}'.format(item, info[item])
