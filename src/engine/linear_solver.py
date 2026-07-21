import pandas as pd
from typing import List, Dict, Literal, Tuple
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpAffineExpression, LpStatus

from models.data_models import ScenarioParameters
from src.consts.mapping import EXERCISE_DICT, MUSCLES_DICT


class LinearSolver:
    def __init__(self, scenario_params: ScenarioParameters):
        self.scenario_params = scenario_params

        self.valid_equip_names = [equip.name for equip in self.scenario_params.valid_equipments]
        self.valid_exercises = [
            exercise for _, exercise in EXERCISE_DICT.items() if exercise.equipment in self.valid_equip_names]
        self.strain_matrix = self._build_strain_matrix()

        self.problem = None

    def _build_strain_matrix(self) -> Dict[Tuple[str, str], int]:
        """
        Builds matrix-like dictionary representing the strain a given exercise will apply to a given muscle
        :return:
        """
        strain_matrix = pd.DataFrame(index=[muscle.name for muscle in self.scenario_params.muscles_list],
                                     columns=[exercise.name for exercise in self.valid_exercises])

        for muscle in MUSCLES_DICT.values():
            for exercise in self.valid_exercises:
                if muscle.name in exercise.primary_muscles:
                    strain = self.scenario_params.primary_score
                elif muscle.name in exercise.secondary_muscles:
                    strain = self.scenario_params.secondary_score
                elif muscle.name in exercise.synergistic_muscles:
                    strain = self.scenario_params.synergistic_score
                elif muscle.name in exercise.stabilizing_muscles:
                    strain = self.scenario_params.stabilizing_score
                elif muscle.name in exercise.antagonist_muscles:
                    strain = self.scenario_params.antagonist_score
                elif muscle.name in exercise.dynamic_muscles:
                    strain = self.scenario_params.dynamic_score
                else:
                    strain = 0

                strain_matrix.at[muscle.name, exercise.name] = strain

        return strain_matrix

    def _create_variables(self):
        """
        Creates variables needed for the linear solver
        :return:
        """
        # Create variables for the usage of a given valid exercise from the scenario parameters
        self.var_exercise: Dict[str, LpVariable] = {
            exercise.name: LpVariable(f'{exercise.name}_usage', lowBound=0, cat='Integer')
            for exercise
            in self.valid_exercises
        }

    def solve(self):
        # Defining problem
        self.problem = LpProblem("Training_Optimization", LpMinimize)

        self._create_variables()
