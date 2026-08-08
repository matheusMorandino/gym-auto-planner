import math
import pandas as pd
import itertools
import numpy as np
from typing import List, Dict, Literal, Tuple

from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, LpStatusOptimal, LpAffineExpression

from models.data_models import ScenarioParameters, Exercise, TrainingSolution
from src.consts.mapping import EXERCISE_DICT, MUSCLES_DICT


class LinearSolver:
    def __init__(self, scenario_params: ScenarioParameters):
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
        redundancy between two given exercises(1 is completely different, 0 is identical).
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
            cosine_similar = round(dot_prod / (norm_i * norm_j), 6)

            # Adding cosine distance between i and j to the matrix
            cosine_matrix.at[i, j] = math.sqrt(1 - cosine_similar**2)

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

        # For each pair of used exercises their cosine distance must be larger than the similarity threshold
        for exercise_i, exercise_j in itertools.combinations(self.valid_exercises, 2):
            self.problem += (
                self.scenario_params.similarity_threshold - (2 - (self.var_exercise[exercise_i.name] + self.var_exercise[exercise_j.name])) * 1000
                <= self.exercise_cosine_matrix.at[exercise_i.name, exercise_j.name],
                f'{exercise_i.name}_{exercise_j.name}_similarity_restriction'
            )

    def _create_objective_restriction(self, exclude_solution: int):
        """
        Creates a restriction for the objective function to avoid getting the same solution multiple times during multiple solutions runs.
        :param exclude_solution: Value to exclude from the solution as a restriction.
        """
        self.problem += (
            self._create_objective_function() >= exclude_solution + 1,
            'exclude_previous_solution_restriction'
        )

    def _create_objective_function(self) -> LpAffineExpression:
        """
        Creates the objective function for the linear solver.
        :return: LpAffineExpression for the objective function
        """
        # minimize the total number of exercises done
        total_obj_function = lpSum(
            self.var_exercise[exercise.name]
            for exercise in self.valid_exercises
        )

        return total_obj_function

    def solve_single(self, exclude_solution: int = None) -> TrainingSolution:
        """
        Runs the linear solver for a single solution.
        :param exclude_solution: Value to exclude from the solution as a restriction. This is used to avoid getting the same solution multiple times during multiple solutions runs.
        """
        # Defining problem
        self.problem = LpProblem("Training_Optimization", LpMinimize)

        self._create_variables()
        self._create_restictions()
        if exclude_solution is not None:
            self._create_objective_restriction(exclude_solution)

        self.problem += self._create_objective_function()

        # Solve the problem
        self.problem.solve()

        # Create solution object
        solution = TrainingSolution(
            solution_status=LpStatus[self.problem.status],
            exercise_list=[]
        )

        if self.problem.status == LpStatusOptimal:
            result_dict = dict()
            for exercise_name, var in self.var_exercise.items():
                usage = var.varValue
                if isinstance(usage, float) and usage > 0:
                    result_dict[sum(EXERCISE_DICT[exercise_name].muscle_vector.values())] = EXERCISE_DICT[exercise_name]

            # Ordering the exercises by their total strain value and adding them to the solution
            solution.exercise_list = [result_dict[key] for key in sorted(result_dict.keys())]

        return solution

    def solve_multiple(self, n_solutions: int) -> List[TrainingSolution]:
        """
        Runs the linear solver for multiple solutions. The previous solution is used as a restriction in the next as a way of generation multiple valid but suboptimal solutions.
        :param n_solutions: Number of solutions to generate.
        """
        solutions = []
        exclude_solution = None

        for _ in range(n_solutions):
            solution = self.solve_single(exclude_solution=exclude_solution)
            if solution.solution_status == 'Optimal':
                solutions.append(solution)
                exclude_solution = len(solution.exercise_list)
            else:
                break

        return solutions
