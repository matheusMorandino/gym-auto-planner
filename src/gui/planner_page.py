import flet as ft

from src.engine.scenario_handler import ScenarioHandler
from src.gui.components import SliderCard, MultiSelectSearchCard
from src.models.state_models import InterfaceState


class PlannerPage:
    def __init__(self):
        self.scenario_params = InterfaceState()

    def build_param_slider(self, key: str) -> ft.Card:
        config = getattr(self.scenario_params, key)

        def on_change(value: float) -> None:
            setattr(self.scenario_params, key, value)

        return SliderCard(
            title=config.title,
            description=config.description,
            initial_value=config.value,
            min_value=config.min,
            max_value=config.max,
            on_value_change=on_change,
            divisions=20,
            expand=True,
        )

    def build_equipment_card(self):
        return MultiSelectSearchCard(
            title=self.scenario_params.valid_equipments.title,
            description=self.scenario_params.valid_equipments.description,
            options=self.scenario_params.valid_equipments.options,
            on_value_change=lambda value: setattr(self.scenario_params.valid_equipments, "value", value),
            expand=True,
        )

    def build_target_muscles_card(self):
        return MultiSelectSearchCard(
            title=self.scenario_params.target_muscle_groups.title,
            description=self.scenario_params.target_muscle_groups.description,
            options=self.scenario_params.target_muscle_groups.options,
            on_value_change=lambda value: setattr(self.scenario_params.target_muscle_groups, "value", value),
            expand=True,
        )

    def build_excluded_exercises_card(self):
        return MultiSelectSearchCard(
            title=self.scenario_params.excluded_exercises.title,
            description=self.scenario_params.excluded_exercises.description,
            options=self.scenario_params.excluded_exercises.options,
            on_value_change=lambda value: setattr(self.scenario_params.excluded_exercises, "value", value),
            expand=True,
        )

    def build_forced_exercises_card(self):
        return MultiSelectSearchCard(
            title=self.scenario_params.forced_exercises.title,
            description=self.scenario_params.forced_exercises.description,
            options=self.scenario_params.forced_exercises.options,
            on_value_change=lambda value: setattr(self.scenario_params.forced_exercises, "value", value),
            expand=True,
        )

    def build_print_button(self):
        """
        Creates button that prints all value present in scenario_parameters when pressed. This is for testing purposes only.
        :return: flet.Button
        """
        def on_click(e):
            print(">> Current scenario parameters:")
            for key, value in self.scenario_params.__dict__.items():
                print(f"{key}: {value.value if hasattr(value, 'value') else value}")

        return ft.Button("Print scenario parameters", on_click=on_click)

    def build_run_solution_button(self):
        """
        Creates button that runs a solution on the ScenarioHandler based on the defined parameters. This is for testing purposes only.
        """
        def on_click(e):
            handler = ScenarioHandler(
                training_target=self.scenario_params.training_target.value,
                overtraining_delta=self.scenario_params.overtraining_delta.value,
                similarity_threshold=self.scenario_params.similarity_threshold.value,
                group_list=self.scenario_params.target_muscle_groups.value,
                valid_equipments=self.scenario_params.valid_equipments.value,
                exercise_blacklist=self.scenario_params.excluded_exercises.value,
                forced_exercises=self.scenario_params.forced_exercises.value,
            )
            solutions = handler.get_training_plans(n_target=3)

            for i, solution in enumerate(solutions):
                print(f">>> Solution {i + 1}:")
                for exercise in solution.exercise_list:
                    print(f"- {exercise.name}")
                print('\n')

        return ft.Button("Run solution", on_click=on_click)

    def render(self, page: ft.Page) -> None:
        page.title = "Exercise auto planner"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER

        page.add(
            # Scenario parameters
            ft.Row(
                [
                    self.build_param_slider("training_target"),
                    self.build_param_slider("overtraining_delta"),
                    self.build_param_slider("similarity_threshold"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            ft.Row(
                [
                    self.build_equipment_card(),
                    self.build_target_muscles_card(),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            ft.Row(
                [
                    self.build_excluded_exercises_card(),
                    self.build_forced_exercises_card()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            ),
            ft.Row(
                [
                    self.build_print_button(),
                    self.build_run_solution_button()
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),

            # Divisor between the parameter sliders and the equipment/muscle/exercise cards
            ft.Divider(height=1, thickness=1, color=ft.Colors.GREY_400, opacity=0.5),

            # Results section

        )
