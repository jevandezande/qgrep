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
	
