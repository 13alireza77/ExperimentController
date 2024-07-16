from dataclasses import dataclass
from enum import Enum
from typing import Any


class ExperimentFlagType(str, Enum):
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"


@dataclass
class Flag:
    name: str
    type: ExperimentFlagType
    base_value: Any


@dataclass
class Experiment:
    name: str
    flag_name: str
    flag_value: Any
    layer: str
    '''
    share is between 0 and 1
    '''
    share: float

    def __post_init__(self):
        if not 0 <= self.share <= 1:
            raise ValueError("Share value must be a float between 0 and 1, inclusive.")
