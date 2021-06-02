import re
from collections import Counter
from itertools import chain

import networkx as nx
import numpy as np
import psi4
import py3Dmol
import pyscf
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import SimilarityMaps
from rdkit.Chem.rdchem import BondType
from rdkit.Chem.rdMolDescriptors import GetMorganFingerprint
from rdkit.SimDivFilters.rdSimDivPickers import MaxMinPicker

ATOMIC_NUMBERS = ('X', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og')

ions = [ATOMIC_NUMBERS[i] for i in chain([3, 4, 11, 12], range(19, 32), range(37, 51), range(55, 85), range(87, 118))]


def remove_charges(smiles):
    """
    Removes any charges in a SMILES string.

    :param smiles: the SMILES string
    :return: a new SMILES string
    """
    return re.sub('\[([^]]+)[+-]\]', '[\g<1>]', smiles)


def remove_ions(smiles):
    """
    Removes any chunks of a SMILES string if it contains an atom identified as an ion.

    :param smiles: the SMILES string
    :return: a new SMILES string
    """
    new_smiles = []
    for chunk in smiles.split('.'):
        for ion in ions:
            if ion in chunk:
                break
        else:
            new_smiles.append(chunk)
    return '.'.join(new_smiles)

def conjugated_subgraphs(mol):
    """
    Determine the sets of connected subgraphs of conjugated bonds in a molecule.

    Warning: a solitary double bond does not count as a conjugated bond
        e.g. C-C-C-C=C-C-C-C=C yields nothing

    :param mol: an RDKit.mol
    :yield: conjugated sets of atoms
    """
    G = nx.Graph()
    edges = ((bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()) for bond in mol.GetBonds() if bond.GetIsConjugated())
    G.add_edges_from(edges)
    yield from nx.connected_components(G)


def multiple_conjugated_subgraphs(mol, threshold=5):
    """
    Determine if there are multiple connected subgraphs of conjugated bonds in a molecule.
    See :conjugated_subgraphs():

    :param mol: an RDKit.mol
    :param threshold: threshold for small groups (e.g. C-C(=O)OH == 3)
    :return: True or False
    """
    lengths = list(len(sg) for sg in conjugated_subgraphs(mol))
    if len(lengths) < 2:
        return False
    return sorted(lengths)[-2] > threshold


def num_conjugated_subgraphs(mol):
    """
    Determine the number of connected subgraphs of conjugated bonds in a molecule.
    See :conjugated_subgraphs():

    :param mol: an RDKit.mol
    :return: max conjugation of bonds, 0 if no conjugation
    """
    return len(list(conjugated_subgraphs(mol)))


def largest_conjugated_subgraph(mol):
    """
    Determine the size of the largest connected subgraph of conjugated bonds in a molecule.
    See :conjugated_subgraphs():

    Warning: single bonds count as a conjugated bond if between unsaturation,
        thus the count is ≈2x larger than expected.
        e.g. C=C-C=C-C=C yields a 5, not 3

    :param mol: an RDKit.mol
    :return: max conjugation of bonds, 0 if no conjugation
    """
    conj = list(conjugated_subgraphs(mol))
    if conj:
        return max(map(len, conj))
    return 0


def count_bond_types(mol):
    """
    Count the number of each type of bond in an atom.

    :param mol: an RDKit.Mol
    :return: tuple of bond types
    """
    counts = Counter(bond.GetBondType() for bond in mol.GetBonds())
    # Defaults to 0 for non-existing arguments
    return (
        counts[BondType.SINGLE],
        counts[BondType.DOUBLE],
        counts[BondType.TRIPLE],
        counts[BondType.AROMATIC],
        sum(bond.GetIsConjugated() for bond in mol.GetBonds()),
        largest_conjugated_subgraph(mol),
    )


def generate_conformations(mol, numConfs=10):
    """
    Generate 3D conformations

    :param mol: an RDKit.mol
    :return: molecule and lowest energy conformation index
    """
    mol = AllChem.AddHs(mol)
    if not AllChem.EmbedMultipleConfs(mol, numConfs=numConfs):
        return np.nan, -1
        # Sometimes RandomCoords work better for conformer generation of large molecules
        if not AllChem.EmbedMultipleConfs(mol, numConfs=numConfs, useRandomCoords=True):
            print(1)

    results = np.array(AllChem.MMFFOptimizeMoleculeConfs(mol, numThreads=0, maxIters=10000))
    minConf = np.argmin(results[:, 1])
    energy = results[minConf][1]

    return mol, int(minConf), energy


def make_geometry(mol, confId, atomicNum=False):
    """
    Makes a geometry string from the designated conformer.

    :param mol: an RDKit.Mol
    :param confId: the conformer to select.
    :param atomicNum: return with atomic number, else uses symbol
    :return: geometry string, contains atomic numbers instead of symbols
    """
    nums = [atom.GetAtomicNum() for atom in mol.GetAtoms()]
    if not atomicNum:
        symbols = [ATOMIC_NUMBERS[num] for num in nums]
    else:
        symbols = nums
    mol_str = ''
    for num, (x, y, z) in zip(symbols, mol.GetConformer(confId).GetPositions()):
        mol_str += f'{num:<2} {x} {y} {z}\n'
    return mol_str.strip()


def make_psi4_geometry(geom, confId=None):
    """
    Makes a psi4 geometry object.

    :param geom: an RDKit.Mol or a string
    :param confId: the conformer to select, if needed
    :return: psi4 geometry
    """
    if not isinstance(geom, str):
        assert confId
        geom = make_geometry(geom, confId)

    return psi4.geometry(geom)


def energy(geom, confId, method='HF-3C', **kwargs):
    """
    Finds the energy of a given molecule

    :param geom: an RDKit.Mol or a string
    :param confId: the ID of the conformer to optimize
    :param method: the PSI4 method to calculate the HOMO and LUMO
    :return: wavefunction (energy is available under wavefunction.energy)
    """
    try:
        geom = make_psi4_geometry(geom, confId)
        psi4.activate(geom)
        psi4.core.IO.set_default_namespace(str(id(geom)))

        psi4.core.set_global_option("MAXITER", 1000)

        return psi4.energy(method, return_wfn=True, **kwargs)[1]
    except Exception as e:
        print(e)

    return np.nan


def homo_lumo(geom, confId=None, method='HF-3C', **kwargs):
    """
    Finds the HOMO and LUMO of a given molecule

    :param geom: the target molecule
    :param confId: the ID of the conformer to optimize, if needed
    :param method: the method to calculate the HOMO and LUMO
    :return: wavefunction, HOMO, LUMO
    """
    wfn = energy(geom, confId, method, **kwargs)
    if wfn:
        try:
            orbs = wfn.epsilon_a_subset('AO', 'ALL').np
            return wfn, orbs[wfn.nalpha() - 1], orbs[wfn.nalpha()]
        except:
            pass
    return np.nan, np.nan, np.nan


def optimize(geom, confId=None, method='HF-3C', **kwargs):
    """
    Optimizes the given conformation.

    :param mol: an RDKit.Mol or a string
    :param confId: the ID of the conformer to optimize, if needed
    :param method: the PSI4 method to use
    :return: wavefunction (energy is available under wavefunction.energy)
    """
    try:
        geom = make_psi4_geometry(geom, confId)
        psi4.activate(geom)
        psi4.core.IO.set_default_namespace(str(id(geom)))

        psi4.core.set_global_option("MAXITER", 1000)

        return psi4.optimize(method, return_wfn=True, **kwargs)[1]
    except Exception as e:
        pass

    return np.nan


def show_3D_mol(mol, confId):
    """
    Shows a molecule in 3D
    :param: an RDKit.mol
    :param confId: the IR of the conformer to show
    :return: molBlock
    """
    mb = Chem.MolToMolBlock(mol, confId=confId)

    p = py3Dmol.view()
    p.addModel(mb,'sdf')
    p.setStyle({'stick':{}})
    p.setBackgroundColor('0xeeeeee')
    p.zoomTo()
    p.show()

    return mb


def gasteiger_charges(mol):
    """
    Compute and plot the Gasteiger charges

    :param mol: an RDKit.Mol
    :return: charges, plot of charges
    """
    AllChem.ComputeGasteigerCharges(mol)
    return [mol.GetAtomWithIdx(i).GetDoubleProp('_GasteigerCharge') for i in range(mol.GetNumAtoms())]


def plot_vals(mol, vals, colorMap='jet', contourLines=10):
    """
    Plot values on a SimilarityMap

    :param mol: an RDKit.mol
    :return: SimilarityMap
    """
    return SimilarityMaps.GetSimilarityMapFromWeights(mol, vals, colorMap=colorMap, contourLines=contourLines)


def get_mo_view(mol, wfn):
    gridspace = 0
    homo_idx = wfn.nalpha()
    lumo_idx = homo_idx + 1
    self.psi4.set_options({
        "cubeprop_tasks": ['ESP', 'FRONTIER_ORBITALS', 'Density', 'DUAL_DESCRIPTOR'],
        "cubic_grid_spacing": [gridspace, gridspace, gridspace],
        "cubeprop_filepath": self.tempdir
    })

    Chem.MolToMolFile(mol, 'target.mol')
    psi4.cubeprop(wfn)


def tddft(geom, confId=None, method='B3LYP', basis='def2-svp', nstates=5):
    """
    Run TD-DFT with pyscf

    :param geom: an RDKit.Mol or a string
    :param method: method to use
    :param basis: basis to use
    :param nstates: number of excited states to compute
    :param confId: the ID of the conformer to optimize, if needed
    """
    if not isinstance(geom, str):
        assert confId
        geom = make_geometry(geom, confId)

    mol = pyscf.M(
        atom = geom,
        basis = basis,
        symmetry = True,
    )

    mf = mol.RKS()
    mf.xc = method
    mf.run()

    mytd = mf.TDDFT()
    mytd.nstates = nstates
    mytd.run()
    mytd.analyze()


def largest_chromophore(mol):
    edges = [(bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()) for bond in mol.GetBonds() if bond.GetIsConjugated()]

    G = nx.Graph()
    G.add_edges_from(edges)
    connectivity = list(nx.connected_components(G))

    if not connectivity:
        return np.nan

    largest = connectivity[np.argmax(map(len, connectivity))]


def pick_subset(mols, num=5, radius=3, seed=-1):
    """
    Pick a disparate subset of molecules using Morgan Fingerprints.
    https://towardsdatascience.com/a-practical-introduction-to-the-use-of-molecular-fingerprints-in-drug-discovery-7f15021be2b1

    :param mols: an iterable of molecules
    :param num: number of molecules to pick
    :param radius:
    :return: list of integer locations of the subset of molecules
    """
    fps = [GetMorganFingerprint(mol, radius) for mol in mols]

    def distij(i, j, fps=fps):
        return 1 - DataStructs.DiceSimilarity(fps[i], fps[j])

    return list(MaxMinPicker().LazyPick(distij, len(fps), num, seed=seed))
