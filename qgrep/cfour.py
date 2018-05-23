import re
import math

from .helper import BOHR_TO_ANGSTROM


def get_geom(lines, geom_type='xyz', units='bohr'):
    """
    Takes the lines of an cfour output file and returns its last geometry in
    the specified format
    :param lines: lines of a cfour output file
    :param geom_type: style of geometry to return
    :param units: units for the coordinates
    """
    if geom_type == 'xyz' and units.lower() in ['bohr', 'angstrom']:
        start = ' Z-matrix   Atomic            Coordinates (in bohr)'
    else:
        print("Invalid format")
        return ''

    geom_start = -1
    # Iterate backwards until the start of the last set of coordinates is found
    for i, line in enumerate(reversed(lines)):
        if start == line[:51]:
            geom_start = len(lines) - i + 2
            break
    if geom_start == -1:
        print("Could not find start of geometry")
        return ''

    geom_end = -1
    for i, line in enumerate(lines[geom_start:]):
        if line[:65] == ' ' + '-'*64:
            geom_end = geom_start + i
            break
    if geom_end == -1:
        print("Could not find end of geometry")
        return ''

    # Remove the atomic number
    geom = []
    for line in lines[geom_start: geom_end]:
        atom, an, *xyz = line.split()
        x, y, z = map(lambda x: float(x) * BOHR_TO_ANGSTROM, xyz)
        geom.append(f'{atom:s}\t{x}\t{y}\t{z}\n')

    return geom


def plot(lines, geom_type='xyz', units='angstrom'):
    """
    All geometry steps
    :param lines: lines of a cfour output file
    :param geom_type: style of geometry to return
    :param units: units for the coordinates
    """
    if geom_type == 'xyz' and units in ['bohr', 'angstrom']:
        start = ' Z-matrix   Atomic            Coordinates (in bohr)\n'
    else:
        print("Invalid format")
        return ''
    end = ' ----------------------------------------------------------------\n'

    geoms = []
    step = 0
    for i, line in enumerate(lines):
        if line == start:
            step += 1
            geom = ''
            geom_start = i+3
            for j, line2 in enumerate(lines[geom_start:], start=geom_start):
                if line2 == end:
                    geoms.append(f'{j - geom_start}\nStep {step}\n' + geom)
                    break
                atom, an, *xyz = line2.split()
                if units == 'angstrom':
                    x, y, z = map(lambda x: float(x)*BOHR_TO_ANGSTROM, xyz)
                    geom += f'{atom:<2s} {x:> 15.8f} {y:> 15.8f} {z:> 15.8f}\n'
                else:
                    geom += f'{atom:<2s} {x:>11} {y:>11s} {z:>11s}\n'
    return geoms


def check_convergence(lines):
    """
    Returns all the geometry convergence results
    :param lines: lines of a cfour output file
    """
    target = 'Minimum force:'
    return [line.strip() for line in lines if target in line]


def get_ir(lines):
    """
    Returns all the frequencies and geometries in xyz format.
    :param lines: lines of a cfour output file
    """
    geom = get_geom(lines)
    num_atoms = len(geom)
    version = 1
    if '/opt/cfour/2.0' in lines[1]:
        version = 2
    vibrations_start = 0
    vib_modes_start = 0
    vib_modes_end = 0
    vib_freqs_start = 0
    vib_freqs_end = 0
    hybrid_hessian_vib_modes_end = 0
    for i in reversed(list(range(len(lines)))):
        line = lines[i]
        if version == 1:
            if 'Gradient vector in normal coordinate representation' in line:
                vib_modes_end = i - 1
            elif 'Normal Coordinates' in line:
                vib_modes_start = i + 2
            elif 'Zero-point vibrational energy' in line:
                    vib_freqs_end = i - 1
            elif 'Cartesian force constants:' in line:
                if num_atoms == 2:
                    vib_freqs_start = i  # + 1 + 5 # The + 6 is to exclude the 0.000 cm^-1 freqs
                else:
                    vib_freqs_start = i  # + 1 + 6 # The + 6 is to exclude the 0.000 cm^-1 freqs
                break
        else:
            if 'Gradient vector in normal coordinate representation' in line:
                vib_modes_end = i - 1
            elif 'Normal Coordinates' in line:
                vib_modes_start = i + 2
            elif 'Zero-point energy' in line:
                    vib_freqs_end = i - 1
            elif 'Cartesian force constants:' in line:
                if num_atoms == 2:
                    vib_freqs_start = i
                else:
                    vib_freqs_start = i
                break

    freqs = []
    for line in lines[vib_freqs_start: vib_freqs_end + 1]:
        if '0.0' not in line.split()[1]:
            freqs.append(line.split()[1])

    freqs.reverse()

    return freqs


def get_theo_method(lines):
    """ Get the level of correlation and basis set for the computation. """
    for line in lines:
        if 'ICLLVL' in lines:
            theory = line.split()[2]
        if 'IBASIS' in line:
            basis = line.split()[2]
        if 'IREFNC' in line:
            reference = line.split()[2]

    return theory, basis, reference


def get_charge(lines):
    """ Searches through file and finds the charge of the molecule. """
    for line in lines:
        if 'ICHRGE' in line:
            return line.split()[2]

    return None


def get_multiplicity(lines):
    """ Searches through file and finds the charge of the molecule. """
    for line in lines:
        if 'IMULTP' in line:
            return line.split()[2]

    return None


def get_conv_params(lines):
    """ Finds the convergence criterion for SCF, CC, and Geometry. """
    for line in lines:
        if 'ISCFCV' in line:
            scf_conv = line.split()[3]
        if 'ICCCNV' in line:
            cc_conv = line.split()[3]
        if 'ICONTL' in line:
            geo_conv = line.split()[2]
        if 'IZTACN' in line:
            lineq_conv = line.split()[3]
        if 'Integrals less than' in line:
            int_thresh = line.split()[3]

    return scf_conv, cc_conv, geo_conv, lineq_conv, int_thresh


def get_diagnostics(lines):
    """ Gets the S^2 and T1 and T2 diagnostics. """
    s2 = maxT2 = t1a = t1b = t1 = 0.0
    end = case = caset1 = Nbeta = Nalpha = Ncore = 0

    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        if 'The expectation value of S**2 is' in line:
            s2 = line.split()[6]

        if 'Largest T2 amplitudes for spin case' in line:
            maxT = 0
            case = case + 1
            if not case > 3:
                if 'Largest T2 amplitudes for spin case AB' in line:
                    for a in range(15):
                        if 'Norm of T2' in lines[i+a]:
                            end = a - 1
                            break
                    for a in range(i+4, i+end):
                        c = re.findall(r'\]\s?-?\d.\d*', lines[a])
                        for j in range(3):
                            maxT = max(abs(float(b[j][1:])), maxT)
                else:
                    for a in range(10):
                        if 'Norm of T2' in lines[i + a]:
                            end = a - 1
                            break
                    for a in range(i+3, i+end):
                        c = re.findall(r'\]\s?-?\d.\d*', lines[a])
                        for j in range(3):
                            maxT = max(abs(float(b[j][1:])), maxT)
            if maxT > maxT2:
                maxT2 = maxT

        if 'Norm of T1AA' in line:
            caset1 = caset1 + 1
            if not caset1 > 2:
                t1a = line.split(':')[1][:-2]
        if 'Norm of T1BB' in line:
            caset1 = caset1 + 1
            if not caset1 > 2:
                t1b = line.split(':')[1][:-2]
        if 'total alpha spin electron number: ' in line:
            Nalpha = float(line.split(':')[1])
        if 'total  beta spin electron number: ' in line:
            Nbeta = float(line.split(':')[1])
        if 'frozen-core orbitals' in line:
            Ncore = 2*float(line.split()[2])

    t1 = math.sqrt((pow(float(t1a), 2) + pow(float(t1b), 2))/(Nalpha + Nbeta - Ncore))
    return s2, maxT2, t1


def get_final_energy(lines):
    for line in reversed(lines):
        if 'CCSD(T) energy' in line and len(line.split()) == 3:
            return line.split()[2]
    return None


def get_energy(lines):
    """ Obtain the latest HF, MP2, CCSD, and CCSD(T), energies. """
    for line in reversed(lines):
        if 'CCSD(T) energy' in line:
            ccsdpt_energy = line.split()[2]
        if 'CCSD energy' in line:
            ccsd_energy = line.split()[2]
        if 'Total MP2 energy' in line:
            mp2_energy = line.split()[4]
        if 'E(SCF)=' in line:
            hf_energy = line.split()[1]

    return ccsdpt_energy, ccsd_energy, mp2_energy, hf_energy
