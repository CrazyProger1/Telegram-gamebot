from config import *
from telebot import types, TeleBot
from json import loads, dumps
from games import *


class Player:
    def __init__(self, chat_id: int, bot: TeleBot, firstname: str):
        self.id = chat_id
        self.bot = bot
        self.firstname = firstname
        self.game: Game | None = None

    def set_game(self, game_name):
        if game_name == "Tic-Tac-Toe":
            self.game = TicTacToe(self)
        elif game_name == "Gallows":
            self.game = Gallows(self)

    def send_text(self, text) -> int:
        return self.bot.send_message(self.id, text).id

    def send_help(self) -> int:
        return self.send_text(HELP_TEXT.replace("@n", self.firstname))

    def send_inline_keyboard_markup(self, text, markup) -> int:
        return self.bot.send_message(self.id, text, reply_markup=markup).id

    def edit_message_reply_markup(self, message_id, reply_markup) -> int:
        return self.bot.edit_message_reply_markup(self.id, message_id, reply_markup=reply_markup).id

    def send_games(self):
        keyboard = types.InlineKeyboardMarkup()
        for game in GAMES_LIST:
            keyboard.add(types.InlineKeyboardButton(text=game,
                                                    callback_data=dumps({"type": "game selecting", "data": game})))
        return self.send_inline_keyboard_markup("Choose a game", keyboard)

    def start_game(self):
        self.game.start_game()

    def in_game(self):
        return self.game is not None

    def move(self, **kwargs):
        self.game.move(**kwargs)

    def game_over(self):
        self.game = None

    def edit_text(self, message_id, text):
        self.bot.edit_message_text(text, self.id, message_id)

    def send_photo(self, filepath, caption=None) -> int:

        with open(filepath, "rb") as img:
            return self.bot.send_photo(self.id, img, caption).id

    def edit_photo(self, message_id, filepath):
        with open(filepath, "rb") as img:
            self.bot.edit_message_media(types.InputMedia(type='photo', media=img),
                                        self.id,
                                        message_id)
