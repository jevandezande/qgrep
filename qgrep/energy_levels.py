#!/usr/bin/env python3

# Script that takes an output file and returns the orbital energies
import numpy as np

from cclib import ccopen
from cclib.parser.utils import convertor
import matplotlib.pyplot as plt


def read_energy_levels(input_file, units='eV'):
    """
    Determines the energy levels and homos from and output file
    :param input_file: input file to read
    :param units: units to return energies in
    """
    try:
        data = ccopen(input_file).parse()
        levels = np.array(data.moenergies)
        if units != 'eV':
            try:
                levels = convertor(levels, 'eV', units)
            except KeyError as e:
                raise KeyError(f'Cannot convert energy levels to {units}')
    except AttributeError as e:
        raise Exception('Cannot find appropriate data, has the SCF finished yet?')
    return levels, data.homos


def energy_levels(input_file, units='eV', verbose=True, write=None):
    """
    Determines the energy levels and homos from and output file
    :param input_file: input file to read
    :param units: units to return energies in
    """
    levels, homos = read_energy_levels(input_file, units)

    if levels.shape[0] == 1:
        i = homos[0]
        homo = levels[0][i]
        lumo = levels[0][i+1]

        out = f"""\
  eV  │ Index │   Energy  │
──────┼───────┼───────────┤
 LUMO │  {i+1:>3}  │ {lumo:>9.5f} │
 HOMO │  {i:>3}  │ {homo:>9.5f} │
──────┼───────┼───────────┤
 GAP  │       │ {lumo-homo:>9.5f} │
"""
    else:
        ia, ib = homos[0], homos[1]
        ha, hb = levels[0][ia], levels[1][ib]
        la, lb = levels[0][ia+1], levels[1][ib+1]
        spin_flip = min(la - hb, lb - ha)

        out = f"""\
  eV   │  α   β  │  α Energy  β Energy │
───────┼─────────┼─────────────────────┤
 LUMOS │ {ia+1:>3} {ib+1:>3} │ {la:>9.5f} {lb:>9.5f} │
 HOMOS │ {ia:>3} {ib:>3} │ {ha:>9.5f} {hb:>9.5f} │    Spin-Flip Gap
───────┼─────────┼─────────────────────┤    ─────────────
 GAPS  │         │ {la-ha:>9.5f} {lb-hb:>9.5f} │       {spin_flip:^8.5f}
"""
    if verbose:
        print(out)

    if write:
        levels = levels.T
        np.savetxt(write, levels, fmt='%7.5f')

    return levels, homos


def density_of_states(input_file, units='eV', bins=50, window=(-100, 100)):
    """
    Plot the density of states
    :param input_file: input file to read
    :param units: units to plot energies in
    :param bins: number of bins to use for the histogram
    :param window: window in which to plot energies
    """
    lower, upper = window
    levels, homos = read_energy_levels(input_file, units)
    occ, virt = np.array([]), np.array([])
    for spin, homo in zip(levels, homos):
        o, v = spin[:homo + 1], spin[homo + 1:]
        occ = np.append(occ, o[lower < o & o < upper])
        virt = np.append(virt, v[lower < v & v < upper])

    plt.hist([occ, virt], bins=bins)
    plt.show()
