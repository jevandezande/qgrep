'''Source for all qchem related functions'''

def get_geom( lines, type='xyz' ):
	start = 'Standard Nuclear Orientation (Angstroms)'
	end = 'Molecular Point Group'

	geom_end = 0
	# Iterate backwards until the end last set of coordinates is found
	for i in reversed( range( len(lines) ) ):
		if end in lines[i]:
			geom_end = i -1
			break
	if geom_end == 0:
		return ''

	geom_start = 0
	# Iterate backwards until the beginning of the last set of coordinates is found
	for i in reversed( range( geom_end ) ):
		if start in lines[i]:
			geom_start = i + 3
			break
	if geom_start == 0:
		return ''

	geom = [ '\t'.join( line.split()[1:] ) + '\n' for line in lines[geom_start:geom_end] ]

	return geom

def plot( lines ):
	'''Plots all the geometries for the optimization steps'''
	start = 'Standard Nuclear Orientation (Angstroms)'
	end = 'Molecular Point Group'
	
	geoms_start = []
	geoms_end = []
	for i in range( len( lines ) ):
		if start in lines[i]:
			geoms_start.append( i + 3 )
		if end in lines[i]:
			geoms_end.append( i - 1 )
	
	geoms = []
	length = geoms_end[0] - geoms_start[0]
	for i in range( len(geoms_start) ):
		start = geoms_start[i]
		end = geoms_end[i]
		# Should probably do some error checking here
		if not end - start == length:
			length = end - start

		geom = str(length) + '\nStep {0}\n'.format(i)
		for line in lines[start:end]:
			geom += '\t'.join( line.split()[1:] ) + '\n'

		geoms.append( geom )

	return geoms


def check_convergence( lines ):
	'''Returns the last geometry convergence result'''
	convergence_result = 'Maximum     Tolerance    Cnvgd?'
	convergence = ''
	for i in reversed( range( len(lines) ) ):
		if convergence_result in lines[i]:
			convergence = ''.join( lines[i:i+4] )
			break
	
	return convergence
		
def checklist_convergence( lines ):
	'''Returns all the geometry convergence results'''
	convergence_result = 'Maximum     Tolerance    Cnvgd?'
	convergence_list = []
	for i in range( len(lines) ):
		if convergence_result in lines[i]:
			convergence_list.append( ''.join( lines[i:i+4] ) )
	
	return convergence_list
