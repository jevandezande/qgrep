def check_type( lines ):
	'''Takes the lines of an output file and determines what program wrote them'''
	programs = {
	'* O   R   C   A *':	'orca',
	'Welcome to Q-Chem':	'qchem',
	'PSI4: An Open-Source Ab Initio Electronic Structure Package':	'psi4',
	'Northwest Computational Chemistry Package (NWChem)':	'nwchem',
	}

	program = ''
	for line in lines:
		line = line.strip()
		if line in programs:
			program = programs[line]
	
	return program
