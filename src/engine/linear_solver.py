import pandas as pd
from typing import List, Dict, Literal
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpAffineExpression, LpStatus

from models.data_models import ScenarioParameters
fr


class LinearSolver:
    def __init__(self, scenario_params: ScenarioParameters):
        self.scenario_params = scenario_params

        self.problem = None

    def _create_variables(self):
        """
        Creates variables needed for linear solver
        :return:
        """
        #



    def solve(self):
        # Defining problem
        self.problem = LpProblem("Training_Optimization", LpMinimize)

        self._create_variables()
