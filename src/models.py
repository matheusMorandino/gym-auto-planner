from dataclasses import dataclass, field

@dataclass
class MuscleSelection:

    selected: set[str] = field(default_factory=set)

    def toggle(self, muscle: str):

        if muscle in self.selected:
            self.selected.remove(muscle)
        else:
            self.selected.add(muscle)

    def clear(self):
        self.selected.clear()

    def get(self):
        return sorted(self.selected)
    