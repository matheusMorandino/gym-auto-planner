from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class Muscle:
    name: str = field(default='')


@dataclass
class MuscleGroup():
    name: str = field(default='')
    components: List[Muscle] = field(default_factory=list)


@dataclass
class Equipment:
    name: str = field(default='')


@dataclass
class Exercise:
    # Exercise attributes
    name: str = field(default='')
    equipment: Equipment = field(default_factory=Equipment)

    # Muscle groupings
    primary_muscles: List[Muscle] = field(default_factory=list)
    secondary_muscles: List[Muscle] = field(default_factory=list)
    synergistic_muscles: List[Muscle] = field(default_factory=list)
    stabilizing_muscles: List[Muscle] = field(default_factory=list)
    antagonist_muscles: List[Muscle] = field(default_factory=list)
    dynamic_muscles: List[Muscle] = field(default_factory=list)

    # Modeling representations
    muscle_vector: Dict[Muscle, int] = field(default_factory=dict)


@dataclass
class ScenarioParameters:
    overtraining_delta: int = field(default=0)
    muscles_list: List[Muscle] = field(default_factory=list)
    valid_equipments: List[Equipment] = field(default_factory=list)


@dataclass
class TrainingSolution:
    pass
