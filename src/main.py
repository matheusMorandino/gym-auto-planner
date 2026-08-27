import flet as ft

from src.gui.planner_page import PlannerPage


def main(page: ft.Page):
    PlannerPage().render(page)


if __name__ == "__main__":
    ft.run(main=main)
