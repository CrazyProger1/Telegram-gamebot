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

    def check_game_over(self) -> bool:
        return False


class TicTacToeBot:
    def __init__(self, state, symbol):
        self._state: dict = state
        self._symbol = symbol
        self._enemy_symbol = "X" if self._symbol == "O" else "O"
        self._first_steps_strategies = ((5, 3, 1), (1, 5, 7), (9, 5, 3),
                                        (7, 9, 5), (7, 1, 3), (1, 3, 9),
                                        (7, 3, 9), (7, 9, 1))

        self._strategy: tuple | None = None
        self._steps_counter = 0

    def _is_cell_free(self, cell: int):
        return self._state[cell] == " "

    def _is_cells_free(self, cells: tuple[int]):
        output = []
        for cell in cells:
            output.append(self._state[cell] == " ")

        return all(output)

    def _select_strategy(self, tries=0) -> tuple[int] | None:
        if tries > len(self._first_steps_strategies):
            return None

        strategy = self._first_steps_strategies[randint(0, len(self._first_steps_strategies) - 1)]
        if self._is_cells_free(strategy):
            return strategy

        return self._select_strategy(tries + 1)

    def _guess_cell_number(self) -> int:
        if self._strategy is None:
            self._strategy = self._select_strategy()

        if self._steps_counter < 3 and self._strategy is not None:
            number = self._strategy[self._steps_counter]
            if self._is_cell_free(number):
                self._steps_counter += 1
                return number

        try:
            number = randint(1, 9)
            return number if self._is_cell_free(number) else self._guess_cell_number()
        except RecursionError:
            return 0

    def _find_good_position(self, symbol) -> int:
        for combination in WINNING_COMBINATIONS:
            overlaps_num = 0
            for i in range(3):
                if self._state.get(combination[i]) == symbol:
                    overlaps_num += 1

            if overlaps_num == 2:
                for i in range(3):
                    if self._is_cell_free(combination[i]):
                        return combination[i]

    def _choose_cell_number(self) -> int:
        cell_number = self._find_good_position(self._symbol)
        if cell_number:
            return cell_number
        else:
            cell_number = self._find_good_position(self._enemy_symbol)

            if cell_number:
                return cell_number

        return self._guess_cell_number()

    def move(self):
        number = self._choose_cell_number()
        self._state.update({number: self._symbol})


class TicTacToe(Game):
    def __init__(self, player):
        self._symbol = "X" if randint(0, 1) else "O"
        self._state = {i: " " for i in range(1, 10)}
        self._message_id = 0
        self._bot = TicTacToeBot(self._state, "X" if self._symbol == "O" else "O")
        Game.__init__(self, player)

    def _is_cell_free(self, cell):
        return self._state.get(cell) == " "

    def _send_field(self):
        keyboard = types.InlineKeyboardMarkup()
        row = []
        for cell_number, text in self._state.items():
            row.append(types.InlineKeyboardButton(
                text=text,
                callback_data=dumps({"type": "in game", "data": cell_number}))
            )

            if cell_number % 3 == 0:
                keyboard.add(*row)
                row = []

        if not self._message_id:
            self._message_id = self.player.send_inline_keyboard_markup(
                self.player.translator["symbol_text"].replace("@s", self._symbol)
                , keyboard)
        else:
            self.player.edit_message_reply_markup(self._message_id, keyboard)

    def start_game(self):
        self._send_field()
        if self._symbol == "O":
            self._bot.move()
            self._send_field()

    def move(self, **kwargs):
        cell_number: int = kwargs.get("data")
        if not self._is_cell_free(cell_number):
            return

        self._state.update({cell_number: self._symbol})
        self._send_field()
        if self.check_game_over():
            self.player.send_games()
            return

        self._bot.move()
        self._send_field()
        if self.check_game_over():
            self.player.send_games()
            return

    def check_game_over(self):
        for combination in WINNING_COMBINATIONS:
            if self._state.get(combination[0]) \
                    == self._state.get(combination[1]) \
                    == self._state.get(combination[2]) \
                    != " ":
                self.player.game_over()
                won = self._state.get(combination[0])
                self.player.send_text(
                    self.player.translator["won_text"].replace("@s", won) + ("🎉", "🤖")[won != self._symbol])
                return True

        if tuple(self._state.values()).count(" ") == 0 or self._state.get(0) is not None:
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
        return random_word.casefold(), riddles.get(random_word)

    def _send_keyboard(self):
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

    def _send_riddle(self):
        if not self.riddle_message_id:
            self.riddle_message_id = self.player.send_text(
                self.player.translator["riddle_text"].replace("@r", self.riddle))

    def _send_guessed(self):

        if not self.guessed_message_id:
            self.guessed_message_id = self.player.send_text(
                self.player.translator["guessed_text"].replace("@g", self.guessed))
        else:
            self.player.edit_text(self.guessed_message_id,
                                  self.player.translator["guessed_text"].replace("@g", self.guessed))

    def _send_gallows(self):
        if not self.gallows_message_id:
            self.gallows_message_id = self.player.send_photo(f"imgs/{self.status}.png")
        else:
            self.player.edit_photo(self.gallows_message_id,
                                   f"imgs/{self.status}.png")

    def start_game(self):
        self._send_gallows()
        self._send_riddle()
        self._send_guessed()
        self._send_keyboard()

    def move(self, **kwargs):
        supposed_letter: str = kwargs.get("data")

        if supposed_letter in self.word:
            for i, letter in enumerate(self.word):
                if letter == supposed_letter:
                    self.guessed = self.guessed[:i] + letter + self.guessed[i + 1:]

            self._send_guessed()
            if self.check_game_over():
                self.player.send_games()
                return

        else:
            self.status -= 1
            if self.check_game_over():
                self.player.send_games()
                return
            self._send_gallows()

        self.available_letters.remove(supposed_letter)
        self._send_keyboard()

    def check_game_over(self):
        if self.status == 0:
            self.player.send_text(self.player.translator["game_over_text"])
            self.player.game_over()
            return True

        if self.guessed.count("_") == 0:
            self.player.send_text(self.player.translator["you_won_text"])
            self.player.game_over()
            return True
