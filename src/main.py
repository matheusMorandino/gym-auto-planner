import flet as ft

from gui.components import value_slider_card


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
}


def build_param_slider(key: str) -> ft.Card:
    config = scenario_params[key]

    def on_change(value: float) -> None:
        scenario_params[key]["value"] = value

    return value_slider_card(
        title=config["title"],
        description=config["description"],
        initial_value=config["value"],
        min_value=config["min"],
        max_value=config["max"],
        on_value_change=on_change,
        divisions=20,
    )


def main(page: ft.Page):
    page.title = "Exercise auto planner"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(
        ft.Row(
            [
                build_param_slider("training_target"),
                build_param_slider("overtraining_delta"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),

    )


if __name__ == "__main__":
    ft.run(main=main)
