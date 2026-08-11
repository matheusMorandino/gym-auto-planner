from typing import Callable, Optional, List

import flet as ft


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
            on_focus=self._clear_text_field,
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

    def _clear_text_field(self, e: ft.Event):
        self.dropdown.value = None
        self.dropdown.update()

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
