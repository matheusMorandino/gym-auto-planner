from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class Muscle:
    name: str = field(default='')


@dataclass
class MuscleGroup:
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

    # strain groups
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
    training_target: int = field(default=0)
    muscles_list: List[Muscle] = field(default_factory=list)
    valid_equipments: List[Equipment] = field(default_factory=list)

    # strain groups scores
    primary_score: float = field(default=1)
    secondary_score: float = field(default=0.8)
    synergistic_score: float = field(default=0.5)
    stabilizing_score: float = field(default=0.2)
    antagonist_score: float = field(default=0.1)
    dynamic_score: float = field(default=0.2)

@dataclass
class TrainingSolution:
    pass
