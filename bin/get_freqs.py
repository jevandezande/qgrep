#!/usr/bin/env python3

import argparse
import importlib

from helper import read


parser = argparse.ArgumentParser(description='Get the geometry of an output file.')
parser.add_argument('-i', '--input', help='The file to be read.', type=str, default='output.dat')
parser.add_argument('-o', '--output', help='Where to output the geometry.', type=str, default='geom.xyz')

args = parser.parse_args()

lines, program = read(args.input)

if program:
    try:
        mod = importlib.import_module(program)
        if hasattr(mod, 'get_freqs'):
            with open(args.output, 'w') as f:
                f.write(mod.get_freqs(lines))
        else:
            print(program + ' does not yet have get_freqs implemented.')
    except ImportError:
        print(program + ' is not yet supported.')
else:
    print('Cannot determine what program made this output file.')
