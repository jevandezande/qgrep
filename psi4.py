"""Source for all psi4 related functions"""


def get_geom(lines, type='xyz'):
    """Takes the lines of an psi4 output file and returns its last geometry"""
    start = '    Cartesian Geometry (in Angstrom)\n'
    end = '             OPTKING Finished Execution \n'

    geom_end = 0
    for i in reversed(list(range(len(lines)))):
        if end == lines[i]:
            geom_end = i - 2
            break
    if geom_end == 0:
        return ''

    geom_start = 0
    # Iterate backwards until the beginning of the last set of coordinates is found
    for i in reversed(list(range(geom_end))):
        if start == lines[i]:
            geom_start = i + 1
            break
    if geom_start == 0:
        return ''

    geom = lines[geom_start: geom_end]

    return geom


def plot(lines, type='xyz'):
    """Plots the the geometries from the optimization steps"""
    start = '    Cartesian Geometry (in Angstrom)\n'
    end = '             OPTKING Finished Execution \n'

    geoms_start = []
    geoms_end = []
    for i in range(len(lines)):
        if start == lines[i]:
            geoms_start.append(i + 1)
        if end == lines[i]:
            geoms_end.append(i - 1)

    geoms = []
    length = geoms_end[0] - geoms_start[0]
    for i in range(len(geoms_start) - 1):
        start = geoms_start[i]
        end = geoms_end[i]
        if end - start != length:
            length = end - start

        geom = str(length) + '\nStep {0}\n'.format(i)
        for line in lines[start:end]:
            geom += '\t'.join(line.split()) + '\n'

        geoms.append(geom)

    # Last optimization step has an extra line after it
    start = geoms_start[-1]
    end = geoms_end[-1]
    for line in lines[start + 1:end]:
        geom += '\t'.join(line.split()) + '\n'

    return geoms


def check_convergence(lines):
    """Returns all the geometry convergence results"""
    convergence_result = '  ==> Convergence Check <==\n'
    convergence_list = []
    for i in range(len(lines)):
        if convergence_result == lines[i]:
            convergence_list.append(''.join(lines[i + 5:i + 11]))

    return convergence_list


def get_freqs(lines):
    """Returns all the frequencies and geometries in xyz format"""

    geometries = plot(lines)

    # Save the geometries to the output file
    output = '\n\n'.join(['\n'.join(geom) for geom in geometries])


    # Find the coordinates of the vibrational modes
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
    for i in reversed(list(range(len(lines)))):
        if 'The first frequency considered to be a vibration is ' == lines[i][0:52]:
            vibrations_start = int(lines[i][52:].strip())

        if 'IR SPECTRUM\n' == lines[i]:
            vib_modes_end = i - 3
        if 'NORMAL MODES\n' == lines[i]:
            vib_modes_start = i + 7
            break

    vibrations_start = 0

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

    num_atoms = len(geometries[-1])
    print(geometries)
    print(num_atoms)
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
    geom = geometries[-1]
    vibrations = []
    for i in range(len(modes)):
        mode = modes[i]
        vibrations.append([str(num_atoms), 'Mode: {0}'.format(i)])
        for j in range(len(modes[i])):
            vibrations[i].append(geom[j + 2] + '\t' + '\t'.join(mode[j]))

    output = ''
    for freq in vibrations[vibrations_start:]:
        output += '\n'.join(freq) + '\n\n'

    return output


def get_energy(lines, energy_type='sp'):
    """WARNING: It returns as a string in order to prevent python from rounding"""
    if energy_type == 'sp':
        for line in reversed(lines):
            if line[:18] == '    Total Energy =':
                return line.split()[-1]
    else:
        print('Energy type not yet supported')
