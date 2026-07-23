from typing import List

from src.engine.linear_solver import LinearSolver
from src.consts.mapping import EQUIPMENT_DICT, MUSCLE_GROUPS
from src.models.data_models import Equipment, Muscle, MuscleGroup, ScenarioParameters, TrainingSolution


class ScenarioHandler:
    def __init__(
        self,
        training_target: int,
        group_list: List[MuscleGroup],
        valid_equipments: List[Equipment] = list(EQUIPMENT_DICT.values())
    ):
        self.training_target = training_target
        self.group_list = group_list
        self.valid_equipments = valid_equipments

        self.scenario_params = ScenarioParameters(
            training_target=training_target,
            valid_equipments=valid_equipments,
            targeted_muscles=self._build_muscles_list(self.group_list)
        )

    def _build_muscles_list(self, group_list: List[MuscleGroup]) -> List[Muscle]:
        """
        Takes a list of muscle groups and returns a list of muscle groups
        :param group_list: list of muscle groups
        :return:
        """
        muscles_list = []

        for group in group_list:
            muscles_list.extend(group.components)

        return muscles_list


    def get_training_plans(self) -> List[TrainingSolution]:
        solver = LinearSolver(scenario_params=self.scenario_params)

        solution = solver.solve()


if __name__ == '__main__':
    ScenarioHandler(
        training_target=1,
        group_list=[
            MUSCLE_GROUPS['biceps'],
            MUSCLE_GROUPS['forearms'],
            MUSCLE_GROUPS['triceps'],
            MUSCLE_GROUPS['upper_abs'],
        ],
        # valid_equipments=[
        #     EQUIPMENT_DICT['Barbell'],
        #     EQUIPMENT_DICT['Dumbbell'],
        #     EQUIPMENT_DICT['Body Weight'],
        # ]
    ).get_training_plans()
