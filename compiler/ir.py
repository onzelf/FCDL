from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class NeuralLayer:
    kind: str
    params: Dict[str, str]

@dataclass
class Module:
    name: str
    mod_type: str
    attrs: Dict[str, str]
    layers: List[NeuralLayer] = field(default_factory=list)

@dataclass
class Orchestration:
    attrs: Dict[str, str]

@dataclass
class SystemIR:
    name: str
    version: str
    modules: Dict[str, Module] = field(default_factory=dict)
    orchestration: Optional[Orchestration] = None

