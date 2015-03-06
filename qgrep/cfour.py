

def get_geom(lines, type='xyz', units='bohr'):
    """Takes the lines of an cfour output file and returns its last geometry in
        the specified format"""
    if type == 'xyz' and units in ['bohr', 'angstrom']:
        start = ' Z-matrix   Atomic            Coordinates (in bohr)\n'
        if units == 'angstrom':
            print('Warning: Switching units to bohr.')
    else:
        print("Invalid format")
        return ''
    end = ' ----------------------------------------------------------------\n'

    geom_start = -1
    # Iterate backwards until the start of the last set of coordinates is found
    for i in reversed(list(range(len(lines)))):
        if start == lines[i]:
            geom_start = i + 3
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

    # Remove the atomic number
    geom = []
    for line in lines[geom_start: geom_end]:
        atom, an, *xyz = line.split()
        geom.append('{:<2s}  {}  {}  {}\n'.format(atom, *xyz))

    return geom


