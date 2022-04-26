class Game:
    def __init__(self, player):
        self.player = player


class TicTacToe(Game):
    def __init__(self, player):
        Game.__init__(self, player)


class Gallows(Game):
    def __init__(self, player):
        Game.__init__(self, player)