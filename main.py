import random

class MinesGame:
    def __init__(self, grid_size=5, mines_count=3):
        self.grid_size = grid_size
        self.mines_count = mines_count
        self.total_cells = grid_size * grid_size
        self.mines = self.generate_mines()
        self.revealed = []
        self.multiplier = 1.0

    def generate_mines(self):
        return random.sample(range(self.total_cells), self.mines_count)

    def reveal(self, cell):
        if cell in self.revealed:
            return "already"

        if cell in self.mines:
            self.multiplier = 1.0
            return "mine"

        self.revealed.append(cell)
        safe_cells = self.total_cells - self.mines_count
        probability = (safe_cells - len(self.revealed) + 1) / (self.total_cells - len(self.revealed) + 1)

        self.multiplier *= (1 / probability)
        return "safe"

    def get_multiplier(self):
        return round(self.multiplier, 2)