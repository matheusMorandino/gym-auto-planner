import flet as ft

from src.consts.mapping import EQUIPMENT_DICT, EXERCISE_DICT, MUSCLE_GROUPS
from src.engine.scenario_handler import ScenarioHandler
from src.gui.components import SliderCard, MultiSelectSearchCard


scenario_params = {
    "training_target": {
        "value": 3,
        "title": "Training target",
        "description": "Desired average strain level for the selected workout.",
        "min": 1,
        "max": 5,
    },
    "overtraining_delta": {
        "value": 2,
        "title": "Overtraining delta",
        "description": "Allowed margin above target before penalty increases.",
        "min": 0,
        "max": 5,
    },
    "similarity_threshold": {
        "value": 0.4,
        "title": "Similarity threshold",
        "description": "Threshold for considering exercises as too similar.",
        "min": 0,
        "max": 1,
    },
    "valid_equipments": {
        "value": [],
        "options": list(EQUIPMENT_DICT.keys()),
        "title": "Valid equipments",
        "description": "Choose the equipments you want to include in your workout. If left empty all equipments will be included.",
    },
    "excluded_exercises": {
        "value": [],
        "options": list(EXERCISE_DICT.keys()),
        "title": "Excluded exercises",
        "description": "Choose the exercises you want to exclude from your workout."
    },
    "target_muscle_groups": {
        "value": [],
        "options": list(MUSCLE_GROUPS.keys()),
        "title": "Target muscle groups",
        "description": "Choose the muscle groups you want to target in your workout."
    }
}


def build_param_slider(key: str) -> ft.Card:
    config = scenario_params[key]

    def on_change(value: float) -> None:
        scenario_params[key]["value"] = value

    return SliderCard(
        title=config["title"],
        description=config["description"],
        initial_value=config["value"],
        min_value=config["min"],
        max_value=config["max"],
        on_value_change=on_change,
        divisions=20,
    )


def build_equipment_card():
    return MultiSelectSearchCard(
        title=scenario_params["valid_equipments"]["title"],
        description=scenario_params["valid_equipments"]["description"],
        options=scenario_params["valid_equipments"]["options"],
        on_value_change=lambda value: scenario_params["valid_equipments"].update({"value": value}),
        width=550
    )


def build_target_muscles_card():
    return MultiSelectSearchCard(
        title=scenario_params["target_muscle_groups"]["title"],
        description=scenario_params["target_muscle_groups"]["description"],
        options=scenario_params["target_muscle_groups"]["options"],
        on_value_change=lambda value: scenario_params["target_muscle_groups"].update({"value": value}),
        width=550
    )


def build_excluded_exercises_card():
    return MultiSelectSearchCard(
        title=scenario_params["excluded_exercises"]["title"],
        description=scenario_params["excluded_exercises"]["description"],
        options=scenario_params["excluded_exercises"]["options"],
        on_value_change=lambda value: scenario_params["excluded_exercises"].update({"value": value}),
        width=1120
    )


def build_print_button():
    """
    Creates button that prints all value present in scenario_parameters when pressed. This is for testing purposes only.
    :return: flet.Button
    """
    def on_click(e):
        print("Current scenario parameters:")
        for key, value in scenario_params.items():
            print(f"{key}: {value['value'] if 'value' in value else value}")

    return ft.ElevatedButton("Print scenario parameters", on_click=on_click)


def build_run_solution_button():
    """
    Creates button that runs a solution on the ScenarioHandler based on the defined parameters. This is for testing purposes only.
    """
    def on_click(e):
        handler = ScenarioHandler(
            training_target=scenario_params["training_target"]["value"],
            overtraining_delta=scenario_params["overtraining_delta"]["value"],
            similarity_threshold=scenario_params["similarity_threshold"]["value"],
            group_list=scenario_params["target_muscle_groups"]["value"],
            valid_equipments=scenario_params["valid_equipments"]["value"]
        )
        solutions = handler.get_training_plans(n_target=3)

        for i, solution in enumerate(solutions):
            print(f">>> Solution {i + 1}:")
            for exercise in solution.exercise_list:
                print(f"- {exercise.name}")
            print('\n')

    return ft.ElevatedButton("Run solution", on_click=on_click)


def main(page: ft.Page):
    page.title = "Exercise auto planner"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Row(
            [
                build_param_slider("training_target"),
                build_param_slider("overtraining_delta"),
                build_param_slider("similarity_threshold"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                build_equipment_card(),
                build_target_muscles_card(),
            ],
            alignment = ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                build_excluded_exercises_card()
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                build_print_button(),
                build_run_solution_button()
            ],
            alignment = ft.MainAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    ft.run(main=main)
