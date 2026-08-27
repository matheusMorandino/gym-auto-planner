from dataclasses import dataclass, field


from src.consts.mapping import EQUIPMENT_DICT, EXERCISE_DICT, MUSCLE_GROUPS


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class _TrainingTarget(metaclass=SingletonMeta):
    """
    Singleton class to hold the state of the training.
    """
    value: int = 3
    title: str = 'Training target'
    description: str = 'Desired average strain level for the selected workout.'
    min: int = 1
    max: int = 5


class _OvertrainingDelta(metaclass=SingletonMeta):
    """
    Singleton class to hold the state of the overtraining delta.
    """
    value: int = 1
    title: str = 'Overtraining delta'
    description: str = 'Allowed margin above target before penalty increases.'
    min: int = 0
    max: int = 5


class _SimilarityThreshold(metaclass=SingletonMeta):
    """
    Singleton class to hold the state of the similarity threshold.
    """
    value: float = 0.5
    title: str = 'Similarity threshold'
    description: str = 'Threshold for considering exercises as too similar.'
    min: float = 0.0
    max: float = 1.0


class _ValidEquipments(metaclass=SingletonMeta):
    """
    Singleton class to hold the state of the valid equipments.
    """
    value: list = None
    title: str = 'Valid equipments'
    description: str = 'Choose the equipments you consider valid. If left empty all equipments will be included.'
    options: list = list(EQUIPMENT_DICT.keys())


class _ExcludedExercises(metaclass=SingletonMeta):
    """
    Singleton class to hold the state of the excluded exercises.
    """
    value: list = None
    title: str = 'Excluded exercises'
    description: str = 'Choose the exercises you want to exclude from your workout.'
    options: list = list(EXERCISE_DICT.keys())


class _TargetMuscleGroups(metaclass=SingletonMeta):
    """
    Singleton class to hold the state of the target muscle groups.
    """
    value: list = None
    title: str = 'Target muscle groups'
    description: str = 'Choose the muscle groups you want to target in your workout.'
    options: list = list(MUSCLE_GROUPS.keys())


class _ForcedExercises(metaclass=SingletonMeta):
    """
    Singleton class to hold the state of the forced exercises.
    """
    value: list = None
    title: str = 'Forced exercises'
    description: str = 'Choose the exercises you want to force into your workout.'
    options: list = list(EXERCISE_DICT.keys())


@dataclass
class InterfaceState(metaclass=SingletonMeta):
    """
    Singleton class to hold the state of the interface.
    """
    current_page: str = 'home'
    training_target: _TrainingTarget = field(default_factory=_TrainingTarget)
    overtraining_delta: _OvertrainingDelta = field(default_factory=_OvertrainingDelta)
    similarity_threshold: _SimilarityThreshold = field(default_factory=_SimilarityThreshold)
    valid_equipments: _ValidEquipments = field(default_factory=_ValidEquipments)
    excluded_exercises: _ExcludedExercises = field(default_factory=_ExcludedExercises)
    target_muscle_groups: _TargetMuscleGroups = field(default_factory=_TargetMuscleGroups)
    forced_exercises: _ForcedExercises = field(default_factory=_ForcedExercises)
