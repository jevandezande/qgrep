from qgrep import helper
import importlib


class Molecule(object):
    def __init__(self, geom=None, name=None):
        """
        Simple molecule class

        :param geom: List of lists where the first column corresponds to the
            element and the others to x, y, and z respectively
        """
        if geom is None:
            geom = []
        else:
            Molecule.check_geom(geom)
        self.geom = geom

        self.name = name

    def __len__(self):
        """Return the number of atoms in the molecule"""
        return len(self.geom)

    def __str__(self):
        """
        Returns a string of the geometry, filling out positions with zeros and
        spaces as needed
        """
        return '\n'.join([('{:<4}' + ' {:> 13.8f}' * 3).format(*atom) for atom in self.geom])

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
        if self.geom != other.geom:
            return False
        if self.name != other.name:
            return False
        return True

    def insert(self, i, atom):
        """Insert the atom in the specified position"""
        Molecule.check_atom(atom)
        self.geom.insert(i, list(atom))

    @property
    def geom(self):
        """Return the geometry
        Use self._geom to store the geomtery so extra checks can be added"""
        return self._geom

    @geom.setter
    def geom(self, geom):
        """Set the geometry"""
        Molecule.check_geom(geom)
        self._geom = geom

    def append(self, atom, i=0):
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
        for atom in geom:
            Molecule.check_atom(atom)

        return True

    @staticmethod
    def read_geom(infile="geom.xyz"):
        """Read the geometry from a file, currectly only supports XYZ files"""
        lines, program = helper.read(infile)
        if program:
            if program == 'zmatrix':
                raise SyntaxError('Zmatrices are not yet supported')
            mod = importlib.import_module('qgrep.' + program)
            lines = mod.get_geom(lines)

        # Attempt to read as an XYZ file
        if lines[0].strip().isdigit():
            # Strip off length if provided
            lines = lines[2:]
        geom = []
        for line in lines:
            if line.strip() == '':
                continue
            atom, x, y, z = line.split()
            geom.append([atom, float(x), float(y), float(z)])

        return geom

    def read(self, infile="geom.xyz"):
        """Read (and set) the geometry"""
        self.geom = Molecule.read_geom(infile)

    def write(self, outfile="geom.xyz", label=True, style='xyz'):
        """
        Writes the geometry to the specified file
        Prints the size at the beginning if desired (to conform to XYZ format)
        """
        out = ''
        if style == 'xyz':
            if label:
                out += '{}\n\n'.format(len(self))
            out += str(self)
        elif style == 'latex':
            header = '{}\\\\\n'.format(len(self))
            if self.name:
                header = self.name + '\\\\\n' + header
            line_form = '{:<2}' + ' {:> 13.6f}' * 3
            atoms = [line_form.format(atom, *pos) for atom, *pos in self.geom]
            atoms = '\n'.join(atoms)
            #out = header + '\\begin{verbatim}\n' + atoms + '\n\\end{verbatim}'
            out = '\\begin{verbatim}\n' + atoms + '\n\\end{verbatim}'
        else:
            raise SyntaxError('Invalid style')
        with open(outfile, 'w') as f:
            f.write(out)
