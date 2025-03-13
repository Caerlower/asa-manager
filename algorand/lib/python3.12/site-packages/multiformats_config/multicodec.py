r"""
    Utilities to load and build the multicodec table.
"""

from __future__ import annotations # See https://peps.python.org/pep-0563/

import importlib.resources as importlib_resources
import json
import os
import sys
from typing import Any, Dict, Iterable, Set, TextIO, Tuple, TYPE_CHECKING

from . import config

if TYPE_CHECKING:
    from multiformats.multicodec import Multicodec

def build_multicodec_tables(codecs: Iterable[Multicodec], *,
                            allow_private_use: bool = False) -> Tuple[Dict[int, Multicodec], Dict[str, Multicodec]]:
    """
        Creates code->multicodec and name->multicodec mappings from a finite iterable of multicodecs,
        returning the mappings.

        Example usage:

        >>> code_table, name_table = build_multicodec_tables(codecs)

        :param codecs: multicodecs to be registered
        :type codecs: iterable of :class:`Multicodec`
        :param allow_private_use: whether to allow multicodec entries with private use codes in ``range(0x300000, 0x400000)`` (default :obj:`False`)
        :type allow_private_use: :obj:`bool`, *optional*

        :raises ValueError: if ``allow_private_use`` and a multicodec with private use code is encountered
        :raises ValueError: if the same multicodec code is encountered multiple times, unless exactly one of the multicodecs
        has permanent status (in which case that codec is the one inserted in the table)
        :raises ValueError: if the same name is encountered multiple times

    """
    # pylint: disable = import-outside-toplevel
    from multiformats.multicodec.err import MulticodecValueError
    from multiformats.multicodec import Multicodec
    # validate(codecs, Iterable[Multicodec]) # TODO: not yet properly supported by typing-validation
    # validate(allow_private_use, bool)
    code_table: Dict[int, Multicodec] = {}
    name_table: Dict[str, Multicodec] = {}
    overwritten_draft_codes: Set[int] = set()
    for m in codecs:
        if not allow_private_use and m.is_private_use:
            raise MulticodecValueError(f"Private use multicodec not allowed: {m}")
        if m.code in code_table:
            if code_table[m.code].status == "permanent":
                if m.status == "draft":
                    # this draft code has been superseded by a permanent one, skip it
                    continue
                raise MulticodecValueError(f"Multicodec code {m.hexcode} appears multiple times in table.")
            if m.status != "permanent":
                # overwriting draft code with another draft code: dodgy, need to check at the end
                overwritten_draft_codes.add(m.code)
        code_table[m.code] = m
        if m.name in name_table:
            raise MulticodecValueError(f"Multicodec name {m.name} appears multiple times in table.")
        name_table[m.name] = m
    for code in overwritten_draft_codes:
        m = code_table[code]
        if m.status != "permanent":
            raise MulticodecValueError(f"Code {m.code} appears multiple times in table, "
                              "but none of the associated multicodecs is permanent.")
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

def load_multicodec_table() -> Tuple[Dict[int, Multicodec], Dict[str, Multicodec]]:
    """
        Returns code->encoding and name->encoding mappings created (via :func:`build_multicodec_tables`) from the local copy of `multicodec-table.json`.
        If a subset of multicodecs has been enabled, only those multicodecs are loaded.

        Example usage:

        >>> code_table, name_table = load_multicodec_table()

    """
    # pylint: disable = import-outside-toplevel
    from multiformats.multicodec import Multicodec
    # with importlib_resources.open_text("multiformats_config", "multicodec-table.json", encoding="utf8") as _table_f:
    with open_text("multiformats_config", "multicodec-table.json", encoding="utf8") as _table_f:
        table_json = json.load(_table_f)
        multicodecs = (Multicodec(**row) for row in table_json)
        if config._enabled_multicodecs is not None:
            multicodecs = (m for m in multicodecs if m.name in config._enabled_multicodecs or m.code in config._enabled_multicodecs)
        code_table, name_table = build_multicodec_tables(multicodecs)
    config.lock()
    return code_table, name_table
