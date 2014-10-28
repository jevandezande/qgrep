import helper
import importlib


class Molecule(object):
    def __init__(self, geom=[], zmatrix=[], name=None):
        # self.geom is a list of lists where the first column corresponds to the element
        # and the others to x, y, and z respectively
        self.geom = []
        self.zmat = []
        if len(geom) > 0 and Molecule.check_geom(geom):
            self.geom = geom
        if len(zmatrix) > 0 and Molecule.check_zmatrix(zmatrix):
            self.zmat = zmatrix
        self.name = None

    def __len__(self):
        """Return the number of atoms in the molecule"""
        return len(self.geom)

    def __str__(self):
        """Returns a string of the cartesion geometry, filling out positions with zeros and spaces as needed"""
        return '\n'.join([('{:<8}' + ' {:> 15.8f}'*3).format(*line) for line in self.geom])

    def __getitem__(self, i):
        """Returns the ith atom"""
        return self.geom[i]

    def __setitem__(self, i, atom):
        """Sets the ith atom"""
        Molecule.check_atom(atom)
        self.geom[i] = list(atom)

    def __delitem__(self, i):
        """Deletes the ith atom"""
        del self.geom[i]

    def __eq__(self, other):
        if not isinstance(other, Molecule):
            return False
        if self.geometry != self.geometry:
            return False
        return True

    def insert(self, i, atom):
        """Insert the atom in the specified position"""
        Molecule.check_atom(atom)
        self.geom.insert(i, list(atom))

    @property
    def geometry(self):
        """Return the geometry"""
        return self.geom

    @geometry.setter
    def geometry(self, geom):
        """Set the geometry"""
        Molecule.check_geom(geom)
        self.geom = geom

    def append(self, atom):
        """Append atom to geometry"""
        Molecule.check_atom(atom)
        self.geom.append(list(atom))

    @staticmethod
    def check_atom(atom):
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
    def check_geom(geom):
        """Checks if the given geometry is valid, raises a syntax error if it is not"""
        if len(geom) == 0:
            return True
        for atom in geom:
            if not Molecule.check_atom(atom):
                return False

        return True

    @staticmethod
    def check_zmatrix(zmatrix):
        """Checks if the given zmatrix is valid, raises a syntax error if not"""
        if len(zmatrix) == 0:
            return True
        if len(zmatrix[0]) != 1:
            raise SyntaxError("Only need one atom on first line: " + str(zmatrix[0]))
        if not isinstance(zmatrix[0][0], str):
            raise SyntaxError("Atom name must be a string. {} is not a valid atom name".format(zmatrix[0]))
        if len(zmatrix) > 1 and len(zmatrix[1]) != 3:
            raise SyntaxError("Need atom, its connection, and distance on second line: " + str(zmatrix[1]))
        name, atom1, distance = zmatrix[1]
        if not isinstance(name, str) or not isinstance(atom1, int) or not isinstance(distance, (int, float)):
            raise SyntaxError("Invalid specification of second atom: {}".format(zmatrix[1]))
        if len(zmatrix) > 2 and len(zmatrix[2]) != 5:
            raise SyntaxError("Need atom, its connection, and distance on second line: " + str(zmatrix[1]))
        name, atom1, distance, atom2, angle = zmatrix[2]
        if not isinstance(name, str) or not isinstance(atom1, int) or not isinstance(distance, (int, float)) or \
                not isinstance(atom2, int) or not isinstance(angle, (int, float)):
            raise SyntaxError("Invalid specification of second atom: {}".format(zmatrix[1]))
        for i, atom in enumerate(zmatrix[3:], start=4):
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

        return True

    @staticmethod
    def read_geometry(infile="geom.xyz"):
        """Read the geometry from a file, currectly only supports XYZ files"""
        lines, program = helper.read(infile)
        if program is None:
            # Attempt to read as an XYZ file
            if lines[0].strip().isdigit():
                # Strip off geom length if provided
                lines = lines[2:]
            geom = []
            for line in lines:
                atom, x, y, z = line.split()
                geom.append([atom, float(x), float(y), float(z)])
        elif program == 'zmatrixrix':
            raise SyntaxError('Zmatrices are not yet supported')
        else:
            # TODO, make get_geom actually output a molecule
            mod = importlib(program)
            geom = mod.get_geom()
        return geom

    def read(self, infile="geom.xyz"):
        """Read (and set) the geometry"""
        self.geom = Molecule.read_geometry(infile)

    def write(self, outfile="geom.xyz", size=False):
        """Writes the geometry to the specified file, includes the size if desired (to conform to XYZ format)"""
        out = ''
        if size:
            out += '{}\n\n'.format(len(self))
        out += str(self)
        with open(outfile, 'w') as f:
            f.write(out)
