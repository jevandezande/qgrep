import helper
import importlib


class Molecule(object):
    def __init__(self, geom=None, name=None):
        # self.geom is a list of lists where the first column corresponds to the element
        # and the others to x, y, and z respectively
        self.geom = None
        if geom is not None and Molecule.check_geom(geom):
            self.geom = geom
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
            print('hey')
            return False
        if self.geometry != self.geometry:
            print('he2y')
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
        if len(geom) == 0 or len(geom[0]) == 0:
            raise SyntaxError("No atoms in geometry")
        for atom in geom:
            Molecule.check_atom(atom)

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
        elif program == 'zmatrix':
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
