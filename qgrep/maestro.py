import re
from itertools import filterfalse, takewhile
from typing import Iterable

import pandas as pd
from .helper import MyIter


def remove_comments(it):
    """
    Remove any line that is blank or a comment
    """

    def is_comment(line):
        return line and line[0] == "#"

    yield from filterfalse(is_comment, it)


def read_key_values(
    it: Iterable[str],
    stop: str = ":::",
    is_matched: bool = True,
) -> dict | tuple[list[str], list[list[str]]]:
    """
    Read keys and values separated by `stop`
    """
    keys = list(takewhile(lambda x: x != stop, remove_comments(it)))
    values = remove_comments(it)

    if is_matched:
        return dict(zip(keys, values))  # zip makes values stop at the right point

    # values are thus rectangular
    vals = list(
        map(
            lambda x: x.split(),
            takewhile(
                lambda x: x != stop,
                values,
            ),
        )
    )

    return keys, vals


def read_molecule_chunk_header(line) -> tuple[str, int] | None:
    """
    Interpret the section header.
    >>> read_molecule_chunk_header("m_atom[20]")
    ('atom', 20)
    """
    if res := re.search(r"m_(.+?)\[(\d+)\]", line):
        name, n_values = res.groups()
        return name, int(n_values)
    return None


def read_mae(infile: str) -> list[dict[str, dict | tuple[list[str], list[list[str]]]]]:
    """
    Read an mae file
    """
    data = []
    with open(infile) as fin:
        f = MyIter(fin)
        for line in f:
            if line[:6] == "f_m_ct":
                molecule_data = {"mol_data": read_key_values(f, is_matched=True)}

                # atom, bond, depend, etc.
                for line in f:
                    if not line or line == "}":
                        break

                    if res := read_molecule_chunk_header(line):
                        name, n_values = res
                    else:
                        raise ValueError(f"Unable to read line={f._position}\n{line}")

                    keys, values = read_key_values(f, is_matched=False)

                    if name in ["atom", "bond", "depend"]:
                        keys.insert(0, "idx")

                    molecule_data[name] = keys, values

                    if name == "atom":
                        atoms_to_df(keys, values)

                    assert n_values == len(values)
                    assert next(f) == "}"

                data.append(molecule_data)
    return data


def atoms_to_df(titles: list[str], atoms: list[list[str]]) -> pd.DataFrame:
    """
    Convert atom data to a dataframe
    """
    df = pd.DataFrame(atoms, columns=titles).convert_dtypes(infer_objects=True)

    for col in [
        "idx",
        "i_m_atomic_number",
        "r_m_x_coord",
        "r_m_y_coord",
        "r_m_z_coord",
        "i_m_mmod_type",
        "i_m_representation",
        "i_m_color",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])

    return df


def write_geoms(molecule_data, outfile: str = "geom.xyz") -> None:
    with open(outfile, "w") as f:
        for mol in molecule_data:
            df = atoms_to_df(*mol["atom"])
            geom = df[["i_m_atomic_number", "r_m_x_coord", "r_m_y_coord", "r_m_z_coord"]]

            f.write(f"{len(df)}\n\n")
            f.writelines(
                f"{an:.0f} {x:9.5f} {y:9.5f} {z:9.5f}\n"
                for _, (an, x, y, z) in geom.iterrows()  # keep open
            )
