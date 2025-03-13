"""
    Configuration for the `multiformats <https://github.com/hashberg-io/multiformats>`_ package.
"""

import re
from typing import Iterable, Optional, Set, Union

_minimal_multicodecs = frozenset([
    0x00, # identity
    0x01, # cidv1
    0x02, # cidv2
    0x12, # sha2-256
    0x14, # sha3-512
    0x16, # sha3-256
    0x70, # dag-pb
    0x71, # dag-cbor
    0x72, # libp2p-key
])

_minimal_multibases = frozenset([
    "identity",
    "base16",
    "base32",
    "base58btc",
])

_enabled_multicodecs: Optional[Set[Union[int, str]]] = None
_enabled_multibases: Optional[Set[str]] = None
_locked: bool = False

def is_locked() -> bool:
    r""" Whether the configuration is locked. """
    return _locked

def lock() -> None:
    r"""
        Locks configuration, disabling further modification.
        Automatically called the first time configuration/table data is accessed.
    """
    # pylint: disable = global-statement
    global _locked
    _locked = True

class LockedConfigError(Exception):
    r""" Error raised by :func:`enable` if the configuration is locked (see :func:`is_locked` and :func:`lock`). """
    ...

def enable(*,
           codecs: Optional[Iterable[Union[int, str]]] = None,
           bases: Optional[Iterable[str]] = None,
          ) -> None:
    r"""
        Mantually enable a sub-set of multicodecs and/or multibases:

        - a multicodec can be specified by name (passing a :obj:`str`) or by code (passing an :obj:`int`).
        - a multibase can be specified by name (passing a :obj:`str` of length > 1) or by code (passing a :obj:`str` of length 1).

        Passing :obj:`None` (default) to the `multicodecs` (resp. `multibases`) keyword argument means that all multicodecs (resp. multibases) will be loaded.
    """
    # pylint: disable = global-statement
    if is_locked():
        raise LockedConfigError("Cannot enable multicodecs/multibases: multiformats configuration is locked.")
    global _enabled_multicodecs
    global _enabled_multibases
    _multicodecs = {_validate_multicodec_data(data) for data in codecs} if codecs is not None else None
    _multibases = {_validate_multibase_data(data) for data in bases} if bases is not None else None
    if _multicodecs is not None:
        _multicodecs.update(_minimal_multicodecs)
    if _multibases is not None:
        _multibases.update(_minimal_multibases)
    _enabled_multicodecs = _multicodecs
    _enabled_multibases = _multibases

def _validate_multicodec_data(data: Union[int, str]) -> Union[int, str]:
    if isinstance(data, str):
        _validate_multicodec_name(data)
    elif isinstance(data, int):
        _validate_multicodec_code(data)
    else:
        raise TypeError(f"Expected multicodec name (str) or code (int), found {data} of type {type(data)}.")
    return data

def _validate_multicodec_name(name: str) -> None:
    if not re.match(r"^[a-z][a-z0-9_-]+$", name):
        raise ValueError(f"Invalid multicodec name {repr(name)}")

def _validate_multicodec_code(code: int) -> None:
    if code < 0:
        raise ValueError(f"Invalid multicodec code {repr(code)}.")

def _validate_multibase_data(data: str) -> str:
    if not isinstance(data, str):
        raise TypeError(f"Expected multibase name (str of len > 1) or code (str of len 1), found {data} of type {type(data)}.")
    if len(data) == 1:
        _validate_multibase_code(data)
    elif isinstance(data, int):
        _validate_multibase_name(data)
    return data

def _validate_multibase_name(name: str) -> None:
    if not re.match(r"^[a-z][a-z0-9_-]+$", name): # ensures len(name) > 1
        raise ValueError(f"Invalid multibase encoding name {repr(name)}")

def _validate_multibase_code(code: str) -> None:
    if len(code) != 1:
        raise ValueError("Multibase codes must be single-character strings or the hex digits '0x...' of a non-empty bytestring.")
