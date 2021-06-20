
from dataclasses import dataclass
from typing import Any, List

@dataclass
class Hash:
    algo: str = None
    value: str = None

@dataclass
class File:
    id: str = None
    name: str = None 
    supplierName: str = None
    hashes: List[Hash] = None
    rawdata: Any = None

@dataclass
class Package:
    id: str = None
    name: str = None
    version: str = None
    supplierName: str = None
    hashes: List[Hash] = None
    rawdata: Any = None

@dataclass
class FinalProduct:
    id: str
    supplierName: str
    name: str
    hash: List[Hash]
    rawdata: Any


@dataclass
class Relationship:
    id: str = None
    fromId: str = None
    toId: str = None
    type: str = None
    rawdata: Any = None
    