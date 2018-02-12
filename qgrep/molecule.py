import numpy as np

from cclib.io import ccread


class Molecule:
    def __init__(self, geom=None):
        """ Simple molecule class

        :param geom: List of lists ordered as [[atom, [x, y, z]], ...]
        """
        # Magically unpacks
        self.geom = geom

    def __len__(self):
        """Return the number of atoms in the molecule"""
        return len(self.atoms)

    def __str__(self):
        """
        Returns a string of the geometry, filling out positions with zeros and
        spaces as needed
        """
        form = '{:<4}' + ' {:> 13.8f}' * 3
        return '\n'.join([form.format(atom, *xyz) for atom, xyz in self])

    def __iter__(self):
        for atom, xyz in zip(self.atoms, self.xyz):
            yield atom, xyz

    def __add__(self, other):
        """ Combine two molecules """
        if isinstance(self, Molecule) and isinstance(self, Molecule):
            return Molecule(self.geom + other.geom)
        else:
            raise ValueError(f'Cannot combine {type(self)} and {type(other)}')

    def __getitem__(self, i):
        """Returns the ith atom"""
        return (self.atoms[i], self.xyz[i])

    def __setitem__(self, i, atom_xyz):
        """Sets the ith atom"""
        atom, xyz = atom_xyz
        Molecule.check_atom(atom, xyz)
        self.atoms[i] = atom
        self.xyz[i] = xyz

    def __delitem__(self, i):
        """Deletes the ith atom"""
        del self.atoms[i]
        self.xyz = np.delete(self.xyz, i, axis=0)

    def __eq__(self, other):
        if not isinstance(other, Molecule):
            return False
        if self.atoms != other.atoms or (self.xyz != other.xyz).any():
            return False
        return True

    def insert(self, i, atom, xyz):
        """Insert the atom in the specified position"""
        Molecule.check_atom(atom, xyz)
        self.atoms.insert(i, atom)
        self.xyz = np.insert(self.xyz, i, xyz, axis=0)

    @property
    def geom(self):
        """Return the geometry"""
        return [[atom, list(xyz)] for atom, xyz in self]

    @geom.setter
    def geom(self, geom):
        """Set the geometry"""
        self.atoms, self.xyz = [], np.array([])
        if geom is not None:
            Molecule.check_geom(geom)
            atoms, xyzs = zip(*geom)
            self.atoms = list(atoms)
            self.xyz = np.array(xyzs)

    def append(self, atom, xyz):
        """Append atom to geometry"""
        Molecule.check_atom(atom, xyz)
        self.atoms.append(atom)
        self.xyz = np.append(self.xyz, np.array(xyz)[np.newaxis, ...], axis=0)

    @staticmethod
    def check_atom(atom, xyz):
        """ Check if an atom is properly formatted
        Raises a syntax error if it is not
        """
        if not isinstance(atom, str):
            raise SyntaxError(f'Atom name must be a string: {atom}')
        if len(xyz) != 3:
            raise SyntaxError('Only 3 coordinates supported.')
        return True

    @staticmethod
    def check_geom(geom):
        """ Checks if the given geometry is valid
        raises a syntax error if it is not
        """
        for atom, xyz in geom:
            Molecule.check_atom(atom, xyz)

        return True

    @staticmethod
    def read_from(infile):
        """Read from a file"""
        try:
            data = ccread(infile)
            # Hack: cclib doesn't have an easy way to access atom names
            lines = data.writexyz().splitlines()
        except AttributeError as e:
            # Attempt to read as an XYZ file
            with open(infile) as f:
                lines = f.readlines()
        # Strip off length if provided
        if lines[0].strip().isdigit():
            lines = lines[2:]
        geom = []
        for line in lines:
            if line.strip() == '':
                continue
            atom, x, y, z = line.split()[:4]
            geom.append([atom, [float(x), float(y), float(z)]])

        return Molecule(geom)

    def write(self, outfile='geom.xyz', label=True, style='xyz'):
        """
        Writes the geometry to the specified file
        Prints the size at the beginning if desired (to conform to XYZ format)
        """
        out = ''
        if style == 'xyz':
            if label:
                out += f'{len(self)}\n\n'
            out += f'{self}'
        elif style == 'latex':
            header = f'{len(self)}\\\\\n'
            line_form = '{:<2}' + ' {:> 13.6f}' * 3
            atoms = [line_form.format(atom, *xyz) for atom, xyz in self]
            atoms = '\n'.join(atoms)
            out = '\\begin{verbatim}\n' + atoms + '\n\\end{verbatim}'
        else:
            raise SyntaxError('Invalid style')
        with open(outfile, 'w') as f:
            f.write(out)
