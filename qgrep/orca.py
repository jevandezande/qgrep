"""Source for all orca related functions"""
import re

from collections import OrderedDict

from .molecule import Molecule
from .convergence import Convergence, Step


def get_geom(lines, geom_type='xyz', units='angstrom'):
    """
    Takes the lines of an orca output file and returns its last geometry in the
    specified format
    """
    start = ''
    end = '\n'
    if geom_type == 'xyz' and units == 'angstrom':
        start = 'CARTESIAN COORDINATES (ANGSTROEM)\n'
    elif geom_type == 'zmat' and units == 'angstrom':
        start = 'INTERNAL COORDINATES (ANGSTROEM)\n'
    elif geom_type == 'xyz' and units == 'bohr':
        start = 'CARTESIAN COORDINATES (A.U.)\n'
    elif geom_type == 'zmat' and units == 'bohr':
        start = 'INTERNAL COORDINATES (A.U.)\n'
    else:
        print("Invalid format or units")
        return ''

    geom_start = -1
    # Iterate backwards until the start of the last set of coordinates is found
    for i in reversed(list(range(len(lines)))):
        if start == lines[i]:
            geom_start = i + 2
            break
    if geom_start == -1:
        print("Could not find start of geometry")
        return ''

    geom_end = -1
    for i in range(geom_start, len(lines)):
        if end == lines[i]:
            geom_end = i
            break
    if geom_end == -1:
        return ''

    if geom_type == 'xyz' and units == 'bohr':
        geom_start += 1
    geom = lines[geom_start: geom_end]

    return geom


def plot(lines, geom_type='xyz'):
    """Plots the geometries from the optimization steps"""
    start = 'CARTESIAN COORDINATES (ANGSTROEM)\n'
    end = 'CARTESIAN COORDINATES (A.U.)\n'

    geoms_start = []
    geoms_end = []
    for i in range(len(lines)):
        if start == lines[i]:
            geoms_start.append(i + 2)
        if end == lines[i]:
            geoms_end.append(i - 2)

    geoms = []
    length = geoms_end[0] - geoms_start[0]
    for i in range(len(geoms_start)):
        start = geoms_start[i]
        end = geoms_end[i]
        if end - start != length:
            length = end - start

        geom = str(length) + '\nStep {0}\n'.format(i)
        for line in lines[start:end]:
            geom += '\t'.join(line.split()) + '\n'

        geoms.append(geom)

    return geoms


def check_convergence(lines):
    """Returns all the geometry convergence results"""
    convergence_result = 'Geometry convergence'
    convergence_list = []
    for i in range(len(lines)):
        if convergence_result in lines[i]:
            convergence_list.append(''.join(lines[i - 1:i + 11]))

    return convergence_list


def template(geom='', jobtype='Opt', functional='B3LYP', basis='sto-3g'):
    """Returns a template with the specified geometry and other variables"""
    template_style = """% pal nprocs 8 end

! {0} {1} {2} RIJCOSX AutoAux

% SCF maxiter 300 end

* xyz 0 1
{3}
*
"""
    return template_style.format(jobtype, functional, basis, geom)


def get_freqs(lines):
    """Returns all the frequencies and geometries in xyz format"""
    # Find the coordinates of the vibrational modes (assumes the last coordinates given)
    geom = get_geom(lines)
    num_atoms = len(geom)
    geom = [str(num_atoms), ''] + ['\t'.join(line.split()) for line in geom]

    """Model of vibrational output for an N atom molecule
            0    1    ...        5
    atom1x    #    #    ...        #
    atom1y    #    #    ...        #
    atom1z    #    #    ...        #
    atom2x    #    #    ...        #
    atom2y    #    #    ...        #
    atom2z    #    #    ...        #
    ...
    atomNz    #    #    ...        #
            6    7    ...        11
    atom1x    #    #    ...        #
    atom1y    #    #    ...        #
    atom1z    #    #    ...        #
    atom2x    #    #    ...        #
    atom2y    #    #    ...        #
    atom2z    #    #    ...        #
    ...
    atomNz    #    #    ...        #
    ...
    """
    vibrations_start = 0
    vib_modes_start = 0
    vib_modes_end = 0
    vib_freqs_start = 0
    vib_freqs_end = 0
    hybrid_hessian_vib_modes_end = 0
    for i in reversed(list(range(len(lines)))):
        line = lines[i]
        if 'The first frequency considered to be a vibration is ' == line[0:52]:
            vibrations_start = int(line[52:].strip())
            hybrid_hessian_vib_modes_end = i - 2

        if 'IR SPECTRUM\n' == line:
            vib_modes_end = i - 3
        elif 'NORMAL MODES\n' == line:
            vib_modes_start = i + 7
        elif 'VIBRATIONAL FREQUENCIES\n' == line:
            vib_freqs_start = i + 3
            break

    # Partial hessian calculation output looks a little different
    if vib_modes_end == 0 and hybrid_hessian_vib_modes_end != 0:
        vib_modes_end = hybrid_hessian_vib_modes_end

    # Plot all vibrations (don't remove non-frequencies)
    vibrations_start = 0

    vib_freqs_end = vib_modes_start - 10
    vib_freqs = []
    # Read in the vibrational frequencies
    for i in range(vib_freqs_start, vib_freqs_end):
        vib_freqs.append(lines[i].split()[1])

    vibrations = lines[vib_modes_start:vib_modes_end]
    modes = []
    """modes list to be ordered by mode number
    [
        [       #mode0
            (atom1_x,y,z),(atom2_x,y,z),...
       ],
        [       #mode1
            (atom1_x,y,z),(atom2_x,y,z),...
       ],
        ...
   ]
    """

    for i in range(0, len(vibrations), 3 * num_atoms + 1):
        coords = []
        for j in range(0, 3 * num_atoms, 3):
            x = vibrations[i + j + 1].split()[1:]
            y = vibrations[i + j + 2].split()[1:]
            z = vibrations[i + j + 3].split()[1:]
            # the xyz coordinates for atom1 across the vibrations (up to 6)
            xyz = list(zip(x, y, z))
            coords.append(xyz)
            # mode0    mode1    ...    mode5
        # atom1 xyz = [(x,y,z),(x,y,z), ...]
        # atom2 xyz = [(x,y,z),(x,y,z), ...]
        # ...
        num_modes = len(coords[0])
        for j in range(num_modes):
            mode = []
            for k in range(num_atoms):
                mode.append(coords[k][j])
            modes.append(mode)

    # Apply vibrations to the last geometry
    vibrations = []
    # Don't print the first six modes, as they are not vibrations
    for i in range(len(modes) - 6):
        mode = modes[i + 6]
        # xyz header including the vibrational frequency
        # offset by 6 to avoid non-vibrational modes
        vibrations.append([str(num_atoms), '{0} cm^-1'.format(vib_freqs[i + 6])])
        for j in range(len(modes[i])):
            # Geometry goes first, then x, y, and z displacements for modes
            vibrations[i].append(geom[j + 2] + '\t' + '\t'.join(mode[j]))

    output = ''
    for freq in vibrations[vibrations_start:]:
        output += '\n'.join(freq) + '\n\n'

    return output


def get_ir(lines):
    vib_freqs_start = 0
    vib_freqs_end = 0
    for i in reversed(list(range(len(lines)))):
        line = lines[i]
        if 'NORMAL MODES\n' == line:
            vib_freqs_end = i - 3
        elif 'VIBRATIONAL FREQUENCIES\n' == line:
            vib_freqs_start = i + 3
            break

    vib_freqs = []
    # Read in the vibrational frequencies
    for i in range(vib_freqs_start, vib_freqs_end):
        vib_freqs.append(lines[i].split()[1])

    return vib_freqs


def get_energy(lines, energy_type='sp'):
    """Returns the last calculated energy
    WARNING: It returns as a string in order to prevent python from rounding"""
    energy = 0
    if energy_type == 'sp':
        energy_line = 'FINAL SINGLE POINT ENERGY'
        for line in reversed(lines):
            if energy_line == line[:25]:
                energy = line.split()[4]
                break
    elif energy_type == 'gibbs':
        energy_line = 'Final Gibbs free enthalpy'
        for line in reversed(lines):
            if energy_line == line[:25]:
                energy = line.split()[-2]
                break
    elif energy_type == 'enthalpy':
        energy_line = 'Total enthalpy'
        for line in reversed(lines):
            if energy_line == line[:14]:
                energy = line.split()[-2]
                break
    elif energy_type == 'entropy':
        energy_line = 'Total entropy correction'
        for line in reversed(lines):
            if energy_line == line[:24]:
                energy = line.split()[4]
                break
    elif energy_type == 'zpve':
        energy_line = 'Zero point energy'
        for line in reversed(lines):
            if energy_line == line[:17]:
                energy = line.split()[4]
                break

    return energy


def get_energies(lines, energy_type='sp'):
    """
    Returns all of the calculated energies
    """
    energies = []
    if energy_type == 'sp':
        energy_line = 'FINAL SINGLE POINT ENERGY'
        for line in lines:
            if energy_line == line[:25]:
                energies.append(float(line.split()[4]))
    elif energy_type == 'gibbs':
        energy_line = 'Final Gibbs free enthalpy'
        for line in lines:
            if energy_line == line[:25]:
                energies.append(float(line.split()[-2]))
    elif energy_type == 'enthalpy':
        energy_line = 'Total enthalpy'
        for line in lines:
            if energy_line == line[:14]:
                energies.append(float(line.split()[-2]))
    elif energy_type == 'entropy':
        energy_line = 'Total entropy correction'
        for line in lines:
            if energy_line == line[:24]:
                energies.append(float(line.split()[4]))
    elif energy_type == 'zpve':
        energy_line = 'Zero point energy'
        for line in lines:
            if energy_line == line[:17]:
                energies.append(float(line.split()[4]))

    return energies


def convert_zmatrix(lines, units):
    """Convert the orca zmatrix to a proper zmatrix"""
    zmat = get_geom(lines, 'zmat', units)
    line = zmat[0].split()
    normal_zmatrix = [[line[0]]]
    line = zmat[1].split()
    normal_zmatrix.append([line[0], line[1], line[4], ])
    if len(zmat) > 2:
        line = zmat[2].split()
        normal_zmatrix.append([line[0], line[1], line[4], line[2], line[5]])
    for line in zmat[3:]:
        # break line into parts
        element, atom1, atom2, atom3, distance, angle, dihedral = line.split()
        normal_zmatrix.append([element, atom1, distance, atom2, angle, atom3, dihedral])

    return normal_zmatrix


def convert_to_orca_zmatrix(lines):
    """Convert a proper zmatrix into an orca zmatrix"""
    # First line
    element = lines[0].split()[0]
    orca_zmatrix = [[element, '0', '0', '0', '0', '0', '0']]
    # Second lines
    element, atom1, distance = lines[1].split()[:3]
    orca_zmatrix.append([element, atom1, '0', '0', distance, '0', '0'])
    # Third line
    if len(lines) > 2:
        element, atom1, distance, atom2, angle = lines[2].split()[:5]
        orca_zmatrix.append([element, atom1, atom2, '0', distance, angle, '0'])
    # All other lines
    for line in lines[3:]:
        element, atom1, distance, atom2, angle, atom3, dihedral = line.split()[:7]
        orca_zmatrix.append([element, atom1, atom2, atom3,
                             distance, angle, dihedral])

    return orca_zmatrix


def energy_levels(lines):
    """
    Returns the orbital occupations and energies of the last geometry as well as
    useful information
    """
    start = 'ORBITAL ENERGIES\n'
    end = '\n'

    levels_start = 0
    # Iterate backwards until the start of the last set of coordinates is found
    for i in reversed(list(range(len(lines)))):
        if start == lines[i]:
            levels_start = i + 5
            break
    if levels_start == 0:
        print("Could not find start of orbitals")
        return ''

    levels_end = 0
    for i in range(levels_start, len(lines)):
        if end == lines[i]:
            levels_end = i
            break
    if levels_end == 0:
        print("Could not find the end of the orbitals")
        return ''

    levels = lines[levels_start: levels_end]

    clean = []
    for level in levels:
        num, occ, hartree, eV, *sym = level.split()
        if sym:
            clean.append((int(num), float(occ), float(hartree)))
        else:
            clean.append((int(num), float(occ), float(hartree), sym))

    info = OrderedDict()
    for i in range(len(clean)):
        if clean[i][1] == 0:
            info['homo'] = clean[i - 1][2]
            info['lumo'] = clean[i][2]
            info['homo-lumo-gap'] = info['lumo'] - info['homo']
            break

    return levels, info


def get_molecule(lines):
    start = 'CARTESIAN COORDINATES (ANGSTROEM)\n'
    end = '\n'
    geom_start = -1
    for i, line in reversed(list(enumerate(lines))):
        if start == line:
            geom_start = i + 2
            break
    if geom_start == -1:
        return ''

    mol = Molecule()
    for i in range(geom_start, len(lines)):
        if end == lines[i]:
            break
        data = lines[i].split()
        mol.append([data[0]] + list(map(float, data[1:4])))

    return mol


def get_charge(lines):
    """
    Returns the charge of the molecule in the computations
    """
    for line in reversed(lines):
        if line[:13] == ' Total Charge':
            return int(line.split()[-1])
    return None

def get_multiplicity(lines):
    """
    Returns the multiplicity of the computation. Uses the SCF value.
    If no multiplicity can be found, it returns 0
    """
    for line in reversed(lines):
        if line[:13] == ' Multiplicity':
            return int(line.split()[-1])
    return 0


def convergence(output_file):
    """
    Sample geometry convergence output. May not include energy change line
                                .--------------------.
          ----------------------|Geometry convergence|---------------------
          Item                value                 Tolerance   Converged
          -----------------------------------------------------------------
          Energy change      -0.42714550            0.00003000      NO
          RMS gradient        0.23385284            0.00050000      NO
          MAX gradient        0.96262577            0.00200000      NO
          RMS step            0.06464278            0.00700000      NO
          MAX step            0.26280432            0.01000000      NO
          ....................................................
          Max(Bonds)      0.1391      Max(Angles)    0.48
          Max(Dihed)        0.00      Max(Improp)    0.00
          -----------------------------------------------------------------
    """
    convergence_re = r'''(Energy change\s+([-]?\d+.\d+)\s+([-]?\d+.\d+)\s+(YES|NO))?
          RMS gradient \s+([-]?\d+.\d+)\s+([-]?\d+.\d+)\s+(YES|NO)
          MAX gradient \s+([-]?\d+.\d+)\s+([-]?\d+.\d+)\s+(YES|NO)
          RMS step     \s+([-]?\d+.\d+)\s+([-]?\d+.\d+)\s+(YES|NO)
          MAX step     \s+([-]?\d+.\d+)\s+([-]?\d+.\d+)\s+(YES|NO)
          ....................................................
          Max\(Bonds\)\s+([-]?\d+.\d+)\s+Max\(Angles\)\s+([-]?\d+.\d+)
          Max\(Dihed\)\s+([-]?\d+.\d+)\s+Max\(Improp\)\s+([-]?\d+.\d+)
          -----------------------------------------------------------------'''

    output = open(output_file).read()
    matches = re.findall(convergence_re, output)
    steps = []
    for match in matches:
        e_str, e_val,  e_tol, e_conv = match[0:4]
        if e_val:
            e_val = float(e_val)
        else:
            e_val = 0
        rg_val, rg_tol, rg_conv = match[4:7]
        mg_val, mg_tol, mg_conv = match[7:10]
        rs_val, rs_tol, rs_conv = match[10:13]
        ms_val, ms_tol, ms_conv = match[13:16]
        rg_val, mg_val, rs_val, ms_val = float(rg_val), float(mg_val), float(rs_val), float(ms_val)
        steps.append(Step(e_val, rg_val, mg_val, rs_val, ms_val))

    return Convergence(steps, [])


def update_geom(infile='input.dat', outfile='output.dat'):
    with open(infile) as f:
        in_lines = f.readlines()
    start = -1
    end = -1
    for i, line in enumerate(in_lines):
        if line[0] == '*':
            if len(line.strip()) > 1:
                geom_type = line[1:].split()[0]
                start = i + 1
            else:
                end = i
                break

    with open(outfile) as f:
        out_lines = f.readlines()

    geom = get_geom(out_lines, geom_type=geom_type)

    updated = in_lines[:start] + geom + in_lines[end:]

    with open(infile, 'w') as f:
        f.writelines(updated)


def completed(lines):
    """
    Check if the output file shows successful completion
    """
    return lines[-1][:14] == 'TOTAL RUN TIME'


def get_nat_orb_occ(lines):
    """
    Find the natural orbital occupations
    """
    nat_occ = []
    start = False
    for line in lines:
        if start:
            if line.strip():
                nat_occ.append(abs(float(line.split('=')[-1].strip())))
            else:
                break
        elif line == 'Natural Orbital Occupation Numbers:\n':
            start = True

    return nat_occ
