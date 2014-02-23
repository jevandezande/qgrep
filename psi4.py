'''Source for all psi4 related functions'''

def get_geom( lines, type='xyz' ):
	'''Takes the lines of an psi4 output file and returns its last geometry'''
	start = '	Cartesian Geometry (in Angstrom)\n'
	end = '			 OPTKING Finished Execution \n'
	
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
			geom_start = i + 1
			break
	if geom_start == 0:
		return ''

	geom = lines[ geom_start: geom_end ]

	return geom

def plot( lines, type='xyz' ):
	'''Plots the the geometries from the optimization steps'''
	start = '	Cartesian Geometry (in Angstrom)\n'
	end = '			 OPTKING Finished Execution \n'

	geoms_start = []
	geoms_end = []
	for i in range( len(lines) ):
		if start == lines[i]:
			geoms_start.append( i + 1 )
		if end == lines[i]:
			geoms_end.append( i - 1 )
	print geoms_start
	print geoms_end

	geoms = []
	length = geoms_end[0] - geoms_start[0]
	for i in range( len(geoms_start) - 1 ):
		start = geoms_start[i]
		end = geoms_end[i]
		if end - start != length:
			length = end - start

		geom = str(length) + '\n\n'
		for line in lines[start:end]:
			geom += '\t'.join( line.split() ) + '\n'
		
		geoms.append(geom)
	
	# Last optimization step has an extra line after it
	start = geoms_start[-1]
	end = geoms_end[-1]
	for line in lines[start+1:end]:
		geom += '\t'.join( line.split() ) + '\n'
		
	return geoms

def check_convergence( lines ):
	'''Returns the last geometry convergence result'''
	convergence_result = '  ==> Convergence Check <==\n'
	convergence = ''
	for i in reversed( range( len( lines ) ) ):
		if convergence_result == lines[i]:
			convergence = ''.join( lines[i+5:i+11] )
			break
	
	return convergence
	
def checklist_convergence( lines ):
	'''Returns all the geometry convergence results'''
	convergence_result = '  ==> Convergence Check <==\n'
	convergence_list = []
	for i in range( len( lines ) ):
		if convergence_result == lines[i]:
			convergence_list.append( ''.join( lines[i+5:i+11] ) )
	
	return convergence_list
	
