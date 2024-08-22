from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Optional


class ExperimentFlagType(str, Enum):
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    STRING = "STRING"


@dataclass
class AiModel:
    name: str
    version: int

    @classmethod
    def from_string_format(cls, data):
        split_data = data.split(' | ')
        return AiModel(split_data[0], int(split_data[1]))

    def to_string_format(self):
        return f'{self.name} | {self.version}'

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class Flag:
    name: str
    type: ExperimentFlagType
    base_value: Any
    ai_model: Optional[AiModel]


@dataclass
class Experiment:
    name: str
    flag_name: str
    flag_value: Any
    layer: str
    ai_model: Optional[AiModel]
    '''
    share is between 0 and 1
    '''
    share: float

    def __post_init__(self):
        if not 0 <= self.share <= 1:
            raise ValueError("Share value must be a float between 0 and 1, inclusive.")
