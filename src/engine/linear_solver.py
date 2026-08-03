import pandas as pd
import itertools
import numpy as np
from typing import List, Dict, Literal, Tuple

from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, LpStatusOptimal

from models.data_models import ModelParameters, Exercise, TrainingSolution
from src.consts.mapping import EXERCISE_DICT, MUSCLES_DICT


class LinearSolver:
    def __init__(self, scenario_params: ModelParameters):
        self.scenario_params = scenario_params

        self.valid_exercises: List[Exercise] = self._get_valid_exercises()
        self.strain_matrix: pd.DataFrame = self._build_strain_matrix()
        self.exercise_cosine_matrix: pd.DataFrame = self._build_cosine_matrix()

        self.problem = None

    def _get_valid_exercises(self) -> List[Exercise]:
        """
        Returns a list of valid exercises based on the scenario parameters
        :return:
        """
        return [
            exercise
            for _, exercise
            in EXERCISE_DICT.items()
            if exercise.equipment in [equip.name for equip in self.scenario_params.valid_equipments]
        ]

    def _build_cosine_matrix(self) -> pd.DataFrame:
        """
        Create a cosine distance matrix between all present exercises. Used in measuring
        redundancy between two given exercises.
        :return:
        """
        cosine_matrix = pd.DataFrame(
            index=[exercise.name for exercise in self.valid_exercises],
            columns=[exercise.name for exercise in self.valid_exercises],
        )

        for i, j in itertools.permutations(cosine_matrix.index, 2):
            vect_i = np.array(list(EXERCISE_DICT[i].muscle_vector.values()))
            vect_j = np.array(list(EXERCISE_DICT[j].muscle_vector.values()))

            # Calculate cosine similarity between exercises i and j
            dot_prod = np.dot(vect_i, vect_j)
            norm_i = np.linalg.norm(vect_i)
            norm_j = np.linalg.norm(vect_j)
            cosine_similar = dot_prod / (norm_i * norm_j)

            # Adding cosine distance between i and j to the matrix
            cosine_matrix.at[i, j] = 1 - cosine_similar

        return cosine_matrix.fillna(0)

    def _build_strain_matrix(self) -> pd.DataFrame:
        """
        Builds dataframe representing the strain a given exercise will apply to a given muscle
        :return:
        """
        strain_matrix = pd.DataFrame(
            index=[muscle.name for muscle in MUSCLES_DICT.values()],
            columns=[exercise.name for exercise in self.valid_exercises]
        )

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
        Creates all the required restrictions for the linear solver.
        :return:
        """
        # Each muscle group must have a total strain(sum strain of all muscles) above the scenario's target strain
        for group in self.scenario_params.target_groups:
            total_strain = lpSum(
                self.strain_matrix.at[muscle.name, exercise] * self.var_exercise[exercise]
                for muscle in group.components
                for exercise in self.strain_matrix.columns
            )

            self.problem += (
                total_strain >= self.scenario_params.training_target,
                f'{group.name}_min_strain_restriction'
            )

        # Each muscle group must have a total strain(sum strain of all muscles) below the sum of the
        # scenario's overtraining delta plus target strain
        for group in self.scenario_params.target_groups:
            total_strain = lpSum(
                self.strain_matrix.at[muscle.name, exercise] * self.var_exercise[exercise]
                for muscle in group.components
                for exercise in self.strain_matrix.columns
            )

            self.problem += (
                total_strain <= self.scenario_params.training_target + self.scenario_params.overtraining_delta,
                f'{group.name}_max_strain_restriction'
            )

    def _create_objective_function(self):
        """
        Creates the objective function for the linear solver.
        """
        # minimize the total number of exercises done
        total_obj_function = lpSum(
            self.var_exercise[exercise.name]
            for exercise in self.valid_exercises
        )

        self.problem += total_obj_function

    def solve(self) -> TrainingSolution:
        # Defining problem
        self.problem = LpProblem("Training_Optimization", LpMinimize)

        self._create_variables()
        self._create_restictions()
        self._create_objective_function()

        # Solve the problem
        self.problem.solve()

        # Create solution object
        solution = TrainingSolution(
            solution_status=LpStatus[self.problem.status],
            exercise_list=[]
        )

        if self.problem.status == LpStatusOptimal:
            for exercise, var in self.var_exercise.items():
                usage = var.varValue
                if isinstance(usage, float) and usage > 0:
                    solution.exercise_list.append(EXERCISE_DICT[exercise])

        return solution
