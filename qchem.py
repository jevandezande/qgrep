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
