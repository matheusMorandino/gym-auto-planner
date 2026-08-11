from typing import List

from src.engine.linear_solver import LinearSolver
from src.consts.mapping import EQUIPMENT_DICT, MUSCLE_GROUPS, EXERCISE_DICT
from src.models.data_models import Muscle, MuscleGroup, ModelParameters, TrainingSolution


class ScenarioHandler:
    def __init__(
        self,
        training_target: int,
        overtraining_delta: int,
        similarity_threshold: float,
        group_list: List[str],
        valid_equipments: List[str] = None,
        exercise_blacklist: List[str] = None,
        forced_exercises: List[str] = None,
    ):
        if valid_equipments is None or valid_equipments == []:
            valid_equipments = list(EQUIPMENT_DICT.keys())
        if exercise_blacklist is None or exercise_blacklist == []:
            exercise_blacklist = []
        if forced_exercises is None or forced_exercises == []:
            forced_exercises = []

        self.training_target = training_target
        self.overtraining_delta = overtraining_delta
        self.group_list = [MUSCLE_GROUPS[group] for group in group_list]
        self.valid_equipments = [EQUIPMENT_DICT[equip] for equip in valid_equipments]
        self.exercise_blacklist = [EXERCISE_DICT[exercise] for exercise in exercise_blacklist]
        self.forced_exercises = [EXERCISE_DICT[exercise] for exercise in forced_exercises]

        self.scenario_params = ModelParameters(
            training_target=training_target,
            overtraining_delta=overtraining_delta,
            similarity_threshold=similarity_threshold,
            exercise_blacklist=self.exercise_blacklist,
            forced_exercises=self.forced_exercises,
            valid_equipments=self.valid_equipments,
            target_groups=self.group_list,
            targeted_muscles=self._build_muscles_list(self.group_list)
        )

    def _build_muscles_list(self, group_list: List[MuscleGroup]) -> List[Muscle]:
        """
        Takes a list of muscle groups and returns a list of muscle groups
        :param group_list: list of muscle groups
        :return: list of muscles
        """
        muscles_list = []

        for group in group_list:
            muscles_list.extend(group.components)

        return muscles_list

    def get_training_plans(self, n_target: int = 1) -> List[TrainingSolution]:
        """
        Returns a list of training solutions
        :param n_target: number of training solutions to return
        :return: list of training solutions
        """
        solver = LinearSolver(scenario_params=self.scenario_params)

        return solver.solve_multiple(n_solutions=n_target)


if __name__ == '__main__':
    ScenarioHandler(
        training_target=2,
        overtraining_delta=2,
        similarity_threshold=0.4,
        group_list=[
            # 'biceps',
            # 'forearms',
            # 'triceps',
            # 'front_delts',
            # 'side_delts',
            # 'rear_delts',
            # 'upper_pecs',
            # 'lower_pecs',
            # 'middle_pecs',

            'upper_abs',
            'lower_abs',

            'quads',
            'hamstrings',
            'glutes',
            'calves',
            'hip_abductor',
            'hip_adductor',
        ],
        valid_equipments=[
            'Barbell',
            'Dumbbell',
            'Body Weight',
        ]
    ).get_training_plans()
