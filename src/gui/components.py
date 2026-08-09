from gc import enable
from typing import Callable, Optional, List

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
        width: int = 360,
        value_field_width: int = 90,
        divisions: Optional[int] = None
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
            value_field_width=value_field_width
        )

        self.slider.on_change = self.on_slider_update

        super().__init__(
            content=ft.Container(
                width=width,
                padding=16,
                content=ft.Column(
                    [
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(description, size=12, color=ft.Colors.GREY_700),
                        ft.Row([self.slider, self.value_text], alignment=ft.MainAxisAlignment.CENTER),
                    ],
                    tight=True,
                    spacing=10,
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
    def _create_value_text(initial_value, value_field_width):
        return ft.TextField(
            value=f"{initial_value:g}",
            text_align=ft.TextAlign.RIGHT,
            width=value_field_width,
            read_only=True,
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


class MultiSelectSearchCard(ft.Card):
    """
    Builds a reusable multi-select search card with title, description, and callback.
    """
    items: List[str] = None

    def __init__(
        self,
        title: str,
        description: str,
        options: list[str],
        on_value_change: Optional[Callable[[List[str]], None]] = None,
        width: int = 360,
    ):
        self.on_value_change = on_value_change

        self.dropdown = ft.Dropdown(
            options=[ft.DropdownOption(option) for option in options],
            hint_text="Select options",
            width=width - 32,
            on_select=self._update_items_list,
            editable=True,
            enable_filter=True,
        )

        self.chips = ft.Row([], wrap=True)

        super().__init__(
            content=ft.Container(
                width=width,
                padding=16,
                content=ft.Column(
                    [
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(description, size=12, color=ft.Colors.GREY_700),
                        self.dropdown,
                        self.chips
                    ],
                    tight=True,
                    spacing=10,
                ),
            )
        )

    def _update_items_list(self, e: ft.Dropdown):
        val = e.control.value

        if (self.items is None) or (val not in self.items):
            if self.items is None:
                self.items = [val]
            elif not val in self.items:
                self.items.append(val)

            # Update chips
            self.chips.controls.append(
                ft.Chip(
                    label=val,
                    on_delete=lambda e, value=val: self._remove_item(e, value)
                )
            )

        # Update callback reference
        if self.on_value_change:
            self.on_value_change(self.items)

    def _remove_item(self, e: ft.Event, value: str):
        if self.items is not None and value in self.items:
            self.items.remove(value)
        self.chips.controls = [chip for chip in self.chips.controls if chip.label != value]

        # Update callback reference
        if self.on_value_change:
            self.on_value_change(self.items)

        if e.page:
            e.page.update()
