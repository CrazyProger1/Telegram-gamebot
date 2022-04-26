from random import randint
from telebot import types
from json import dumps, load

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
            self.message_id = self.player.send_inline_keyboard_markup(
                self.player.translator["symbol_text"].replace("@s", self.symbol)
                , keyboard)
        else:
            self.player.edit_message_reply_markup(self.message_id, keyboard)

    def start_game(self):
        self.send_field()

        if self.symbol == "O":
            self.bot.move()
            self.send_field()

    def move(self, **kwargs):
        cell_number: int = kwargs.get("data")
        if self.state.get(cell_number) == " ":
            self.state.update({cell_number: self.symbol})
            self.send_field()
            if self.check_game_over():
                self.player.send_games()
                return
            self.bot.move()
            self.send_field()
            if self.check_game_over():
                self.player.send_games()
                return

    def check_game_over(self):
        for combination in WINNING_COMBINATIONS:
            if self.state.get(combination[0]) \
                    == self.state.get(combination[1]) \
                    == self.state.get(combination[2]) \
                    != " ":
                self.player.game_over()
                won = self.state.get(combination[0])
                self.player.send_text(
                    self.player.translator["won_text"].replace("@s", won) + ("🎉", "🤖")[won != self.symbol])
                return True

        if tuple(self.state.values()).count(" ") == 0 or self.state.get(0) is not None:
            self.player.game_over()
            self.player.send_text(self.player.translator["draw_text"])
            return True


class Gallows(Game):
    def __init__(self, player):
        self.word, self.riddle = self.get_random_riddle(player.translator["riddles_pack"])
        self.available_letters = list(player.translator["alphabet"])
        self.guessed = "".join("_" if letter in self.available_letters else letter for letter in self.word)
        self.keyboard_message_id = 0
        self.riddle_message_id = 0
        self.gallows_message_id = 0
        self.guessed_message_id = 0
        self.status = 6
        Game.__init__(self, player)

    @staticmethod
    def get_random_riddle(filepath):
        with open(filepath, "r", encoding='utf-8') as rf:
            riddles: dict = load(rf)
        random_word = tuple(riddles.keys())[randint(0, len(riddles) - 1)]
        return random_word, riddles.get(random_word)

    def send_keyboard(self):
        keyboard = types.InlineKeyboardMarkup()
        row = []
        for letter in self.available_letters:
            row.append(types.InlineKeyboardButton(
                text=letter,
                callback_data=dumps({"type": "in game", "data": letter})))

            if len(row) == 3:
                keyboard.add(*row)
                row = []

        if len(row) > 0:
            keyboard.add(*row)

        if not self.keyboard_message_id:
            self.keyboard_message_id = self.player.send_inline_keyboard_markup(
                self.player.translator["letter_choosing_text"], keyboard)
        else:
            self.player.edit_message_reply_markup(self.keyboard_message_id, keyboard)

    def send_riddle(self):
        if not self.riddle_message_id:
            self.riddle_message_id = self.player.send_text(
                self.player.translator["riddle_text"].replace("@r", self.riddle))

    def send_guessed(self):

        if not self.guessed_message_id:
            self.guessed_message_id = self.player.send_text(
                self.player.translator["guessed_text"].replace("@g", self.guessed))
        else:
            self.player.edit_text(self.guessed_message_id,
                                  self.player.translator["guessed_text"].replace("@g", self.guessed))

    def send_gallows(self):
        if not self.gallows_message_id:
            self.gallows_message_id = self.player.send_photo(f"imgs/{self.status}.png")
        else:
            self.player.edit_photo(self.gallows_message_id,
                                   f"imgs/{self.status}.png")

    def start_game(self):
        self.send_gallows()
        self.send_riddle()
        self.send_guessed()
        self.send_keyboard()

    def move(self, **kwargs):
        supposed_letter: str = kwargs.get("data")

        if supposed_letter in self.word:
            for i, letter in enumerate(self.word):
                if letter == supposed_letter:
                    self.guessed = self.guessed[:i] + letter + self.guessed[i + 1:]

            self.send_guessed()
            if self.check_game_over():
                self.player.send_games()
                return

        else:
            self.status -= 1
            if self.check_game_over():
                self.player.send_games()
                return
            self.send_gallows()

        self.available_letters.remove(supposed_letter)
        self.send_keyboard()

    def check_game_over(self):
        if self.status == 0:
            self.player.send_text(self.player.translator["game_over_text"])
            self.player.game_over()
            return True

        if self.guessed.count("_") == 0:
            self.player.send_text(self.player.translator["you_won_text"])
            self.player.game_over()
            return True
