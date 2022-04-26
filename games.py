from random import randint
from telebot import types
from json import dumps, loads

WINNING_COMBINATIONS = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [1, 4, 7],
    [2, 5, 8],
    [3, 6, 9],
    [1, 5, 9],
    [3, 5, 7]
]


class Game:
    def __init__(self, player):
        self.player = player

    def start_game(self):
        pass

    def move(self, **kwargs):
        pass

    def check_game_over(self):
        pass


class TicTacToeBot:
    def __init__(self, state, symbol):
        self.state: dict = state
        self.symbol = symbol

    def guess_cell_number(self) -> int:
        try:
            number = randint(1, 9)
            return number if self.state.get(number) == " " else self.guess_cell_number()
        except RecursionError:
            return 0

    def find_good_position(self, symbol) -> int:
        for combination in WINNING_COMBINATIONS:
            overlaps_num = 0
            for i in range(3):
                if self.state.get(combination[i]) == symbol:
                    overlaps_num += 1

            if overlaps_num == 2:
                for i in range(3):
                    if self.state.get(combination[i]) == " ":
                        return combination[i]

    def choose_cell_number(self) -> int:
        cell_number = self.find_good_position(self.symbol)
        if cell_number:
            return cell_number
        else:
            cell_number = self.find_good_position("X" if self.symbol == "O" else "O")

            if cell_number:
                return cell_number

        return self.guess_cell_number()

    def move(self):
        number = self.choose_cell_number()
        self.state.update({number: self.symbol})


class TicTacToe(Game):
    def __init__(self, player):
        self.symbol = "X" if randint(0, 1) else "O"
        self.state = {i: " " for i in range(1, 10)}
        self.message_id = 0
        self.bot = TicTacToeBot(self.state, "X" if self.symbol == "O" else "O")
        Game.__init__(self, player)

    def send_field(self):
        keyboard = types.InlineKeyboardMarkup()
        row = []
        for cell_number, text in self.state.items():
            row.append(types.InlineKeyboardButton(
                text=text,
                callback_data=dumps({"type": "in game", "data": cell_number}))
            )

            if cell_number % 3 == 0:
                keyboard.add(*row)
                row = []

        if not self.message_id:
            self.message_id = self.player.send_inline_keyboard_markup(f"You are {self.symbol}", keyboard).id
        else:
            self.message_id = self.player.edit_message_reply_markup(self.message_id, keyboard).id

    def start_game(self):
        self.send_field()

        if self.symbol == "O":
            self.bot.move()
            self.send_field()

    def move(self, **kwargs):
        cell_number: dict = kwargs.get("data")
        if self.state.get(cell_number) == " ":
            self.state.update({cell_number: self.symbol})
            self.send_field()
            if self.check_game_over():
                return
            self.bot.move()
            self.send_field()
            if self.check_game_over():
                return

    def check_game_over(self):
        if tuple(self.state.values()).count(" ") == 0 or self.state.get(0) is not None:
            self.player.game_over()
            self.player.send_text(f"Draw!")
            return True

        for combination in WINNING_COMBINATIONS:
            if self.state.get(combination[0]) \
                    == self.state.get(combination[1]) \
                    == self.state.get(combination[2]) \
                    != " ":
                self.player.game_over()
                self.player.send_text(f"{self.state.get(combination[0])} won!")
                return True


class Gallows(Game):
    def __init__(self, player):
        Game.__init__(self, player)
