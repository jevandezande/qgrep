#!/usr/bin/env python3

# Script that takes an output file and outputs the geometries of the individual optimization steps

import argparse
import importlib

from qgrep.helper import read

parser = argparse.ArgumentParser(description='Get the geometry of an output file.')
parser.add_argument('-i', '--input', help='The file to be read.', type=str, default='output.dat')
parser.add_argument('-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz')
parser.add_argument('-t', '--type', help='The geometry style', type=str, default='xyz')

args = parser.parse_args()

lines, program = read(args.input)

if program:
    try:
        mod = importlib.import_module('qgrep.' + program)
        if hasattr(mod, 'plot'):
            geoms = mod.plot(lines, args.type)
            with open(args.output, 'w') as f:
                f.write('\n'.join(geoms))
        else:
            print(program + ' does not yet have plot implemented.')
    except ImportError:
        print(program + ' is not yet supported.')
else:
    print('Cannot determine what program made this output file.')

