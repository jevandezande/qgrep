'''Source for all orca related functions'''

def get_geom( input, output, type='xyz' ):
	'''Takes an orca output file and returns its last geometry'''
	with open( input ) as f:
		lines = f.readlines()

	start = 'CARTESIAN COORDINATES (ANGSTROEM)'
	end = 'CARTESIAN COORDINATES (A.U.)'
	
	for i in reversed( range( len(lines) ) ):
		if end in lines[i]:
			geom_end = i - 2
			break
	if geom_end == 0:
		print "No coordinates found"
		return ''

	geom_start = 0
	# Iterate backwards until the beginning of the last set of coordinates is found
	for i in reversed( range( geom_end ) ):
		if start in lines[i]:
			geom_start = i + 2
			break
	if geom_start == 0:
		print "No coordinates found"
		sys_exit( 1 )

	geom = lines[ geom_start: geom_end ]

	if not output == '':
		out = ''
		for line in geom:
			out += '\t'.join( line.split() ) + '\n'

		with open( output, 'w' ) as f:
			f.write( out )

	return geom

def plot( input='output.xyz', output='geom.xyz', type='xyz' ):
	'''Plots the the geometries from the optimization steps'''
	with open( input ) as f:
		lines = f.readlines()

	geoms_start = []
	geoms_end = []
	for i in range( len(lines) ):
		if 'CARTESIAN COORDINATES (ANGSTROEM)\n' == lines[i]:
			geoms_start.append( i + 2 )
		if 'CARTESIAN COORDINATES (A.U.)\n' == lines[i]:
			geoms_end.append( i - 2 )


	geoms = []
	length = geoms_end[0] - geoms_start[0]
	for i in range( len(geoms_start) ):
		start = geoms_start[i]
		end = geoms_end[i]
		if end - start != length:
			print "Starting work on new molecule"
			length = end - start

		geom = str(length) + '\n\n'
		for line in lines[start:end]:
			geom += '\t'.join( line.split() ) + '\n'
		
		geoms.append(geom)

	if not output == '':
		out = '\n'.join(geoms)

		with open( output, 'w' ) as f:
			f.write( out )
		
	return geoms

def check_convergence( input ):
	'''Returns the last geometry convergence results'''	
	with open( input ) as f:
		lines = f.readlines()
	
	convergence = ''
	for i in reversed( range( len( lines ) ) ):
		if 'Geometry convergence' in lines[i]:
			convergence = ''.join( lines[i-1:i+11] )
			break
	
	return convergence
	
def checklist_convergence( input ):
	'''Returns all the geometry convergence results'''	
	with open( input ) as f:
		lines = f.readlines()
	
	convergence_list = []
	for i in range( len( lines ) ):
		if 'Geometry convergence' in lines[i]:
			convergence_list.append( ''.join( lines[i-1:i+11] ) )
	
	return convergence_list
	
