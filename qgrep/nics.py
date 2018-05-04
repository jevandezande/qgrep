import pybel
import numpy as np
import openbabel as ob


def nics_points(molecule, format='orca'):
    """
    Generate the NICS(0,1, and -1) points for all rings in a geometry
    :param molecule: a molecule that pybel can read
    :param format: format to output the NICS points
    """
    mol = pybel.readstring('xyz', molecule)

    # Find centers and normal vectors of rings to generate ghost atom positions
    c, n1, n2 = ob.vector3(), ob.vector3(), ob.vector3()
    ghost_atoms = []
    for i, ring in enumerate(mol.sssr):
        atoms = [a for a in range(len(mol.atoms)) if ring.IsInRing(a + 1)]
        ring.findCenterAndNormal(c, n1, n2)
        center = np.array([ c.GetX(),  c.GetY(),  c.GetZ()])
        normal = np.array([n1.GetX(), n1.GetY(), n1.GetZ()])
        normal /= np.linalg.norm(normal)
        print('-'*51)
        print(f'Ring {i}')
        print(f'Atoms {atoms}')
        print('C:  {:>15.10f} {:>15.10f} {:>15.10f}'.format(*center))
        print('N1: {:>15.10f} {:>15.10f} {:>15.10f}'.format(*normal))
        ghost_atoms += center, center + normal, center - normal

    # Print ghost atoms
    format = format.lower()
    if format == 'orca':
        newgto = 'newgto S 1 1 100000 1 end newauxJKgto S 1 1 200000 1 end'
        print('-'*51)
        print('Ghost atoms for NICS')
        for i, (x, y, z) in enumerate(ghost_atoms):
            comment = ['Center', 'Top', 'Bottom'][i % 3]
            print(f'H:  {x:>15.10f} {y:>15.10f} {z:>15.10f} {newgto} # {comment}')
    else:
        print(f'{format} is not currently supported.')
