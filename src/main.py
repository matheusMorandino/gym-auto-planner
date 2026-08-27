import flet as ft

from src.engine.scenario_handler import ScenarioHandler
from src.gui.components import SliderCard, MultiSelectSearchCard
from src.models.state_models import InterfaceState


scenario_params = InterfaceState()


def build_param_slider(key: str) -> ft.Card:
    config = getattr(scenario_params, key)

    def on_change(value: float) -> None:
        setattr(scenario_params, key, value)

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


def build_equipment_card():
    return MultiSelectSearchCard(
        title=scenario_params.valid_equipments.title,
        description=scenario_params.valid_equipments.description,
        options=scenario_params.valid_equipments.options,
        on_value_change=lambda value: setattr(scenario_params, "valid_equipments", value),
        expand=True,
    )


def build_target_muscles_card():
    return MultiSelectSearchCard(
        title=scenario_params.target_muscle_groups.title,
        description=scenario_params.target_muscle_groups.description,
        options=scenario_params.target_muscle_groups.options,
        on_value_change=lambda value: setattr(scenario_params, "target_muscle_groups", value),
        expand=True,
    )


def build_excluded_exercises_card():
    return MultiSelectSearchCard(
        title=scenario_params.excluded_exercises.title,
        description=scenario_params.excluded_exercises.description,
        options=scenario_params.excluded_exercises.options,
        on_value_change=lambda value: setattr(scenario_params, "excluded_exercises", value),
        expand=True,
    )


def build_forced_exercises_card():
    return MultiSelectSearchCard(
        title=scenario_params.forced_exercises.title,
        description=scenario_params.forced_exercises.description,
        options=scenario_params.forced_exercises.options,
        on_value_change=lambda value: setattr(scenario_params, "forced_exercises", value),
        expand=True,
    )


def build_print_button():
    """
    Creates button that prints all value present in scenario_parameters when pressed. This is for testing purposes only.
    :return: flet.Button
    """
    def on_click(e):
        print("Current scenario parameters:")
        for key, value in scenario_params.__dict__.items():
            print(f"{key}: {value.value if hasattr(value, 'value') else value}")

    return ft.Button("Print scenario parameters", on_click=on_click)


def build_run_solution_button():
    """
    Creates button that runs a solution on the ScenarioHandler based on the defined parameters. This is for testing purposes only.
    """
    def on_click(e):
        handler = ScenarioHandler(
            training_target=scenario_params.training_target.value,
            overtraining_delta=scenario_params.overtraining_delta.value,
            similarity_threshold=scenario_params.similarity_threshold.value,
            group_list=scenario_params.target_muscle_groups.value,
            valid_equipments=scenario_params.valid_equipments.value,
            exercise_blacklist=scenario_params.excluded_exercises.value,
            forced_exercises=scenario_params.forced_exercises.value,
        )
        solutions = handler.get_training_plans(n_target=3)

        for i, solution in enumerate(solutions):
            print(f">>> Solution {i + 1}:")
            for exercise in solution.exercise_list:
                print(f"- {exercise.name}")
            print('\n')

    return ft.Button("Run solution", on_click=on_click)


def main(page: ft.Page):
    page.title = "Exercise auto planner"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    excluded_card = build_excluded_exercises_card()
    forced_exercises_card = build_forced_exercises_card()

    page.add(
        ft.Row(
            [
                build_param_slider("training_target"),
                build_param_slider("overtraining_delta"),
                build_param_slider("similarity_threshold"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        ),
        ft.Row(
            [
                build_equipment_card(),
                build_target_muscles_card(),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        ),
        ft.Row(
            [
                excluded_card,
                forced_exercises_card
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        ),
        ft.Row(
            [
                build_print_button(),
                build_run_solution_button()
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    ft.run(main=main)
