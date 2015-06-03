"""Source for all nbo relate functions"""
import re
import numpy as np


class NPA():
    """Natural Population Analysis class"""

    def __init__(self, lines):
        self.atoms, self.npa = self.read(lines)
    
    def __str__(self):
        ret = 'Atom  Charge     Core     Valence   Rydberg   Total\n'
        line_form = '{:<2} ' + '  {: >8.5f}'*5 + '\n'
        for atom, pop in zip(self.atoms, self.npa):
            ret += line_form.format(atom, *pop)
        return ret

    @staticmethod
    def read(lines):
        """Read the natural population analysis

 Summary of Natural Population Analysis:
                                     Natural Population 
             Natural    --------------------------------------------- 
  Atom No    Charge        Core      Valence    Rydberg      Total 
 -------------------------------------------------------------------- 
   Fe  1   -0.57877     17.97641     8.54310    0.05926    26.57877 
    C  2    0.60637      1.99951     3.34225    0.05187     5.39363 
    O  3   -0.42097      1.99976     6.38932    0.03189     8.42097
...
"""

        # Find the NPA Section
        start = 0
        for i, line in enumerate(lines):
            if line == ' Summary of Natural Population Analysis:\n':
                start = i + 6
                break
        if start == 0:
            raise Exception('Unable to find the start of NPA analysis')

        npa = []
        atoms = []
        # Interpret the NPA
        for line in lines[start:]:
            if line[:50] == " " + "="*49:
                break
            atom, num, *others = line.split()
            atoms.append(atom)
            num = int(num)
            charge, core, valence, rydberg, total, *ns = map(float, others)
            npa.append([charge, core, valence, rydberg, total])
        return atoms, np.array(npa)


class NBO():
    """Natural Bond Orbital class"""

    def __init__(self, lines):
        self.nbos = self.read(lines)

    def __str__(self):
        ret = 'Bond #, Bond Order, type, sub bond #, atom1, atom1 #, atom2,' \
              'atom2 #\n'
        nbo_form = ' {:>3d}     {:6.5f}     {:<3s}      {:d}        {:<2s}' \
                   '     {:>3d}       {:<2s}    {:>3d}\n'
        for nbo in self.nbos:
            ret += nbo_form.format(*nbo)
        return ret

    @staticmethod
    def read(lines):
        # noinspection PyPep8
        """
        Read the Natural Bond Orbital Analysis

   1. (1.92050) BD ( 1)Fe  1- C  2
               ( 32.17%)   0.5672*Fe  1 s( 33.10%)p 0.00(  0.02%)d 2.02( 66.88%)
                                                  f 0.00(  0.00%)
                                         0.0000  0.0000 -0.0044  0.5753  0.0022
    ...
  36. (2.00000) CR ( 1)Fe  1             s(100.00%)
                                         1.0000 -0.0000  0.0000 -0.0000  0.0000
    ...
  72. (1.79971) LP ( 1)Fe  1             s(  0.00%)p 0.00(  0.00%)d 1.00(100.00%)
                                                  f 0.00(  0.00%)
                                         0.0000  0.0000 -0.0000  0.0001 -0.0001
    ...
  90. (0.01241) RY*( 1)Fe  1             s(  0.00%)p 1.00(  3.05%)d31.77( 96.89%)
                                                  f 0.02(  0.06%)
                                         0.0000  0.0000  0.0000  0.0000  0.0005
    ...
 618. (0.67669) BD*( 1)Fe  1- C  2
               ( 67.83%)   0.8236*Fe  1 s( 33.10%)p 0.00(  0.02%)d 2.02( 66.88%)
                                                  f 0.00(  0.00%)
    ...
        """
        for i, line in enumerate(lines):
            if line == '     (Occupancy)   Bond orbital/ Coefficients/ Hybrids\n':
                start = i + 2
                break

        atom1 = 'C'
        num1 = 26
        atom2 = 'O'
        num2 = 27
        types = '(BD |BD\*|CR |LP |RY |RY\*)'

        #atom_label_1 = atom1.rjust(2) + str(num1).rjust(3)
        atom_label = ' ?(\w+) +(\d+)'
        #atom_label_2 = atom2.rjust(2) + str(num2).rjust(3)

        regex = r'(\d+)\. \((\d\.\d*)\) {}\( ?(\d+)\){}-{}'

        regex = regex.format(types, atom_label, atom_label)

        # TODO: Actually use starting coordinates
        out_string = open('output.dat').read()
        results = re.findall(regex, out_string)

        nbos = []
        for nbo in results:
            bond_num, b_order, b_type, b_sub, a1, a1_n, a2, a2_n = nbo
            nbos.append([int(bond_num), float(b_order), str(b_type), int(b_sub),
                         str(a1), int(a1_n), str(a2), int(a2_n)])

        return nbos

