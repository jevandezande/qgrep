import helper
import importlib


class Molecule(object):
    def __init__(self, geom=[], geom_type=None, name=None):
        """
        Simple molecule class that includes zmatrix and cartesian (xyz) coordinates
        Geometries:
            XYZ
                List of lists where the first column corresponds to the element
                and the others to x, y, and z respectively
            ZMATRIX
                List of list where the first column corresponds to the element
                and the others to atom1, distance, atom2, angle, atom3, dihedral
        """
        self.xyz = None
        self.zmat = None
        if not geom_type is None:
            if geom_type == 'xyz':
                self.geom_type = 'xyz'
                Molecule.check_xyz(geom)
                self.xyz = geom
            elif geom_type == 'zmat':
                self.geom_type = 'zmat'
                Molecule.check_zmatrix(geom)
                self.zmat = geom
            else:
                raise SyntaxError("Invalid geometry type, must be either 'xyz' or 'zmat'.")
        elif len(geom) > 0 and len(geom[0]) == 1:
            self.geom_type = 'zmat'
            Molecule.check_zmatrix(geom)
            self.zmat = geom
        else:
            self.geom_type = 'xyz'
            Molecule.check_xyz(geom)
            self.xyz = geom

        self.name = None

    def __len__(self):
        """Return the number of atoms in the molecule"""
        if self.geom_type == 'zmat':
            return len(self.zmat)
        return len(self.xyz)

    def __str__(self):
        """Returns a string of the geometry, filling out positions with zeros and spaces as needed"""
        if self.geom_type == 'zmat':
            out = self.zmat[0]
            if len(self.zmat) > 1:
                out += '\n{:<8} {:>4d} {:> 15.8f}'.format(*self.zmat[1])
            if len(self.zmat) > 2:
                out += ('\n{:<8}' + ' {:>4d} {:> 15.8f}'*2).format(*self.zmat[2])
            for atom in self.zmat[3:]:
                out += ('\n{:<8}' + ' {:>4d} {:> 15.8f}'*3).format(*atom)
            return out
        return '\n'.join([('{:<8}' + ' {:> 15.8f}'*3).format(*line) for line in self.xyz])

    def __getitem__(self, i):
        """Returns the ith atom"""
        if self.geom_type == 'zmat':
            return self.zmat[i]
        return self.xyz[i]

    def __setitem__(self, i, atom):
        """Sets the ith atom"""
        if self.geom_type == 'zmat':
            Molecule.check_zmatrix_atom(atom, i)
        Molecule.check_xyz_atom(atom)
        self.xyz[i] = list(atom)

    def __delitem__(self, i):
        """Deletes the ith atom"""
        if self.geom_type == 'zmat':
            del self.zmat[i]
        del self.xyz[i]

    def __eq__(self, other):
        if not isinstance(other, Molecule):
            return False
        if self.geometry != other.geometry:
            return False
        return True

    def insert(self, i, atom):
        """Insert the atom in the specified position"""
        if self.geom_type == 'zmat':
            Molecule.check_zmatrix_atom(atom, i)
            self.xyz.insert(i, list(atom))
        else:
            Molecule.check_xyz_atom(atom)
            self.xyz.insert(i, list(atom))

    @property
    def geometry(self):
        """Return the geometry"""
        if self.geom_type == 'zmat':
            return self.zmat
        return self.xyz

    @geometry.setter
    def geometry(self, geom):
        """Set the geometry"""
        geom_type = Molecule.check_type(geom)
        if geom_type == 'xyz':
            self.geom_type = 'xyz'
            self.xyz = geom
        elif geom_type == 'zmat':
            self.geom_type = 'zmat'
            self.xyz = geom
        else:
            raise SyntaxError("Invalid geometry.")

    @staticmethod
    def check_type(geom):
        """Determine the geometry type, and return a string corresponding to it. If not a valid format, returns None"""
        try:
            Molecule.check_xyz(geom)
            return 'xyz'
        except SyntaxError:
            try:
                Molecule.check_zmatrix(geom)
                return 'zmat'
            except SyntaxError:
                return None

    def append(self, atom, i=0):
        """Append atom to geometry"""
        if self.geom_type == 'zmat':
            Molecule.check_zmatrix_atom(atom, i)
            self.xyz.append(list(atom))
        else:
            Molecule.check_xyz_atom(atom)
            self.xyz.append(list(atom))

    @staticmethod
    def check_xyz_atom(atom):
        """Check if an atom is properly formatted, raises a syntax error if it is not"""
        name, *positions = atom
        if not isinstance(name, str):
            raise SyntaxError("Atom name must be a string: {}".format(name))
        if len(positions) != 3:
            raise SyntaxError("Only 3 coordinates supported.")
        for x in positions:
            if not isinstance(x, (int, float)):
                raise SyntaxError("Positions must be numbers: {}".format(x))
        return True

    @staticmethod
    def check_xyz(xyz):
        """Checks if the given xyz geometry is valid, raises a syntax error if it is not"""
        if len(xyz) == 0:
            return True
        for atom in xyz:
            Molecule.check_xyz_atom(atom)

        return True

    @staticmethod
    def check_zmatrix_atom(atom, i):
        if i == 1:
            if len(atom) != 1:
                raise SyntaxError("Only need one atom on first line: " + str(atom))
            if not isinstance(atom[0], str):
                raise SyntaxError("Atom name must be a string. {} is not a valid atom name".format(atom[0]))
        elif i == 2:
            if len(atom) != 3:
                raise SyntaxError("Need atom, its connection, and distance: " + str(atom))
            name, atom1, distance = atom
            if not isinstance(name, str) or not isinstance(atom1, int) or not isinstance(distance, (int, float)):
                raise SyntaxError("Invalid specification of second atom: {}".format(atom))
        elif i == 3:
            if len(atom) != 5:
                raise SyntaxError("Need atom, its connection, and distance on second line: " + str(atom))
            name, atom1, distance, atom2, angle = atom
            if not isinstance(name, str) or not isinstance(atom1, int) or not isinstance(distance, (int, float)) or \
                    not isinstance(atom2, int) or not isinstance(angle, (int, float)):
                raise SyntaxError("Invalid specification of atom: {}".format(atom))
        elif i > 3 and isinstance(i, int):
            if len(atom) != 7:
                raise SyntaxError("Incorrect number of values, excpecting 6 but got " + str(len(atom)))
            if not isinstance(atom[0], str):
                raise SyntaxError("Atom name must be a string. {} is not a valid atom name".format(atom[0]))
            atoms = atom[1::2]
            for a in atoms:
                if not isinstance(a, int):
                    raise SyntaxError("Atoms must be specified with a number.")
                if a >= i:
                    # Using indexing starting at 1
                    raise SyntaxError("Cannot use atoms appearing after the current atom.")
            params = atom[2::2]
            for p in params:
                if not isinstance(p, (int, float)):
                    raise SyntaxError("Distance, angle, and dihedral must be specified with a number: {}".format(atom))
        else:
            raise SyntaxError("Index must be an integer greater than one.")

    @staticmethod
    def check_zmatrix(zmatrix):
        """Checks if the given zmatrix is valid, raises a syntax error if not"""
        for i, atom in enumerate(zmatrix, start=1):
            Molecule.check_zmatrix_atom(atom, i)

        return True

    @staticmethod
    def read_xyz(infile="geom.xyz"):
        """Read the xyzetry from a file, currectly only supports XYZ files"""
        lines, program = helper.read(infile)
        if program is None:
            # Attempt to read as an XYZ file
            if lines[0].strip().isdigit():
                # Strip off length if provided
                lines = lines[2:]
            xyz = []
            for line in lines:
                atom, x, y, z = line.split()
                xyz.append([atom, float(x), float(y), float(z)])
        elif program == 'zmatrix':
            raise SyntaxError('Zmatrices are not yet supported')
        else:
            # TODO, make get_xyz actually output a molecule
            mod = importlib(program)
            xyz = mod.get_geom()
        return xyz

    def read(self, infile="geom.xyz"):
        """Read (and set) the xyzetry"""
        self.xyz = Molecule.read_xyz(infile)

    def write(self, outfile="geom.xyz", label=True):
        """
        Writes the geometry to the specified file
        If an xyz geometry, prints the size at the beginning if desired (to conform to XYZ format)
        If a zmat, prints  the zmatrix label at the beginning (#ZMATRIX) (to conform to JMol zmatrix format)
        """
        out = ''
        if label:
            if self.geom_type == 'zmat':
                out += '#ZMATRIX\n\n'
            else:
                out += '{}\n\n'.format(len(self))
        out += str(self)
        with open(outfile, 'w') as f:
            f.write(out)
