'''Source for all qchem related functions'''

def get_geom( lines, type='xyz' ):
	geom_end = 0
	# Iterate backwards until the end last set of coordinates is found
	for i in reversed( range( len(lines) ) ):
		if 'Point Group' in lines[i]:
			geom_end = i
			break
	if geom_end == 0:
		return ''

	geom_start = 0
	# Iterate backwards until the beginning of the last set of coordinates is found
	for i in reversed( range( geom_end ) ):
		if 'Coordinates (Angstroms)' in lines[i]:
			geom_start = i + 2
			break
	if geom_start == 0:
		return ''


	geom = [ str( geom_end - geom_start ) + '\n', '\n' ]
	geom += [ '\t'.join( line.split()[1:] ) + '\n' for line in lines[geom_start:geom_end] ]

	return geom

def check_convergence( lines ):
	'''Returns the last geometry convergence result'''
	convergence = ''
	for i in reversed( range( len(lines) ) ):
		if 'Maximum     Tolerance    Cnvgd?' in lines[i]:
			convergence = ''.join( lines[i:i+4] )
			break
	
	return convergence
		
def checklist_convergence( lines ):
	'''Returns all the geometry convergence results'''
	convergence_list = []
	for i in range( len(lines) ):
		if 'Maximum     Tolerance    Cnvgd?' in lines[i]:
			convergence_list.append( ''.join( lines[i:i+4] ) )
	
	return convergence_list
