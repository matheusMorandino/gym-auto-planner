from nicegui import ui

from consts.ui_models import MuscleSelection
from consts.mapping import SVG_TO_MUSCLES
from src.svg_loader import load_svg


class MuscleSelector:

    def __init__(self, svg_path):

        self.model = MuscleSelection()

        svg = load_svg(svg_path)

        self.html = ui.add_body_html(svg)

        ui.on(
            "muscle-selection",
            self._selection_changed
        )

    async def _selection_changed(self, e):

        self.model.clear()

        for region in e.args:

            for muscle in SVG_TO_MUSCLES.get(region, []):

                self.model.toggle(muscle)

    def get_selected(self):

        return self.model.get()

    def clear(self):

        self.model.clear()