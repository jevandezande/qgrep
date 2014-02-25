'''Source for all orca related functions'''

def get_geom( lines, type='xyz' ):
	'''Takes the lines of an orca output file and returns its last geometry'''
	start = 'CARTESIAN COORDINATES (ANGSTROEM)\n'
	end = 'CARTESIAN COORDINATES (A.U.)\n'
	
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

		geom = str(length) + '\n\n'
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
	for i in reversed( range(len(lines) ) ):
		if 'The first frequency considered to be a vibration is ' == lines[i][0:52]:
			vibrations_start = int(lines[i][52:].strip())
		
		if 'IR SPECTRUM\n' == lines[i]:
			vib_modes_end = i - 3
		if 'NORMAL MODES\n' == lines[i]:
			vib_modes_start = i + 7
			break

	vibrations_start = 0
#	if vibrations_start == 0:
#		print "Could not find the first vibrational mode"
#	if args.all == True:
#		vibrations_start = 0
#	if vibrations_start > 6:
#		print "Warning: not all frequencies are considered vibrations. Use -a(--all) to plot all modes"
#		print "Starting with mode " + str( vibrations_start)

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
		vibrations.append( [ str(num_atoms) , 'Mode: {0}'.format(i) ] )
		for j in range(len(modes[i])):
			vibrations[i].append( geom[j+2] + '\t' + '\t'.join( mode[j] ) )

	output = ''
	for freq in vibrations[vibrations_start:]:
		output += '\n'.join(freq) + '\n\n'
		
	return output
