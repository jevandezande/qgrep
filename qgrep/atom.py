
# noinspection PyPep8
short_to_long_names = {'X': 'Dummy',
    'H': 'Hydrogen', 'He': 'Helium',
    'Li': 'Lithium', 'Be': 'Beryllium',
        'B': 'Boron', 'C': 'Carbon', 'N': 'Nitrogen', 'O': 'Oxygen', 'F': 'Fluorine', 'Ne': 'Neon',
    'Na': 'Sodium', 'Mg': 'Magnesium',
        'Al': 'Aluminum', 'Si': 'Silicon', 'P': 'Phosphorus', 'S': 'Sulfur', 'Cl': 'Chlorine', 'Ar': 'Argon',
    'K': 'Potassium', 'Ca': 'Calcium',
        'Sc': 'Scandium', 'Ti': 'Titanium', 'V': 'Vanadium', 'Cr': 'Chromium', 'Mn': 'Manganese', 'Fe': 'Iron', 'Co': 'Cobalt', 'Ni': 'Nickel', 'Cu': 'Copper', 'Zn': 'Zinc',
        'Ga': 'Gallium', 'Ge': 'Germanium', 'As': 'Arsenic', 'Se': 'Selenium', 'Br': 'Bromine', 'Kr': 'Krypton',
    'Rb': 'Rubidium', 'Sr': 'Strontium',
        'Y': 'Yttrium', 'Zr': 'Zirconium', 'Nb': 'Niobium', 'Mo': 'Molybdenum', 'Tc': 'Technetium', 'Ru': 'Ruthenium', 'Rh': 'Rhodium', 'Pd': 'Palladium', 'Ag': 'Silver', 'Cd': 'Cadmium',
        'In': 'Indium', 'Sn': 'Tin', 'Sb': 'Antimony', 'Te': 'Tellurium', 'I': 'Iodine', 'Xe': 'Xenon',
    'Cs': 'Cesium', 'Ba': 'Barium',
        'La': 'Lanthanum', 'Ce': 'Cerium', 'Pr': 'Praseodymium', 'Nd': 'Neodymium', 'Pm': 'Promethium', 'Sm': 'Samarium', 'Eu': 'Europium', 'Gd': 'Gadolinium', 'Tb': 'Terbium', 'Dy': 'Dysprosium', 'Ho': 'Holmium', 'Er': 'Erbium', 'Tm': 'Thulium', 'Yb': 'Ytterbium', 'Lu': 'Lutetium', 'Hf': 'Hafnium', 'Ta': 'Tantalum', 'W': 'Tungsten', 'Re': 'Rhenium', 'Os': 'Osmium', 'Ir': 'Iridium', 'Pt': 'Platinum', 'Au': 'Gold', 'Hg': 'Mercury',
        'Tl': 'Thallium', 'Pb': 'Lead', 'Bi': 'Bismuth', 'Po': 'Polonium', 'At': 'Astatine', 'Rn': 'Radon',
    'Fr': 'Francium', 'Ra': 'Radium',
        'Ac': 'Actinium', 'Th': 'Thorium', 'Pa': 'Protactinium', 'U': 'Uranium', 'Np': 'Neptunium', 'Pu': 'Plutonium', 'Am': 'Americium', 'Cm': 'Curium', 'Bk': 'Berkelium', 'Cf': 'Californium', 'Es': 'Einsteinium', 'Fm': 'Fermium', 'Md': 'Mendelevium', 'No': 'Nobelium', 'Lr': 'Lawrencium', 'Rf': 'Rutherfordium', 'Db': 'Dubnium', 'Sg': 'Seaborgium', 'Bh': 'Bohrium', 'Hs': 'Hassium', 'Mt': 'Meitnerium', 'Ds': 'Darmstadtium', 'Rg': 'Roentgenium', 'Cp': 'Copernicium',
        'Uut': 'Ununtrium', 'Uuq': 'Ununquadium', 'Uup': 'Ununpentium', 'Uuh': 'Ununhexium', 'Uus': 'Ununseptium', 'Uuo': 'Ununoctium'
}
long_to_short_names = dict((reversed(item) for item in short_to_long_names.items()))


def ensure_short_atom_name(atom):
    atom = atom.title()
    if atom in long_to_short_names:
        atom = long_to_short_names[atom]
    elif atom not in short_to_long_names:
        raise ValueError(f'Invalid atom name: {atom}')
    return atom


def ensure_long_atom_name(atom):
    atom = atom.title()
    if atom in short_to_long_names:
        atom = short_to_long_names[atom]
    elif atom not in long_to_short_names:
        raise ValueError(f'Invalid atom name: {atom}')
    return atom


atomic_numbers = {'X': 0,
    'H': 1, 'He': 2,
        'Li': 3, 'Be': 4,
        'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18,
    'K': 19, 'Ca': 20,
        'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30,
        'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36,
    'Rb': 37, 'Sr': 38,
        'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48,
        'In': 49, 'Sn': 50, 'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54,
    'Cs': 55, 'Ba': 56,
        'La': 57, 'Ce': 58, 'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80,
        'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85, 'Rn': 86,
    'Fr': 87, 'Ra': 88,
        'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99, 'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105, 'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109, 'Ds': 110, 'Rg': 111, 'Cp': 112,
        'Uut': 113, 'Uuq': 114, 'Uup': 115, 'Uuh': 116, 'Uus': 117, 'Uuo': 118,
}
numbers_atomic = dict((reversed(item) for item in atomic_numbers.items()))


am_list = [0.0, 1.00782503207, 4.00260325415, 7.016004548, 9.012182201, 11.009305406,  12, 14.00307400478, 15.99491461956, 18.998403224, 19.99244017542,  22.98976928087, 23.985041699, 26.981538627, 27.97692653246, 30.973761629,  31.972070999, 34.968852682, 39.96238312251, 38.963706679, 39.962590983,  44.955911909, 47.947946281, 50.943959507, 51.940507472, 54.938045141,  55.934937475, 58.933195048, 57.935342907, 62.929597474, 63.929142222,  68.925573587, 73.921177767, 74.921596478, 79.916521271, 78.918337087,  85.910610729, 84.911789737, 87.905612124, 88.905848295, 89.904704416,  92.906378058, 97.905408169, 98.906254747, 101.904349312, 102.905504292,  105.903485715, 106.90509682, 113.90335854, 114.903878484, 119.902194676,  120.903815686, 129.906224399, 126.904472681, 131.904153457, 132.905451932,  137.905247237, 138.906353267, 139.905438706, 140.907652769, 141.907723297,  144.912749023, 151.919732425, 152.921230339, 157.924103912, 158.925346757,  163.929174751, 164.93032207, 165.930293061, 168.93421325, 173.938862089,  174.940771819, 179.946549953, 180.947995763, 183.950931188, 186.955753109,  191.96148069, 192.96292643, 194.964791134, 196.966568662, 201.970643011,  204.974427541, 207.976652071, 208.980398734, 208.982430435, 210.987496271,  222.017577738, 222.01755173, 228.031070292, 227.027752127, 232.038055325,  231.03588399, 238.050788247, 237.048173444, 242.058742611, 243.06138108,  247.07035354, 247.07030708, 251.079586788, 252.082978512, 257.095104724,  258.098431319, 255.093241131, 260.105504, 263.112547, 255.107398, 259.114500,  262.122892, 263.128558, 265.136151, 281.162061, 272.153615, 283.171792, 283.176451,  285.183698, 287.191186, 292.199786, 291.206564, 293.214670]
atomic_masses = dict(zip(range(len(am_list)), am_list))


class Atom:
    """
    Simple atom class
    """
    def __init__(self, name, *xyz):
        """
        :param name: the name or atomic number of the desired atom
        :param xyz: the xyz coordinates of the atom
        """
        if isinstance(name, int):
            if 0 <= name and name < len(self.atomic_numbers):
                self.atomic_number = name
        else:
            self.atomic_number = Atom.atomic_number(name)

        self.check_xyz(xyz)
        self.xyz = xyz

    def __str__(self):
        return f'{name:<4}' + (' {:> 13.8f}' * 3).format(*xyz)

    def check_name(self, name):
        if name not in short_to_long_names or name not in long_to_short_names:
            raise SyntaxError(f'Invalid atom name: {name}')

    def check_xyz(self, xyz):
        if len(xyz) != 3:
            raise SyntaxError(f'Improper number of coordinates: {len(xyz)}')
        for q in xyz:
            if not isinstance(q, (float, int)):
                raise SyntaxError(f'Coordinates must be numbers, got: {type(q)}')

    @staticmethod
    def convert_name(name):
        name = name.title()
        if name in short_to_long_names:
            return short_to_long_names[name]
        elif name in long_to_short_names:
            return long_to_short_names[name]
        else:
            raise SyntaxError(f'Invalid atom: {name}')

    @staticmethod
    def atomic_number(name):
        if name.isdigit():
            return numbers_atomic[int(name)]

        if name in short_to_long_names:
            return atomic_numbers[name]
        elif name in long_to_short_names:
            return atomic_numbers[Atom.convert_name(name)]
        else:
            raise SyntaxError(f'Invalid atom name: {name}')

    @property
    def mass(self):
        return atomic_masses[self.atomic_number]

    @property
    def name(self):
        return numbers_atomic[self.atomic_number]
