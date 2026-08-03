from typing import List

from src.engine.linear_solver import LinearSolver
from src.consts.mapping import EQUIPMENT_DICT, MUSCLE_GROUPS
from src.models.data_models import Equipment, Muscle, MuscleGroup, ModelParameters, TrainingSolution


class ScenarioHandler:
    def __init__(
        self,
        training_target: int,
        overtraining_delta: int,
        group_list: List[MuscleGroup],
        valid_equipments: List[Equipment] = None
    ):
        if valid_equipments is None:
            valid_equipments = list(EQUIPMENT_DICT.values())

        self.training_target = training_target
        self.overtraining_delta = overtraining_delta
        self.group_list = group_list
        self.valid_equipments = valid_equipments

        self.scenario_params = ModelParameters(
            training_target=training_target,
            overtraining_delta=overtraining_delta,
            valid_equipments=valid_equipments,
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


    def get_training_plans(self) -> List[TrainingSolution]:
        solver = LinearSolver(scenario_params=self.scenario_params)

        solution = solver.solve()

        # print solution
        for exercise in solution.exercise_list:
            print(f'>> {exercise.name}')


if __name__ == '__main__':
    ScenarioHandler(
        training_target=2,
        overtraining_delta=2,
        group_list=[
            # MUSCLE_GROUPS['biceps'],
            # MUSCLE_GROUPS['forearms'],
            # MUSCLE_GROUPS['triceps'],
            # MUSCLE_GROUPS['front_delts'],
            # MUSCLE_GROUPS['side_delts'],
            # MUSCLE_GROUPS['rear_delts'],
            # MUSCLE_GROUPS['upper_pecs'],
            # MUSCLE_GROUPS['lower_pecs'],
            # MUSCLE_GROUPS['middle_pecs'],
            MUSCLE_GROUPS['upper_abs'],
            MUSCLE_GROUPS['lower_abs'],
        ],
        valid_equipments=[
            EQUIPMENT_DICT['Barbell'],
            EQUIPMENT_DICT['Dumbbell'],
            EQUIPMENT_DICT['Body Weight'],
        ]
    ).get_training_plans()
