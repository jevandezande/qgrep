"""Source for all qchem related functions"""

import os.path as path


# noinspection PyPep8
def get_geom(lines, geom_type='xyz', units='Angstrom'):
    start = 'Standard Nuclear Orientation (Angstroms)'
    end = 'Molecular Point Group'

    geom_end = 0
    # Iterate backwards until the end last set of coordinates is found
    for i in reversed(list(range(len(lines)))):
        if end in lines[i]:
            geom_end = i - 1
            break
    if geom_end == 0:
        return ''

    geom_start = 0
    # Iterate backwards until the beginning of the last set of coordinates is found
    for i in reversed(list(range(geom_end))):
        if start in lines[i]:
            geom_start = i + 3
            break
    if geom_start == 0:
        return ''

    geom = ['\t'.join(line.split()[1:]) + '\n' for line in lines[geom_start:geom_end]]

    return geom


def plot(lines, geom_type='xyz'):
    """Plots all the geometries for the optimization steps"""
    if geom_type != 'xyz':
        raise SyntaxError('Only xyz coordinates are currently supported')
    
    start = 'Standard Nuclear Orientation (Angstroms)'
    end = 'Molecular Point Group'

    geoms_start = []
    geoms_end = []
    for i in range(len(lines)):
        if start in lines[i]:
            geoms_start.append(i + 3)
        if end in lines[i]:
            geoms_end.append(i - 1)

    geoms = []
    length = geoms_end[0] - geoms_start[0]
    for i in range(len(geoms_start)):
        start = geoms_start[i]
        end = geoms_end[i]
        # Should probably do some error checking here
        if not end - start == length:
            length = end - start

        geom = str(length) + '\nStep {0}\n'.format(i)
        for line in lines[start:end]:
            geom += '\t'.join(line.split()[1:]) + '\n'

        geoms.append(geom)

    return geoms


def check_convergence(lines):
    """Returns all the geometry convergence results"""
    convergence_result = 'Maximum     Tolerance    Cnvgd?'
    convergence_list = []
    for i in range(len(lines)):
        if convergence_result in lines[i]:
            convergence_list.append(''.join(lines[i:i + 4]))

    return convergence_list


def template(geom='', jobtype='Opt', functional='B3LYP', basis='sto-3g'):
    """Returns a template with the specified geometry and other variables"""
    template_style = """$molecule
{0}
$end

$rem
    jobtype            {1}
    exchange        {2}
    basis            {3}
$end
"""

    return template_style.format(geom, jobtype, functional, basis)


def generate_input(geom='', options=None):
    """
    Generate an input file with the given options and the files available in the
    folder
    """
    if not options: options = {}
    # Convert keys and values to lowercase strings for ease of use
    if options:
        options = {str(k).lower(): str(v).lower() for k, v in options.items()}
    else:
        options = {}

    # Run a frequency before these jobs
    job2 = None
    if options['jobtype'] == 'ts' or options['jobtype'] == 'rpath':
        job2 = options['jobtype']
        options['jobtype'] = 'freq'
    # Run a frequency to confirm minimum
    if options['jobtype'] == 'optfreq':
        job2 = 'freq'
        options['jobtype'] = 'opt'

    check = []
    if geom:
        if geom == 'read':
            if path.isfile('geom.xyz'):
                geom = [line.split() for line in open('geom.xyz').readlines() ]
                charge = 0
                multiplicity = 1
                if len(geom[0]) == 2 and geom[0][0].isdigit() and geom[0][1].isdigit():
                    charge = int(geom[0][0])
                    multiplicity = int(geom[0][1])
                else:
                    check.append('charge/multiplicity')
                    
                if len(geom[0]) == 1 and geom[0][0].isdigit():
                    # Remove the useless numatoms and blank line
                    geom = geom[2:]
                geom = ''.join(['\t' + '\t'.join(line) + '\n' for line in geom])
            else:
                check.append('Missing geometry file')
    # Prettify the geometry by adding tabs
    input_str = "$molecule\n{}\n$end\n".format(geom)

    basis = ''
    if 'basis' in options:
        if options['basis'] == 'read':
            if path.isfile('basis.gbs'):
                basis = "\n$basis\n" + open('basis.gbs').read() + "$end\n"
            else:
                check.append("Can't open basis")
    else:
        check.append('Missing basis')

    ecp = ''
    if 'ecp' in options:
        if options['ecp'] == 'read':
            if path.isfile('ecp.gbs'):
                ecp = "\n$ecp\n" + open('ecp.gbs').read() + "$end\n"
            else:
                check.append("Can't open ecp")

    # Extra options
    if not 'max_scf_cycles' in options:
        options['max_scf_cycles'] = '300'
    
    # Write rem section using keys and values from dictionary
    kv_form = '\t{:<19s} {}\n'
    rem = ''.join([kv_form.format(k, v) for k, v in sorted(options.items())])
    input_str += '\n$rem\n' + rem + '\n$end\n'

    if 'basis' in options:
        if options['basis'] == 'read':
            input_str += basis
    if 'ecp' in options:
        if options['ecp'] == 'read':
            input_str += ecp

    if job2:
        input_str += "\n@@@\n\n$molecule\n\tread\n$end\n"
        if options['basis'] == 'read':
            input_str += basis
        if options['ecp'] == 'read':
            input_str += ecp
        options['scf_guess'] = 'read'
        if options['jobtype'] == 'freq':
            options['geom_opt_hessian'] = 'read'
        options['jobtype'] = job2

        # Write rem
        kv_form = '\t{:<19s} {}\n'
        rem = ''.join([kv_form.format(k, v) for k, v in sorted(options.items())])
        input_str += '\n$rem\n' + rem + '\n$end\n'

    print(input_str)
    print('Check:' + '\n\t'.join(check))

    open('input.dat', 'w').write(input_str)
