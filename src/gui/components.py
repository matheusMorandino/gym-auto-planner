from typing import Callable, Optional

import flet as ft


def value_slider_card(
        title: str,
        description: str,
        initial_value: float,
        min_value: float,
        max_value: float,
        on_value_change: Optional[Callable[[float], None]] = None,
        width: int = 360,
        value_field_width: int = 90,
        divisions: Optional[int] = None,
) -> ft.Card:
    """
    Builds a reusable slider card with title, description, value display and callback.
    """
    value_text = ft.TextField(
        value=f"{initial_value:g}",
        text_align=ft.TextAlign.RIGHT,
        width=value_field_width,
        read_only=True,
    )

    slider = ft.Slider(
        min=min_value,
        max=max_value,
        value=initial_value,
        divisions=divisions,
        expand=True,
    )

    def on_slider_update(e: ft.Event[ft.Slider]) -> None:
        current_value = e.control.value
        value_text.value = f"{current_value:g}"
        if on_value_change:
            on_value_change(current_value)
        if e.page:
            e.page.update()

    slider.on_change = on_slider_update

    return ft.Card(
        content=ft.Container(
            width=width,
            padding=16,
            content=ft.Column(
                [
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                    ft.Text(description, size=12, color=ft.Colors.GREY_700),
                    ft.Row([slider, value_text], alignment=ft.MainAxisAlignment.CENTER),
                ],
                tight=True,
                spacing=10,
            ),
        )
    )
