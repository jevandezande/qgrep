#!/usr/bin/env python3
from __future__ import annotations

import itertools
from more_itertools import take
from typing import Generator, Iterable
from pprint import pprint

period_2 = ["Li", "Be", "B", "C", "N", "O", "F", "Ne"]
bent_carbon = ["C(C)C", "C(C)(C)C", "C(CC)C", "C(CC)(CC)C"]
b_group = ["B", "Al"]
c_group = ["C", "Si"]
pnictogens = ["N", "P"]
chalcogens = ["O", "S"]
halogens = ["F", "Cl", "Br", "I"]
bonds = ["", "=", "#"]
functional_groups = ["=O", "(=O)O", "C#N", "N=C=O"]


def insert_in_str(group, string: str, index: int, strict: bool = False) -> str:
    """
    Insert a group into a string.

    >>> insert_in_str(123, 'abcd', 2)
    'ab123cd'
    """
    if strict and index > len(string):
        raise ValueError("Trying to insert beyond the end of a string.")
    return string[:index] + str(group) + string[index:]


def alkyl_chains(carbons_max: int, start: int = 1) -> Generator[str, None, None]:
    """
    >>> list(alkyl_chains(5))
    ['C', 'CC', 'CCC', 'CCCC', 'CCCCC']
    """
    yield from ("C" * i for i in range(start, carbons_max + 1))


def alkene_chains(carbons_max: int, start=2):
    """
    Note: only produces an even number of carbon atoms
    >>> list(alkene_chains(10))
    ['C=C', 'C=CC=C', 'C=CC=CC=C', 'C=CC=CC=CC=C', 'C=CC=CC=CC=CC=C']
    """
    yield from ("=".join(["CC"] * i)[1:-1] for i in range(start, carbons_max // 2 + 2))


def rings(
    sizes: Iterable[int] | int, atoms: Iterable[str] | str = "C", strict: bool = False
) -> Generator[str, None, None]:
    """
    Generate rings of various sizes

    >>> list(rings([2], ['C']))
    []
    >>> list(rings(4, 'C'))
    ['C1CCC1']
    >>> list(rings([4, 5], ['C', 'N']))
    ['C1NCN1', 'C1NCNC1']
    """
    sizes = [sizes] if isinstance(sizes, int) else sizes
    atoms = itertools.repeat(atoms) if isinstance(atoms, str) else itertools.cycle(atoms)

    for size in sizes:
        if size < 3:
            if strict:
                raise ValueError(f"Cannot make ring with {size=}")
            continue

        it = iter(take(size, atoms))
        yield f"{next(it)}1" + "".join(atom for atom in it) + "1"


def aromatics(max_order: int) -> Generator[str, None, None]:
    """
    Generate aromatics

    >>> list(aromatics(0))
    []
    >>> list(aromatics(2))
    ['c1ccccc1', 'c1ccccccccc1']
    """
    yield from ("c1" + "cccc" * i + "c1" for i in range(1, (max_order + 1)))


def append_groups(chains: Iterable[str] | str, groups: Iterable[str] | str) -> Generator[str, None, None]:
    """
    >>> list(append_groups('CCC', 'Br'))[0]
    'CCCBr'
    >>> list(append_groups(['CC', 'HO'], ['12', '6789']))
    ['CC12', 'CC6789', 'HO12', 'HO6789']
    """
    if isinstance(chains, str):
        chains = [chains]
    if isinstance(groups, str):
        groups = [groups]
    for vals in itertools.product(chains, groups):
        yield "".join(vals)


def insert_groups(
    chains: Iterable[str] | str,
    groups: Iterable[str] | str,
    locations: Iterable[int] | int,
) -> Generator[str, None, None]:
    """
    Insert groups into chains at locations.
    If location > len(chain), it appends to the end.

    If multiple chains and locations are specified, they are zipped together.

    Warnings:
        Does not deal with clashing numbers in rings.
        Does not remove accidental duplicates.
    """
    if isinstance(chains, str):
        if isinstance(locations, int):
            chains = [chains]
            locations = [locations]
        else:
            # Thus locations is an iterable, so repeating is safe
            chains = itertools.repeat(chains)
    elif isinstance(locations, int):
        # Thus chains is an iterable, so repeating is safe
        locations = itertools.repeat(locations)

    if isinstance(groups, str):
        groups = [groups]

    for group in groups:
        chains, chains_dup = itertools.tee(chains)
        yield from (insert_in_str(f"({group})", chain, location) for chain, location in zip(chains_dup, locations))


if __name__ == "__main__":
    molecules: list[str] = []
    molecules += alkyl_chains(5)
    molecules += alkene_chains(5)
    molecules += append_groups(alkyl_chains(5), period_2[4:-1] + functional_groups)
    molecules += insert_groups(alkyl_chains(5), period_2[4:-1] + ["=O"], 2)
    molecules += rings(range(10), strict=False)
    molecules += append_groups(rings(range(10)), alkyl_chains(7))
    molecules += aromatics(2)
    molecules += append_groups(aromatics(2), alkyl_chains(7))

    pprint(molecules)
