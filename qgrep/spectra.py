#!/usr/bin/env python3
import abc
import numpy as np

from cclib.io import ccread
from cclib.parser.utils import convertor

from matplotlib import pyplot as plt


class Peak:
    """
    A spectral peak
    """
    def __init__(self, energy, intensity, width):
        self.energy = energy
        self.intensity = intensity
        self.width = width

    def __repr__(self):
        return f"<{type(self).__name__} {energy}:{intensity}:{width}>"

    def __str__(self):
        return repr(self)

    @abc.abstractmethod
    def __call__(self, x):
        """ Return the intensity at point x """
        pass


class Gaussian(Peak):
    def __call__(self, x):
        return self.intensity*np.exp(-(x-self.energy)**2/(2*self.width**2))


class Gaussian_fast(Peak):
    """
    Faster form of a gaussian function with a cutoff at 6 standard deviations
    """
    def __call__(self, x):
        val = abs(x-self.energy)/self.width
        if val > 6:
            return 0
        return self.intensity*np.exp(-val**2/2)


def Lorentzian(Peak):
    def __call__(self, x):
        return 1/(2*np.pi) * self.width / ((x - self.energy)**2 + self.width**2/4)


peak_functions = {
    'gaussian': Gaussian_fast,
    'lorentzian': Lorentzian,
}


class Spectra:
    """
    Class for plotting arbitrary spectra
    """
    def __init__(self, energies, intensities, name, **options):
        """
        :param intensities: list of transition energies
        :param energies: list of transition intensities
        :param name: name of spectra
        """
        self.energies = energies
        self.intensities = intensities
        self.name = name

        self.options = {
            'bar_width': (energies[-1] - energies[0])/150,
            'peak_function': 'gaussian',
        }
        self.options.update(options)

    def __repr__(self):
        return f'<Spectra {self.name}>'

    def __str__(self):
        return repr(self)

    def __sub__(self, other):
        return SpectralDifference(self, other)

    def __add__(self, other):
        return SpectralSum(self, other)

    def spectral_values(self, npoints=10001, fwhh=1):
        """
        Generate the values needed for `plot()`
        :return: xs, ys (line of spectra), bar_xs, bar_ys (sticks plots)
        """
        energies, intensities = self.energies, self.intensities

        # Make all of the peak functions functions
        pf = peak_functions[self.options['peak_function']]
        peaks = []
        for energy, intensity in zip(energies, intensities):
            if intensity > 0:
                peaks.append(pf(energy, intensity, fwhh))

        val_range = energies[-1] - energies[0]
        # Add a little before and after the first and last vals
        low, high = energies[0] - val_range/10, energies[-1] + val_range/10
        if val_range > npoints*fwhh:
            raise Exception('Cannot properly plot the spectra, ' +
                            'increase the peak width (fwhh) or the number of points (npoints).')

        xs = np.linspace(low, high, npoints)
        ys = np.zeros(npoints)

        # generate all values
        for i, x in enumerate(xs):
            for peak in peaks:
                ys[i] += peak(x)

        return xs, ys, energies, intensities

    def plot(self, npoints=10001, fwhh=1):
        """
        Plots the transitions
        :param npoints: the number of points to use in the expansion
        :param fwhh: the width of the gaussian
        """
        xs, ys, bar_xs, bar_ys = self.spectral_values(npoints, fwhh)

        # switch to KeV
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 3))

        # Plot
        plt.axhline(0, color='black')

        plt.plot(xs, ys, 'b-', label=self.name)
        plt.bar(bar_xs, bar_ys, self.options['bar_width'], color='r')
        plt.legend()


class CombinedSpectra:
    def __init__(self, spectra1, spectra2):
        """
        Combination of two spectra, either a sum or a difference

        :params spectra1, spectra2: Spectra objects
        """
        # Check if options match
        for key1, val1 in spectra1.options.items():
            if key1 not in spectra2.options:
                print(f'Conflicting options, {key1} not in spectra2.options.')
            if val1 != spectra2.options[key1]:
                print(f'Conflicting options, ' +
                      f'spectra1.options[{key1}]: {val1} != ' +
                      f'spectra2.options[{key1}]: {spectra2.options[key1]}, '
                       'using spectra1.options.')

        self.options = spectra1.options.copy()
        self.spectra1, self.spectra2 = spectra1, spectra2

    def __repr__(self):
        return f'<CombinedSpectra {self.spectra1.name} : {self.spectra2.name}>'

    def plot(self, npoints=1001, fwhh=1):
        """
        Plot the difference of two spectra on top of the spectras
        of the individual spectra, with the second flipped
        TODO: deal with conflicting option values
        TODO: currently broken if xs do not align!!!
        """
        sp1, sp2 = self.spectra1, self.spectra2

        # TODO: remove this hack
        # Force the energies to have the same range
        if sp1.energies[0] < sp2.energies[0]:
            sp2.energies = np.insert(sp2.energies, 0, sp1.energies[0])
            sp2.intensities = np.insert(sp2.intensities, 0, 0)
        elif sp1.energies[0] > sp2.energies[0]:
            sp1.energies = np.insert(sp1.energies, 0, sp2.energies[0])
            sp1.intensities = np.insert(sp1.intensities, 0, 0)

        if sp1.energies[-1] < sp2.energies[-1]:
            sp1.energies = np.append(sp1.energies, sp2.energies[-1])
            sp1.intensities = np.append(sp1.intensities, 0)
        elif sp1.energies[-1] > sp2.energies[-1]:
            sp2.energies = np.append(sp2.energies, sp1.energies[-1])
            sp2.intensities = np.append(sp2.intensities, 0)

        xs1, ys1, bar_xs1, bar_ys1 = sp1.spectral_values(npoints, fwhh)
        xs2, ys2, bar_xs2, bar_ys2 = sp2.spectral_values(npoints, fwhh)

        if isinstance(self, SpectralSum):
            combo = ys1 + ys2
        elif isinstance(self, SpectralDifference):
            combo = ys1 - ys2
            # Flip second spectra if a difference
            ys2 = -ys2
            bar_ys2 = -bar_ys2

        # set max to 1
        #if self.options['norm']:
        #    co_norm = True
        #    if co_norm:
        #        max_int = max(max(ys1), max(ys2), max(combo))
        #        ints1 = ints1 / max_int
        #        ys1 = ys1 / max_int
        #        ints2 = ints2 / max_int
        #        ys2 = ys2 / max_int
        #        combo = combo / max_int
        #    else:
        #        ints1 = ints1 / max(ys1)
        #        ys1 = ys1 / max(ys1)
        #        ints2 = ints2 / max(ys2)
        #        ys2 = ys2 / max(ys2)
        #        combo = ys1 - ys2

        # switch to KeV
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 3))

        # Plot
        plt.axhline(0, color='black')

        plt.plot(xs1, ys1, 'b-', label=self.spectra1.name)
        plt.plot(xs2, ys2, 'g-', label=self.spectra2.name)

        if isinstance(self, (SpectralSum, SpectralDifference)):
            plt.plot(xs1, combo, 'y-', label='Δ')
        plt.bar(bar_xs1, bar_ys1, self.options['bar_width'], color='b')
        plt.bar(bar_xs2, bar_ys2, self.options['bar_width'], color='g')
        plt.legend()


class SpectralDifference(CombinedSpectra):
    def __repr__(self):
        return f'<SpectralDifference {self.spectra1.name} - {self.spectra2.name}>'


class SpectralSum(CombinedSpectra):
    def __repr__(self):
        return f'<SpectralSum {self.spectra1.name} + {self.spectra2.name}>'


def gen_spectra(file_name, name, units='eV', thresh=9):
    data = ccread(file_name)
    energies, intensities = convertor(data.etenergies, 'cm-1', units), data.etoscs
    #intensities = abs(intensities)

    #print(len(energies))
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
