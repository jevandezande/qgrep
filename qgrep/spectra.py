#!/usr/bin/env python3
import numpy as np

from cclib.io import ccread
from cclib.parser.utils import convertor

from matplotlib import pyplot as plt


def gaussian(energy, intensity, width):
    return lambda x: intensity*np.exp(-(x-energy)**2/(2*width**2))


def gaussian_fast(energy, intensity, width):
    """
    Faster form of a gaussian function
    Cutoff at 6 standard deviations
    """
    def f(x):
        val = abs(x-energy)/width
        if val > 6:
            return 0
        return intensity*np.exp(-val**2/2)
    return f


def lorentzian(energy, intensity, width):
    return lambda x: 1/(2*np.pi) * width / ((x - energy)**2 + width**2/4)


peak_functions = {
    'gaussian' : gaussian_fast,
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
            'bar_width' : (energies[-1] - energies[0])/150,
            'crop': False,
            'crop_thresh': 9,
            'norm' : True,
            'peak_function': 'gaussian',
        }
        self.options.update(options)

    def __repr__(self):
        return '<Spectra {}>'.format(self.name)

    def __sub__(self, other):
        return SpectralDifference(self, other)

    def __add__(self, other):
        """
        First hack at sum of spectra
        TODO: Make separate class akin to SpectralDifference but with more additions?
        """
        return SpectralSum(self.energies, other)

    def plot(self, npoints=10001, fwhh=1):
        """
        Plots the transitions
        :param npoints: the number of points to use in the expansion
        :param fwhh: the width of the gaussian
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
        # check to make sure there are enough points for the fwhh
        if  val_range > npoints*fwhh:
            raise Exception('Cannot properly plot the spectra, increase the ' +
                            'peak width or the number of points')

        xs = np.linspace(low, high, npoints)
        ys = np.zeros(npoints)

        # generate all values
        for i, x in enumerate(xs):
            for peak in peaks:
                ys[i] += peak(x)

        # set max to 1
        max_int = max(ys)
        if self.options['norm']:
            intensities = intensities/max_int
            ys = ys/max_int
            max_int = 1
        if self.options['crop']:
            # TODO: fix problem with x space vs point space, may need to do a backconversion
            crop_val = 10**-self.options['crop_thresh']*max_int

            start_point, end_point = np.argmax(ys > crop_val), - np.argmax(ys[::-1] > crop_val)
            xs, ys = xs[start:end + 1], ys[start:end + 1]

            start_e, end_e = np.argmax(energies > start), np.argmax(energies > end) - 1
            val_range = energies[end_e] - energies[start_e]
            energies = energies[start:end + 1]
            intensities = intensities[start:end + 1]

        # switch to KeV
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,3))

        # Plot
        plt.axhline(0, color='black')

        plt.plot(xs, ys, 'b-', label=self.name)
        plt.bar(energies, intensities, self.options['bar_width'], color='r')
        plt.legend()


class CombinedSpectra:

    def __init__(self, spectra1, spectra2):
        """
        Combination of two spectra, either a sum or a difference

        :param spectra1, spectra2: Spectra objects
        """
        self.options = spectra1.options.copy()
        self.spectra1, self.spectra2 = spectra1, spectra2

    def __repr__(self):
        return '<CombinedSpectra {} : {}>'.format(self.spectra1.name, self.spectra2.name)

    def plot(self, npoints=10001, fwhh=1):
        """
        Plot the difference of two spectra on top of the spectras
        of the individual spectra, with the second flipped
        TODO: deal with conflicting option values
        TODO: make better
        """
        spectra1, spectra2 = self.spectra1, self.spectra2
        es1, ints1 = spectra1.energies, spectra1.intensities
        es2, ints2 = spectra2.energies, spectra2.intensities
        # K1, L1 = 6764.83
        # K1, M1 = 7563
        # L23, M23 =  701

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
        if  val_range > npoints*fwhh:
            raise Exception('Cannot properly plot the spectra, increase the ' +
                            'peak width or the number of points')

        xs = np.linspace(low, high, npoints)
        ys1 = np.zeros(npoints)
        ys2 = np.zeros(npoints)

        # generate all values
        for i, x in enumerate(xs):
            for peak1, peak2 in zip(peaks1, peaks2):
                ys1[i] += peak1(x)
                ys2[i] += peak2(x)

        if isinstance(self, SpectralDifference):
            combo = ys1 - ys2
        elif isinstance(self, SpectralSum):
            combo = ys1 + ys2
        else:
            raise SyntaxError('Must be a sum or difference of spectra.')

        # set max to 1
        if self.options['norm']:
            co_norm = True
            if co_norm:
                max_int = max(max(ys1), max(ys2), max(combo))
                ints1 = ints1 / max_int
                ys1 = ys1 / max_int
                ints2 = ints2 / max_int
                ys2 = ys2 / max_int
                combo = combo / max_int
            else:
                ints1 = ints1 / max(ys1)
                ys1 = ys1 / max(ys1)
                ints2 = ints2 / max(ys2)
                ys2 = ys2 / max(ys2)
                combo = ys1 - ys2

        # Flip if a difference
        if isinstance(self, SpectralDifference):
            ys2 = -ys2
            ints2 = -ints2


        # switch to KeV
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,3))

        # Plot
        plt.axhline(0, color='black')

        plt.plot(xs, ys1, 'b-', label=spectra1.name)
        plt.plot(xs, ys2, 'g-', label=spectra2.name)

        plt.plot(xs, combo, 'y-', label='Δ')
        plt.bar(es1, ints1, self.options['bar_width'], color='r')
        plt.bar(es2, ints2, self.options['bar_width'], color='r')
        plt.legend()


class SpectralDifference(CombinedSpectra):
    def __repr__(self):
        return '<SpectralDifference {} - {}>'.format(self.spectra1.name, self.spectra2.name)


class SpectralSum(CombinedSpectra):
    def __repr__(self):
        return '<SpectralSum {} + {}>'.format(self.spectra1.name, self.spectra2.name)


def gen_spectra(file_name, name, thresh=9):
    data = ccread(file_name)
    energies, intensities = convertor(data.etenergies, 'cm-1', 'eV'), data.etoscs
    #intensities = abs(intensities)

    print(len(energies))
    #energies, intensities = energies[intensities > 10**-thresh], intensities[intensities > 10**-thresh]
    #print(len(energies))
    #energies, intensities = energies[intensities > 10**-8], intensities[intensities > 10**-8]
    #print(len(energies))
    #energies, intensities = energies[intensities > 10**-7], intensities[intensities > 10**-7]
    #print(len(energies))
    #energies, intensities = energies[intensities > 10**-6], intensities[intensities > 10**-6]
    #print(len(energies))
    #energies, intensities = energies[intensities > 10**-5], intensities[intensities > 10**-5]
    #print(len(energies))
    #energies, intensities = energies[energies < 3*10**4], intensities[energies < 3*10**4]
    #print(len(energies))

    s = Spectra(energies, intensities, name)
    return s
