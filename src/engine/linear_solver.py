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

    def _build_strain_matrix(self) -> pd.DataFrame:
        """
        Builds dataframe representing the strain a given exercise will apply to a given muscle
        :return:
        """
        strain_matrix = pd.DataFrame(index=[muscle.name for muscle in MUSCLES_DICT.values()],
                                     columns=[exercise.name for exercise in self.valid_exercises])

        for muscle in strain_matrix.index:
            for exercise in strain_matrix.columns:
                if muscle in EXERCISE_DICT[exercise].primary_muscles:
                    strain = self.scenario_params.primary_score
                elif muscle in EXERCISE_DICT[exercise].secondary_muscles:
                    strain = self.scenario_params.secondary_score
                elif muscle in EXERCISE_DICT[exercise].synergistic_muscles:
                    strain = self.scenario_params.synergistic_score
                elif muscle in EXERCISE_DICT[exercise].stabilizing_muscles:
                    strain = self.scenario_params.stabilizing_score
                elif muscle in EXERCISE_DICT[exercise].antagonist_muscles:
                    strain = self.scenario_params.antagonist_score
                elif muscle in EXERCISE_DICT[exercise].dynamic_muscles:
                    strain = self.scenario_params.dynamic_score
                else:
                    strain = 0

                strain_matrix.at[muscle, exercise] = strain

        return strain_matrix

    def _create_variables(self):
        """
        Creates variables needed for the linear solver
        :return:
        """
        # Create variables for the usage of a given valid exercise from the scenario parameters
        self.var_exercise: Dict[str, LpVariable] = {
            exercise.name: LpVariable(f'{exercise.name}_usage', lowBound=0, upBound=1, cat='Binary')
            for exercise
            in self.valid_exercises
        }

    def _create_restictions(self):
        """
        Creates all the required restrictions for the linear solver. The logic follows the following targets:

        1. Each targeted muscle in the scenario must have it's total strain >= training_target

        :return:
        """
        for muscle in self.scenario_params.targeted_muscles:
            total_strain = lpSum(
                self.strain_matrix.at[muscle.name, exercise] * self.var_exercise[exercise]
                for exercise in self.strain_matrix.columns
            )

            self.problem += (total_strain >= self.scenario_params.training_target,
                             f'{muscle.name}_strain_restriction')

    def _create_objective_function(self):
        """
        Creates the objective function for the linear solver. The logic follows the following targets:

        * obj: Minimal objective function
        * formulation:
            total_strain_weight * sum(strain_matrix[muscle][exercise] * var_exercise[exercise])
        """
        total_strain_comp = (
            self.scenario_params.total_strain_weight * lpSum(
                self.strain_matrix.at[muscle, exercise] * self.var_exercise[exercise]
                for muscle in self.strain_matrix.index
                for exercise in self.strain_matrix.columns
            )
        )

        total_obj_function = total_strain_comp

        self.problem += total_obj_function

    def solve(self):
        # Defining problem
        self.problem = LpProblem("Training_Optimization", LpMinimize)

        self._create_variables()
        self._create_restictions()
        self._create_objective_function()

        # Solve the problem
        self.problem.solve()

        # print solution
        for exercise in self.valid_exercises:
            usage = self.var_exercise[exercise.name].varValue
            if isinstance(usage, float) and usage > 0:
                print(f'{exercise.name} -> {usage}')
