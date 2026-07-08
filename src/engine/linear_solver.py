import pandas as pd
from typing import List, Dict, Literal, Tuple
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpAffineExpression, LpStatus

from models.data_models import ScenarioParameters
from src.consts.mapping import EXERCISE_DICT


class LinearSolver:
    def __init__(self, scenario_params: ScenarioParameters):
        self.scenario_params = scenario_params

        self.strain_matrix = self._build_strain_matrix()

        self.problem = None

    def _build_strain_matrix(self) -> Dict[Tuple[str, str], int]:
        """
        Builds matrix-like dictionary representing the strain a given exercise will apply to a given muscle
        :return:
        """
        valid_equip_names = [equip.name for equip in self.scenario_params.valid_equipments]
        valid_exercises = [
            exercise for _, exercise in EXERCISE_DICT.items() if exercise.equipment in valid_equip_names]

        strain_matrix = {}
        for muscle in self.scenario_params.muscles_list:
            for exercise in valid_exercises:
                if muscle.name in exercise.primary_muscles:
                    strain = 2
                elif muscle.name in exercise.secondary_muscles:
                    strain = 1
                else:
                    strain = 0

                strain_matrix[(muscle.name, exercise.name)] = strain

        return strain_matrix

    def _create_variables(self):
        """
        Creates variables needed for linear solver
        :return:
        """
        pass

    def solve(self):
        # Defining problem
        self.problem = LpProblem("Training_Optimization", LpMinimize)

        self._create_variables()
