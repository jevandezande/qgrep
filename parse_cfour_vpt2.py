#!/usr/bin/env python3
import sys

import more_itertools as mit
import numpy as np


def read(file):
    while next(file) != 'PARAMETERS RELEVANT TO MOLECULAR STRUCTURE':
        continue

    file.jump(5)
    line = next(file)
    values = []
    while line != 'AAA FCUBIC --------------------':
        if line != 'AAA FCUBIC bef trafo --------------------':
            _, num, _, value = line.split()
        line = next(file)

    """
 i                      1  j                      1  k    1.00000000000000
  fcubic:   0.000000000000000E+000
"""
    line = next(file)
    while line != 'Special treatment for modes:':
        _, i, _, j, _, k = line.split()
        i, j, k, = int(i), int(j), int(float(k))
        fcubic = float(next(file).split()[-1])
        line = next(file)

    """
 Special treatment for modes:
                    13                    14
"""
    while line != "Cubic force constants written to file cubic.":
        line = next(file)
        i, j = line.split()
        line = next(file)

    """
 AAA constants  0.695038424430000        219474.631371000
   29979245800.0000       0.000000000000000E+000  1.054571596000000E-027
  5.291771888732910E-009  0.000000000000000E+000
    """
    while line:
        line.split()
        line = next(file)

    """
---------------------------------------------------------------------------
  Mean and mean-square displacements in dimensionless normal coordinates

             Geometrical properties evaluated at     0.00 K

         Coordinate              <q>            <q**2>
---------------------------------------------------------------------------
 AAA Q2AVG ----  mode                      7  T-prefact    1.00000000000000
  conv factor    60.1996854688284       omega    1675.75588591928      Q2avg
  0.000000000000000E+000
 AAA conversion to dimensionless coords
 AAA  0.000000000000000E+000   60.1996854688284        1675.75588591928
 AAA tmp2 of icoord  0.499999988943207
"""
    file.jump(3)
    temperature = float(next(file).split()[-2])
    file.jump(3)
    while file.peek().split()[0] == 'AAA':
        _, _, _, _, mode, _, t_prefact = next(file).split()
        _, _, conv_factor, _, omega, _ = next(file).split()
        q2avg = float(next(file))
        next(file)
        _, a, b, c = next(file).split()
        tmp2_icoord = next(file).split()[-1]

#    """
# J J I                     7                     7                     7  cubic
# -4.014716146043627E-012  factor   1.796194958187608E-002
# J J I                     1                     1                     7  cubic
# -9.238060067674107E-003  factor   0.000000000000000E+000
#"""
#    while file.peek() != 'AAA':
#        _, _, _, i, j, k, _ = next(file).split()
#        cubic, _, factor = next(file).split()


    while next(file) != 'C A L C U L A T I O N  OF  V I B R A T I O N A L L Y':
        continue
    file.jump(3)

    """
======================================================================
       C A L C U L A T I O N  OF  V I B R A T I O N A L L Y
             A V E R A G E D  NMR  S H I E L D I N G S
======================================================================

  Atom number   1

   Coordinate            d sigma /dQ         d2 sigma/dQ2
  nuse is                      9
       1                   0.00000             16.96617
       2                   0.00000             16.96733
       3                   0.00000             16.96731
       4                   0.00044              2.34711
       5                   0.00000              2.34711
       6                  50.98729            -12.41176
       7                   0.00000            -13.16114
       8                   0.00000            -13.16430
       9                   0.00000            -13.16432

   Shielding tensor at reference geometry (in ppm):

                   Bx          By          Bz
           Mx  236.181264    0.000000    0.000000
           My    0.000000  236.181264    0.000000
           Mz    0.000000    0.000000  236.181264

    Isotropic shielding at reference geometry (ppm):        236.181
    Anisotropic shielding at reference geometry (ppm):        0.000
    Eigenvalues of tensor (in ppm)            :   236.181   236.181   236.181


    Vibrational correction (in ppm):                         -1.206

   Vibrationally averaged shielding tensor (in ppm):

                   Bx          By          Bz
           Mx  234.975455    0.000000    0.000000
           My    0.000000  234.975452    0.000000
           Mz    0.000000    0.000000  234.975461

    Vibrationally averaged isotropic shielding (ppm):       234.975
    Vibationally averaged anisotropic shielding (ppm):        0.000
    Eigenvalues of vibr. averaged tensor (ppm):   234.975   234.975   234.975
"""
    results = []
    while file.peek()[:11] == 'Atom number':
        atom_number = next(file).split()[-1]
        file.jump(2)
        nuse = int(next(file).split()[-1])
        derivs = read_matrix(file, shape=(nuse, 2), header=0, label=1)

        file.jump(3)
        ref_geom_shielding_tensor = read_matrix(file, shape=(3, 3))
        next(file)
        isotropic_shielding = float(next(file).split()[-1])
        anisotropic_shielding = float(next(file).split()[-1])
        x, y, z = map(float, next(file).split()[-3:])
        file.jump(2)
        vib_correction = float(next(file).split()[-1])

        file.jump(3)
        vib_correct_shielding_tensor = read_matrix(file, shape=(3, 3))
        next(file)
        isotropic_shielding = float(next(file).split()[-1])
        anisotropic_shielding = float(next(file).split()[-1])
        x, y, z = map(float, next(file).split()[-3:])
        results.append([atom_number, derivs, ref_geom_shielding_tensor, vib_correct_shielding_tensor])
        next(file)

    #for atom, derivs, ref, vib in results:
    #    print(f"Atom #{atom}")
    #    print(derivs)
    #    print(ref)
    #    print(vib)
    #    print()

    while next(file) != 'ATOM              INTERNUCLEAR DISTANCE / Angstrom':
        continue

    """
  ------------------------------------------------------
   ATOM              INTERNUCLEAR DISTANCE / Angstrom
  -------------------------------------------------------
  I    J           Re           Rg           Ra
  ------------------------------------------------------
  2    1         1.0830104    1.0984020    1.0921827
  3    1         1.0830104    1.0984020    1.0921827
"""
    line = file.jump(4)
    while line[:10] != '-'*10:
        i, j, re, rg, ra = line.split()
        line = next(file)

    """
********************************************************************************
     PARAMETERS RELEVANT TO ROTATIONAL SPECTROSCOPY
********************************************************************************


  ----------------------------------------------------------------------------
                                     VIB-ROT CONSTANT / (cm-1)
                                  ------------------------------
     AXIS        MODE       CORIOLIS     QUADRATIC     ANHARMONIC    TOTAL
  ----------------------------------------------------------------------------
       1           7       0.0361886     -0.0100770   -0.0238668    0.0022448
       1           8       0.1849831      0.0000000   -0.0141547    0.1708284
       """
    line = file.jump(11)
    while line[:10] != '-'*10:
        axis, mode, coriolis, quadratic, anharmonic, total = line.split()
        line = next(file)

    """
  ----------------------------------------------------------------------------
   Be, B0 AND B-B0 SHIFTS FOR SINGLY EXCITED VIBRATIONAL STATES (CM-1)
   ------------------------------------------------------------
  VIBRATION            X AXIS               Y AXIS                 Z AXIS
  ----------------------------------------------------------------------------
    Be                    5.34782835           5.34782835           5.34782835
    B0                    5.29993647           5.29993647           5.29993647
    """
    line = file.jump(8)
    while line[:10] != '-'*10:
        vibration, x, y, z = line.split()
        line = next(file)

    """
  ----------------------------------------------------------------------------
   Be, B0 AND B-B0 SHIFTS FOR SINGLY EXCITED VIBRATIONAL STATES (MHz)
  VIBRATION            X AXIS               Y AXIS                 Z AXIS
  ----------------------------------------------------------------------------
    Be               160323.86074702      160323.86074787      160323.86074744
    B0               158888.09829073      158888.09829160      158888.09829143
    """
    line = file.jump(5)
    while line[:10] != '-'*10:
        vibration, x, y, z = line.split()
        line = next(file)

    """
                 Vibrationally averaged dipole moment
------------------------------------------------------------------------
                  a.u.                         Debye
         x         y         z              x         y         z
------------------------------------------------------------------------
MU_e  0.00000   0.00000   0.00000        0.00000   0.00000   0.00000
<MU> -0.00000  -0.00000  -0.00000       -0.00000  -0.00000  -0.00000

Equilibrium dipole moment:    0.00000 a.u. (   0.00000 D)
Equilibrium dipole moment:    0.00000 a.u. (   0.00000 D)
    """
    line = file.jump(5)
    _, x_au, y_au, z_au, x_debye, y_debye, y_debye = next(file).split()
    _, x_au, y_au, z_au, x_debye, y_debye, y_debye = next(file).split()
    next(file)
    _, _, _, dipol_au, _, _, dipole_debye, _ = next(file).split()
    _, _, _, dipol_au, _, _, dipole_debye, _ = next(file).split()


    """
  Performing F(IIJJ)/F(JJII) consistency check
  Differences greater than 1 cm-1 will be printed.
  ==============================================================
  I    I    K    K       F(IIKK)       F(KKII)       Difference
  --------------------------------------------------------------
  --------------------------------------------------------------
  Largest absolute difference is    0.01754 cm-1.
  Largest relative difference is .26238D-03.
VPT2 vibrational analysis
    """
    line = file.jump(12)
    while line[:10] != '-'*10:
        i, _, k, _, f_iikk, f_kkii, diff = line.split()
        line = next(file)
    max_abs_diff = float(next(file).split()[-2])
    rel_abs_diff = float(next(file).split()[-1][:-1].replace('D', 'E'))

    """
--------------------------------------------------------------------------------
    Checking for potential third-rank (Fermi) resonances
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
  I  J  K     PHI(I,J,K)     DELTA(W_s)   DIFF(DIAG-VPT2)  Splitting by
                                                           Diagonalization
--------------------------------------------------------------------------------
 12  7  7  -218.24682410   174.40313983     1.40665806    15.66287273
 12  8  8  -218.24682410   174.40313980     1.40665806    15.66287273
    """
    line = file.jump(10)
    while line[:10] != '-'*10:
        i, j, k, phi_ijk, delta_w_s, diff_diag_vpt2, splitting = line.split()
        line = next(file)

    """
  ANHARMONICITY CONSTANTS X(ij)
                   (cm-1)
-------------------------------
  (*) Near-zero denominators were removed
-------------------------------
          I  J          X(IJ)
-------------------------------
           7  7       -6.2917
           7  8       -1.1545
    """
    line = file.jump(10)
    while line:
        i, j, x_ij = line.split()
        line = next(file)

    """
--------------------------------------------------------------------------------
          HARMONIC AND FUNDAMENTAL FREQUENCIES (cm-1) AND INTENSITIES (km/mol)
--------------------------------------------------------------------------------

         Harmonic     Fundamental Anharmonic    Harmonic   Fundamental  Anharm
  Mode   Frequency    Frequency   Contribution  Intensity  Intensity    Contrib
    7   1675.7559   1663.9432      -11.8127      0.0000       0.0000      0.0000
    8   1675.7559   1663.9430      -11.8129      0.0000       0.0000      0.0000
    """
    line = file.jump(7)
    while line[:10] != '-'*10:
        mode, harm, fund, anh_contrib, harm_i, fund_i, anh_contrib_i = line.split()
        line = next(file)

    """
--------------------------------------------------------------------------------
                         ZERO-POINT VIBRATIONAL ENERGIES
--------------------------------------------------------------------------------
                            kcal/mol      kJ/mol        Hartree        cm-1
--------------------------------------------------------------------------------
Harmonic contribution :       33.9101     141.8799      0.05403927     11860.250
VPT2-correction       :       -0.2652      -1.1097     -0.00042267       -92.765
--------------------------------------------------------------------------------
Harm+VPT2             :       33.6449     140.7702      0.05361660     11767.485
--------------------------------------------------------------------------------
  maxlevel                      5
 ------------------------------------------------------------------------------
    """
    line = file.jump(6)
    _, _, _, harm_kcal, harm_kj, harm_hartree, harm_cm = line.split()
    _, _, diff_kcal, diff_kj, diff_hartree, diff_cm = next(file).split()
    next(file)
    _, _, comb_kcal, comb_kj, comb_hartree, comb_cm = next(file).split()
    next(file)
    maxlevel = int(next(file).split()[-1])

    """
                   All levels with up to five quanta
--------------------------------------------------------------------------------
  MODE MODE MODE MODE MODE                   Anharmonic    Anharm      Harmonic
   I    J    K    L    M   NI  NJ  NK  NL  NM Frequency   Intensity   Transition
--------------------------------------------------------------------------------
    8    0    0    0    0  1   0   0   0   0  1663.942    0.000000   1675.755886
    9    0    0    0    0  1   0   0   0   0  1663.943    0.000000   1675.755886
    7    0    0    0    0  1   0   0   0   0  1663.943    0.000000   1675.755886
   10    0    0    0    0  1   0   0   0   0  1886.514    0.000000   1903.718758
    """
    line = file.jump(7)
    while line[:10] != '-'*10:
        i, j, k, l, m, ni, nj, nk, nl, nm, anharm_freq, anharm_int, harmonic = line.split()
        line = next(file)


def read_matrix(file, shape=(3, 3), header=1, label=1, diagonal=False, symmetric=False):
    """
    Reads a matrix

    :param file: MyIter of a file starting on the first line of a matrix
    :param shape: the shape of the matrix
    :param header: number of lines of header at the top of the matrix
    :param label: number of columns of labels
    :param diagonal: should the matrix be diagonal (raises ValueError if not)
    :param symmetric: should the matrix be symmetric (raises ValueError if not)

    e.g.
                   Bx          By          Bz
           Mx  236.181264    0.000000    0.000000
           My    0.000000  236.181264    0.000000
           Mz    0.000000    0.000000  236.181264
    """
    file.jump(header)

    matrix = np.zeros(shape)
    for i, line in zip(range(shape[0]), file):
        # jump first item if a label
        matrix[i] = line.split()[label:]

    if diagonal and not np.allclose(matrix, np.diag(np.diagonal(matrix))):
        raise ValueError('Non-diagonal matrix read in.')
    elif symmetric and not np.allclose(matrix, matrix.T):
        raise ValueError('Non-symmetric matrix read in.')

    return matrix

def print_matrix(matrix, header=None, labels=None, column_width='10.5'):
    """
    Print a Matrix
    """
    out = ''
    if header is not None:
        out += (f'{{:^{column_width}}} '*len(line)).format(*line).strip() + '\n'

    if labels is not None:
        for label, vals in zip(labels, matrix):
            out += f'{{:^{column_width}}} '.format(label)
            out += (f'{{:>{column_width}f}} '*len(vals)).format(*vals).strip() + '\n'
    else:
        for vals in matrix:
            out += (f'{{:> {column_width}f}} '*len(vals)).format(*vals).strip() + '\n'
    print(out)


class MyIter(mit.peekable):
    """
    A few hack on iterable to be more user friendly for parsing files

    Changes:
    Strips lines before yielding iterator
    Keeps track of line number in file
    """
    def __init__(self, iterable):
        super().__init__(iterable)
        self.position = 0
        self.current_line = ''

    def __next__(self):
        self.position += 1
        self.current_line = super().__next__().strip()
        return self.current_line

    def jump(self, num):
        """
        Jump forward the specified number of elements in the iterator
        :return: the line n-steps forward
        """
        for _ in range(num-1):
            next(self)
        if num > 0:
            return next(self)

    def peek(self):
        return super().peek().strip()


if __name__ == '__main__':
    out_file = sys.argv[1]if len(sys.argv) > 1 else 'output.dat'
    out_file = '/home/vandezande/tmp/zeus/vib/cfour/sto-3g/CH4/output.dat'
    with open(out_file) as file:
        myiter = MyIter(file)
        try:
            read(myiter)
        except Exception as e:
            print(f'Iterator on line: {myiter.position}\n{myiter.current_line}\n')
            raise e
