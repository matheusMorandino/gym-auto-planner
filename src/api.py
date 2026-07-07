class MuscleSelectorAPI:

    def __init__(self, selector):

        self.selector = selector

    def selected_muscles(self):

        return self.selector.get_selected()

    def clear(self):

        self.selector.clear()

    def is_selected(self, muscle):

        return muscle in self.selector.get_selected()

    def count(self):

        return len(self.selector.get_selected())