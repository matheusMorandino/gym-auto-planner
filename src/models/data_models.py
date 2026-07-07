from typing import List
from dataclasses import dataclass, field


@dataclass
class Muscle:
    name: str = field(default='')
    target_strain: int = field(default=0)


@dataclass
class Equipment:
    name: str = field(default='')


@dataclass
class Exercise:
    name: str = field(default='')
    equipment: Equipment = field(default_factory=Equipment)
    primary_muscles: List[Muscle] = field(default_factory=list)
    secondary_muscles: List[Muscle] = field(default_factory=list)


@dataclass
class ScenarioParameters:
    overtraining_delta: int = field(default=0)
    training_list: List[Muscle] = field(default_factory=list)
    valid_trainings: List[Equipment] = field(default_factory=list)

