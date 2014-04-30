'''Source for all orca related functions'''

def get_geom( lines, type='xyz' ):
	'''Takes the lines of an orca output file and returns its last geometry in the specified format'''
	start = ''
	end = ''
	if type == 'xyz':
		start = 'CARTESIAN COORDINATES (ANGSTROEM)\n'
		end = 'CARTESIAN COORDINATES (A.U.)\n'
	elif type=='zmat':
		start = 'INTERNAL COORDINATES (ANGSTROEM)\n'
		end = 'INTERNAL COORDINATES (A.U.)\n'
	else:
		print "Invalid format"
		return
	
	geom_end = 0
	for i in reversed( range( len(lines) ) ):
		if end == lines[i]:
			geom_end = i - 2
			break
	if geom_end == 0:
		return ''

	geom_start = 0
	# Iterate backwards until the beginning of the last set of coordinates is found
	for i in reversed( range( geom_end ) ):
		if start == lines[i]:
			geom_start = i + 2
			break
	if geom_start == 0:
		return ''

	geom = lines[ geom_start: geom_end ]

	return geom

def plot( lines, type='xyz' ):
	'''Plots the the geometries from the optimization steps'''
	start = 'CARTESIAN COORDINATES (ANGSTROEM)\n'
	end = 'CARTESIAN COORDINATES (A.U.)\n'

	geoms_start = []
	geoms_end = []
	for i in range( len(lines) ):
		if start == lines[i]:
			geoms_start.append( i + 2 )
		if end == lines[i]:
			geoms_end.append( i - 2 )

	geoms = []
	length = geoms_end[0] - geoms_start[0]
	for i in range( len(geoms_start) ):
		start = geoms_start[i]
		end = geoms_end[i]
		if end - start != length:
			length = end - start

		geom = str(length) + '\nStep {0}\n'.format(i)
		for line in lines[start:end]:
			geom += '\t'.join( line.split() ) + '\n'
		
		geoms.append(geom)
		
	return geoms

def check_convergence( lines ):
	'''Returns the last geometry convergence result'''
	convergence_result = 'Geometry convergence'
	convergence = ''
	for i in reversed( range( len( lines ) ) ):
		if convergence_result in lines[i]:
			convergence = ''.join( lines[i-1:i+11] )
			break
	
	return convergence
	
def checklist_convergence( lines ):
	'''Returns all the geometry convergence results'''
	convergence_result = 'Geometry convergence'
	convergence_list = []
	for i in range( len( lines ) ):
		if convergence_result in lines[i]:
			convergence_list.append( ''.join( lines[i-1:i+11] ) )
	
	return convergence_list
	
def template( geom='', nprocs=8, jobtype='Opt', functional='B3LYP', basis='sto-3g', scf_iter=300 ):
	'''Returns a template with the specified geometry and other variables'''
	template_style = '''% pal nprocs {0} end

! {1} {2} {3}

% SCF maxiter {4} end

* xyz 0 1
{5}
*
'''
	return template_style.format( nprocs, jobtype, functional, basis, scf_iter, geom )

def get_freqs( lines ):
	'''Returns all the frequencies and geometries in xyz format'''
	# Find the coordinates of the geometries
	geometries_start = []
	geometries_end = []
	for i in range( len(lines) ):
		if 'CARTESIAN COORDINATES (ANGSTROEM)\n' == lines[i]:
			geometries_start.append( i + 2 )
		if 'CARTESIAN COORDINATES (A.U.)\n' == lines[i]:
			geometries_end.append( i - 2 )

	# Extract the geometries
	geometries = []
	num_atoms = geometries_end[0] - geometries_start[0]
	for i in range( len(geometries_start) ):
		start = geometries_start[i]
		end = geometries_end[i]
		# Add in error checking here
		if end - start != num_atoms:
			num_atoms = end - start

		geom = [ str(num_atoms), '' ]
		for line in lines[start:end]:
			geom.append( '\t'.join( line.split() ) )
		
		geometries.append(geom)

	# Save the geometries to the output file
	output = '\n\n'.join( [ '\n'.join(geom)  for geom in geometries ] )

	# Find the coordinates of the vibrational modes
	'''Model of vibrational output for an N atom molecule
			0	1	...		5
	atom1x	#	#	...		#
	atom1y	#	#	...		#
	atom1z	#	#	...		#
	atom2x	#	#	...		#
	atom2y	#	#	...		#
	atom2z	#	#	...		#
	...
	atomNz	#	#	...		#
			6	7	...		11
	atom1x	#	#	...		#
	atom1y	#	#	...		#
	atom1z	#	#	...		#
	atom2x	#	#	...		#
	atom2y	#	#	...		#
	atom2z	#	#	...		#
	...
	atomNz	#	#	...		#
	...
	'''
	vibrations_start = 0
	vib_modes_start = 0
	vib_modes_end = 0
	vib_freqs_start = 0
	vib_freqs_end = 0
	for i in reversed( range(len(lines) ) ):
		line = lines[i]
		if 'The first frequency considered to be a vibration is ' == line[0:52]:
			vibrations_start = int(line[52:].strip())
		
		if 'IR SPECTRUM\n' == line:
			vib_modes_end = i - 3
		if 'NORMAL MODES\n' == line:
			vib_modes_start = i + 7
		if 'VIBRATIONAL FREQUENCIES\n' == line:
			vib_freqs_start = i + 3
			break

	# Plot all vibrations (don't remove non-frequencies)
	vibrations_start = 0

	vib_freqs_end = vib_modes_start - 10
	vib_freqs = []
	# Read in the vibrational frequencies
	for i in range( vib_freqs_start, vib_freqs_end ):
		 vib_freqs.append( lines[i].split()[1] )

	vibrations = lines[vib_modes_start:vib_modes_end]
	modes = []
	'''modes list to be ordered by mode number
	[
		[		#mode0
			(atom1_x,y,z),(atom2_x,y,z),...
		],
		[		#mode1
			(atom1_x,y,z),(atom2_x,y,z),...
		],
		...
	]
	'''

	for i in range( 0, len(vibrations), 3*num_atoms+1 ):
		coords = []
		for j in range(0,3*num_atoms,3):
			x = vibrations[i+j+1].split()[1:]
			y = vibrations[i+j+2].split()[1:]
			z = vibrations[i+j+3].split()[1:]
			# the xyz coordinates for atom1 across the vibrations (up to 6)
			xyz = zip(x,y,z)
			coords.append(xyz)
			#				mode0	mode1	...	mode5
			# atom1 xyz = [(x,y,z),(x,y,z), ... ]
			# atom2 xyz = [(x,y,z),(x,y,z), ... ]
			# ...
		num_modes = len(coords[0])
		for j in range(num_modes):
			mode = []
			for k in range(num_atoms):
				mode.append( coords[k][j] )
			modes.append(mode)

	# Apply vibrations to the last geometry
	geom = geometries[-1]
	vibrations = []
	for i in range(len(modes)):
		mode = modes[i]
		vibrations.append( [ str(num_atoms) , '{0} cm^-1'.format( vib_freqs[i] ) ] )
		for j in range(len(modes[i])):
			vibrations[i].append( geom[j+2] + '\t' + '\t'.join( mode[j] ) )

	output = ''
	for freq in vibrations[vibrations_start:]:
		output += '\n'.join(freq) + '\n\n'
		
	return output

def get_energy( lines, energy_type='sp' ):
	'''Returns the last calculated energy
	WARNING: It returns as a string in order to prevent python from rounding'''
	energy = 0
	if energy_type == 'sp':
		energy_line = 'FINAL SINGLE POINT ENERGY'
		for line in reversed( lines ):
			if energy_line == line[:25]:
				energy = line.split()[-1]
				break
	elif energy_type == 'gibbs':
		energy_line = 'Final Gibbs free enthalpy'
		for line in reversed( lines ):
			if energy_line == line[:25]:
				energy = line.split()[-2]
				break
	return energy

def convert_zmatrix( lines ):
	'''Convert the oddly formatted orca zmzatrix into the normal type of zmatrix'''
	zmat = get_geom( lines, 'zmat' )
	line = zmat[0].split()
	normal_zmatrix = [ [ line[0] ] ]
	line = zmat[1].split()
	normal_zmatrix.append( [ line[0], line[1], line[4], ] )
	line = zmat[2].split()
	normal_zmatrix.append( [ line[0], line[1], line[4], line[2], line[5] ] )
	for line in zmat[3:]:
		# break line into parts
		element, atom1, atom2, atom3, distance, angle, dihedral = line.split()
		normal_zmatrix.append( [element, atom1, distance, atom2, angle, atom3, dihedral] )

	return normal_zmatrix
