import math
import pandas as pd
import itertools
import numpy as np
from typing import List, Dict, Literal, Tuple
from copy import deepcopy

from pandas.core.ops import invalid, invalid_comparison
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, LpStatusOptimal, LpAffineExpression

from src.models.data_models import ModelParameters, Exercise, TrainingSolution
from src.consts.mapping import EXERCISE_DICT, MUSCLES_DICT


class LinearSolver:
    def __init__(self, scenario_params: ModelParameters):
        self.scenario_params: ModelParameters = scenario_params

        self.strain_matrix: pd.DataFrame = self._build_strain_matrix()
        self.exercise_cosine_matrix: pd.DataFrame = self._build_cosine_matrix()

        self.problem = None

    def _get_invalid_exercises(self) -> List[Exercise]:
        """
        Returns a list of invalid exercises based on the scenario parameters.
        This list is composed of exercises that are not in the valid equipment list, or that are in the exercise blacklist.
        If an exercise is in the forced exercises list, it will not be considered invalid even if it is in the blacklist or not in the valid equipment list.
        :return:
        """
        invalid_exercises = []

        for exercise in EXERCISE_DICT.values():
            checks = []

            checks.append(exercise.equipment not in self.scenario_params.valid_equipments)
            checks.append(exercise in self.scenario_params.exercise_blacklist)

            if any(checks):
                invalid_exercises.append(exercise)

        # Remove forced exercises from the invalid exercises list
        invalid_exercises = [exercise for exercise in invalid_exercises if exercise not in self.scenario_params.forced_exercises]

        return invalid_exercises

    def _build_cosine_matrix(self) -> pd.DataFrame:
        """
        Create a cosine distance matrix between all present exercises. Used in measuring
        redundancy between two given exercises(1 is completely different, 0 is identical).
        :return:
        """
        cosine_matrix = pd.DataFrame(
            index=[exercise.name for exercise in EXERCISE_DICT.values()],
            columns=[exercise.name for exercise in EXERCISE_DICT.values()],
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
            columns=[exercise.name for exercise in EXERCISE_DICT.values()]
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
            in EXERCISE_DICT.values()
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
        for exercise_i, exercise_j in itertools.combinations(EXERCISE_DICT.values(), 2):
            self.problem += (
                self.scenario_params.similarity_threshold - (2 - (self.var_exercise[exercise_i.name] + self.var_exercise[exercise_j.name])) * 1000
                <= self.exercise_cosine_matrix.at[exercise_i.name, exercise_j.name],
                f'{exercise_i.name}_{exercise_j.name}_similarity_restriction'
            )

        # Force exclusion of exercises listed in the scenario's exercise blacklist
        for exercise in self._get_invalid_exercises():
            if exercise.name in self.var_exercise:
                self.problem += (
                    self.var_exercise[exercise.name] == 0,
                    f'{exercise.name}_blacklist_restriction'
                )

        # Force usage of exercises listed in the scenario's forced exercises list
        for exercise in self.scenario_params.forced_exercises:
            if exercise.name in self.var_exercise:
                self.problem += (
                    self.var_exercise[exercise.name] == 1,
                    f'{exercise.name}_forced_restriction'
                )

    def _create_objective_function(self) -> LpAffineExpression:
        """
        Creates the objective function for the linear solver.
        :return: LpAffineExpression for the objective function
        """
        # minimize the total number of exercises done
        total_obj_function = lpSum(
            self.var_exercise[exercise.name]
            for exercise in EXERCISE_DICT.values()
        )

        return total_obj_function

    def solve_single(self, scenario_params: ModelParameters) -> TrainingSolution:
        """
        Runs the linear solver for a single solution.
        """
        # Defining problem
        self.problem = LpProblem("Training_Optimization", LpMinimize)

        self._create_variables()
        self._create_restictions()

        self.problem += self._create_objective_function()

        # Solve the problem
        self.problem.solve()

        # Create solution object
        solution = TrainingSolution(
            scenario_params=deepcopy(scenario_params),
            solution_status=LpStatus[self.problem.status],
            objective_value=self.problem.objective.value(),
            exercise_list=[]
        )

        if self.problem.status == LpStatusOptimal:
            result_list = []
            for exercise_name, var in self.var_exercise.items():
                usage = var.varValue
                if isinstance(usage, float) and usage > 0:
                    result_list.append(EXERCISE_DICT[exercise_name])

            # Ordering the exercises by their total strain value and adding them to the solution
            solution.exercise_list = sorted(result_list, key=lambda x: sum(x.muscle_vector.values()))

        return solution

    def solve_multiple(self, n_solutions: int) -> List[TrainingSolution]:
        """
        Runs the linear solver for multiple solutions. The previous solution is used as a restriction in the next as a way of generation multiple valid but suboptimal solutions.
        :param n_solutions: Number of solutions to generate.
        """
        solutions = []

        for _ in range(n_solutions):
            solution = self.solve_single(scenario_params=self.scenario_params)

            # Pick a percentage of exercises from the previous solution to be excluded in the next solution.
            # This is to ensure that the next solution is different from the previous one.
            p = self.scenario_params.iteration_novelty_threshold
            if solution.solution_status == 'Optimal' and len(solution.exercise_list) > 0:
                num_exercises_to_exclude = max(1, int(len(solution.exercise_list) * p))
                exercises_to_exclude = np.random.choice(solution.exercise_list, size=num_exercises_to_exclude, replace=False)
                self.scenario_params.exercise_blacklist.extend(exercises_to_exclude)

                solutions.append(solution)
            else:
                break

        return solutions
