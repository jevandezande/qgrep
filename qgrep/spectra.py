#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt
from cclib import ccopen


def gaussian(energy, intensity, width):
    return lambda x: intensity*np.exp(-(x-energy)**2/(2*width**2))


def lorentzian(energy, intensity, width):
    pass


peak_functions = {
    'gaussian' : gaussian,
    'lorentzian' : lorentzian,
}


class Spectra:
    """
    Class for plotting arbitrary spectra
    """
    def __init__(self, energies, intensities, name, **options):
        """
        :param intensities: list of transition energies
        :param energies: list of transition intensities
        """
        self.energies = energies
        self.intensities = intensities
        self.name = name

        self.options = {
            'bar_width' : (energies[-1] - energies[0])/400,
            'norm' : True,
            'peak_function': 'gaussian',
        }
        self.options.update(options)

    def __sub__(self, other):
        return SpectralDifference(self, other)

    def plot(self, npoints=1001, fwhh=1000):
        """
        Plots the transitions
        """
        energies, intensities = self.energies, self.intensities

        # Make all of the peak functions functions
        peak_function = peak_functions[self.options['peak_function']]

        peaks = []
        for energy, intensity in zip(energies, intensities):
            peaks.append(peak_function(energy, intensity, fwhh))

        # Add a little before and after the first and last vals
        val_range = energies[-1] - energies[0]
        low, high = energies[0] - val_range/10, energies[-1] + val_range/10
        xs = np.linspace(low, high, npoints)
        ys = np.zeros(npoints)

        # generate all values
        for i, x in enumerate(xs):
            for peak in peaks:
                ys[i] += peak(x)

        # set max to 1
        if self.options['norm']:
            intensities = intensities/max(ys)
            ys = ys/max(ys)

        plt.plot(xs, ys, 'b-', label=self.name)
        plt.bar(energies, intensities, self.options['bar_width'], color='r')
        plt.legend()


class SpectralDifference:
    def __init__(self, spectra1, spectra2):
        self.options = spectra1.options.copy()
        self.spectra1, self.spectra2 = spectra1, spectra2

    def plot(self, npoints=1001, fwhh=1000):
        """
        Plot the difference of two spectra on top of the spectras
        of the individual spectra, with the second flipped
        TODO: deal with conflicting option values
        TODO: make better
        """
        spectra1, spectra2 = self.spectra1, self.spectra2
        es1, ints1 = spectra1.energies, spectra1.intensities
        es2, ints2 = spectra2.energies, spectra2.intensities

        # Make all of the peak functions functions
        peak_function = peak_functions[self.options['peak_function']]

        peaks1, peaks2 = [], []
        for (e1, e2), (int1, int2) in zip(zip(es1, es2), zip(ints1, ints2)):
            peaks1.append(peak_function(e1, int1, fwhh))
            peaks2.append(peak_function(e2, int2, fwhh))

        # Add a little before and after the first and last vals
        low, high = min(es1[0], es2[0]), max(es1[-1], es2[-1])
        val_range = high - low
        low, high = low - val_range/10, high + val_range/10
        xs = np.linspace(low, high, npoints)
        ys1 = np.zeros(npoints)
        ys2 = np.zeros(npoints)

        # generate all values
        for i, x in enumerate(xs):
            for peak1, peak2 in zip(peaks1, peaks2):
                ys1[i] += peak1(x)
                ys2[i] += peak2(x)

        diff = ys1 - ys2

        # set max to 1
        if self.options['norm']:
            max_int = max(max(ys1), max(ys2))
            ints1 = ints1 / max_int
            ys1 = ys1 / max_int
            ints2 = ints2 / max_int
            ys2 = ys2 / max_int
            diff = diff / max_int

        plt.plot(xs, ys1, 'b-', label=spectra1.name)
        plt.plot(xs,-ys2, 'g-', label=spectra2.name)
        plt.plot(xs, diff, 'y-', label='Δ')
        plt.bar(es1, ints1, self.options['bar_width'], color='r')
        plt.bar(es2,-ints2, self.options['bar_width'], color='r')
        plt.legend()


def gen_spectra(file_name, name):
    data = ccopen(file_name).parse()
    s = Spectra(data.etenergies, data.etoscs, name)
    return s
