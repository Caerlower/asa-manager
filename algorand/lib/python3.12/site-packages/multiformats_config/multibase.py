r"""
    Utilities to load and build the multibase table.
"""

from __future__ import annotations # See https://peps.python.org/pep-0563/

import importlib.resources as importlib_resources
import json
import os
import sys
from typing import Any, Dict, Iterable, TextIO, Tuple, TYPE_CHECKING

from . import config

if TYPE_CHECKING:
    from multiformats.multibase import Multibase

def build_multibase_tables(bases: Iterable[Multibase]) -> Tuple[Dict[str, Multibase], Dict[str, Multibase]]:
    """
        Creates code->encoding and name->encoding mappings from a finite iterable of encodings, returning the mappings.

        Example usage:

        >>> code_table, name_table = build_multicodec_tables(bases)

        :raises ValueError: if the same encoding code or name is encountered multiple times
    """
    # pylint: disable = import-outside-toplevel
    from multiformats.multibase import Multibase
    from multiformats.multibase.err import MultibaseValueError
    code_table: Dict[str, Multibase] = {}
    name_table: Dict[str, Multibase] = {}
    for e in bases:
        if e.code in code_table:
            raise MultibaseValueError(f"Multibase code {e.code} appears multiple times in table.")
        code_table[e.code] = e
        if e.name in name_table:
            raise MultibaseValueError(f"Multibase name {e.name} appears multiple times in table.")
        name_table[e.name] = e
    return code_table, name_table

if sys.version_info[1] >= 9:
    def normalize_path(path: Any) -> str:
        """
            Normalize a path by ensuring it is a string.

            If the resulting string contains path separators, an exception is raised.

            Code snippet from
            `importlib_resources <https://github.com/python/importlib_resources/>`_.

            See https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy
        """
        str_path = str(path)
        parent, file_name = os.path.split(str_path)
        if parent:
            raise ValueError(f'{path!r} must be only a file name')
        return file_name

    def open_text(
        package: importlib_resources.Package,
        resource: importlib_resources.Resource,
        encoding: str = 'utf-8',
        errors: str = 'strict',
    ) -> TextIO:
        """
            Return a file-like object opened for text reading of the resource.

            Code snippet from
            `importlib_resources <https://github.com/python/importlib_resources/>`_.

            See https://importlib-resources.readthedocs.io/en/latest/using.html#migrating-from-legacy
        """
        # pylint: disable = no-member
        return (
            importlib_resources.files(package) / normalize_path(resource)
        ).open("r", encoding=encoding, errors=errors)
else:
    open_text = importlib_resources.open_text


def load_multibase_table() -> Tuple[Dict[str, Multibase], Dict[str, Multibase]]:
    """
        Returns code->encoding and name->encoding mappings created (via :func:`build_multibase_tables`) from the local copy of `multibase-table.json`.
        If a subset of multibases has been enabled, only those multibases are loaded.

        Example usage:

        >>> code_table, name_table = load_multibase_table()

    """
    # pylint: disable = import-outside-toplevel
    from multiformats.multibase import Multibase
    # with importlib_resources.open_text("multiformats_config", "multibase-table.json", encoding="utf8") as _table_f:
    with open_text("multiformats_config", "multibase-table.json", encoding="utf8") as _table_f:
        table_json = json.load(_table_f)
        multibases = (Multibase(**row) for row in table_json)
        if config._enabled_multibases is not None:
            multibases = (m for m in multibases if m.name in config._enabled_multibases or m.code in config._enabled_multibases)
        code_table, name_table = build_multibase_tables(multibases)
    config.lock()
    return code_table, name_table
