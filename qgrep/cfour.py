

def get_geom(lines, geom_type='xyz', units='bohr'):
    """Takes the lines of an cfour output file and returns its last geometry in
        the specified format"""
    if geom_type == 'xyz' and units in ['bohr', 'angstrom']:
        start = ' Z-matrix   Atomic            Coordinates (in bohr)\n'
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
        xyz = list(map(lambda x: float(x) / 1.889725989, xyz))
        geom.append('{:s}\t{}\t{}\t{}\n'.format(atom, *xyz))

    return geom


def get_ir(lines):
  """ Returns all the frequencies and geometries in xyz format. """

  geom = get_geom(lines)
  num_atoms = len(geom)

  vibrations_start = 0
  vib_modes_start = 0
  vib_modes_end = 0
  vib_freqs_start = 0
  vib_freqs_end = 0
  hybrid_hessian_vib_modes_end = 0
  for i in reversed(list(range(len(lines)))):
      line = lines[i]
      if 'Gradient vector in normal coordinate representation' in line:
          vib_modes_end = i - 1
      elif 'Normal Coordinates' in line:
          vib_modes_start = i + 2
      elif 'Zero-point vibrational energy' in line:
          vib_freqs_end = i - 1
      elif 'Cartesian force constants:' in line:
          vib_freqs_start = i + 1 + 6 # The + 6 is to exclude the 0.000 cm^-1 freqs 
          break


  freqs = []
  for i in range(vib_freqs_start, vib_freqs_end + 1):
    freqs.append(lines[i].split()[1])

  freq_num = len(freqs)
  freqs.reverse()

  return freqs

