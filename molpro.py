'''Molpro functions'''

def get_energy( lines ):
	'''Get the energy'''
	# The energy will always be on the third line from the end, zeroth element
	energy = lines[-3].split()[0]

	return energy
