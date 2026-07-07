from nicegui import ui

from src.api import MuscleSelectorAPI
from src.muscle_selector import MuscleSelector

selector = MuscleSelector(
    "assets/Muscles-simplified.svg"
)

api = MuscleSelectorAPI(selector)


def show():

    print(api.selected_muscles())


ui.button(
    "Print Selection",
    on_click=show
)

ui.run()