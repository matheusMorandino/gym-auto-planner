import flet as ft

from src.consts.mapping import EQUIPMENT_DICT
from gui.components import SliderCard, MultiSelectSearchCard


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
                build_equipment_card()
            ],
            alignment = ft.MainAxisAlignment.CENTER,
        ),
        ft.Row(
            [
                build_print_button()
            ],
            alignment = ft.MainAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    ft.run(main=main)
