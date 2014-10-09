#!/usr/bin/env python3

# Script that takes an output file and prints all of its geometry convergence results

import argparse
import importlib

from helper import read


parser = argparse.ArgumentParser(description='Get the geometry of an output file.')
parser.add_argument('-i', '--input', help='The file to be read.', type=str, default='output.dat')
parser.add_argument('-n', '--number', help='The number of steps to be output', type=int, default=0)

args = parser.parse_args()

lines, program = read(args.input)

if program:
    try:
        mod = importlib.import_module(program)
        if hasattr(mod, 'check_convergence'):
            mod.check_convergence(lines)
            # Print the last number of convergence results (even works for too big numbers)
            print('\n'.join(convergence_list[-args.number:])
            print('Optimization Steps:' + len(convergence_list))
        else:
            print(program + ' does not yet have check_convergence implemented.')
    except ImportError:
        print(program + ' is not yet supported.')
else:
    print('Cannot determine what program made this output file.')
