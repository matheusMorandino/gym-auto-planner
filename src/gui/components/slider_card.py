from typing import Callable, Optional

import flet as ft


class SliderCard(ft.Card):
    """
    Builds a reusable slider card with title, description, value display and callback.
    """
    def __init__(
        self,
        title: str,
        description: str,
        initial_value: float,
        min_value: float,
        max_value: float,
        on_value_change: Optional[Callable[[float], None]] = None,
        divisions: Optional[int] = None,
        expand: bool = False,
    ):
        self.on_value_change = on_value_change

        self.slider = self._create_slider(
            min_value=min_value,
            max_value=max_value,
            initial_value=initial_value,
            divisions=divisions,
        )

        self.value_text = self._create_value_text(
            initial_value=initial_value,
        )

        self.slider.on_change = self.on_slider_update

        super().__init__(
            expand=expand,
            content=ft.Container(
                padding=16,
                expand=expand,
                content=ft.Column(
                    [
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(description, size=12, color=ft.Colors.GREY_700),
                        ft.Row(
                            [self.slider, self.value_text],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    tight=True,
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            )
        )

    @staticmethod
    def _create_slider(min_value, max_value, initial_value, divisions):
        return ft.Slider(
            min=min_value,
            max=max_value,
            value=initial_value,
            divisions=divisions,
            expand=True,
        )

    @staticmethod
    def _create_value_text(initial_value):
        return ft.Text(
            value=f"{initial_value:g}",
            text_align=ft.TextAlign.RIGHT,
        )

    def on_slider_update(self, e: ft.Event[ft.Slider]) -> None:
        current_value = e.control.value
        if current_value is None:
            return

        self.value_text.value = f"{current_value:g}"

        if self.on_value_change:
            self.on_value_change(current_value)

        if e.page:
            e.page.update()