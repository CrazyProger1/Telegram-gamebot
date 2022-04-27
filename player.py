from config import *
from telebot import types, TeleBot
from json import loads, dumps
from games import *
import os
from translator import Translator


class Player:
    def __init__(self, chat_id: int, bot: TeleBot, firstname: str):
        self.firstname = firstname
        self._id = chat_id
        self._bot = bot
        self._game: Game | None = None
        self.translator = Translator("English")

    def set_game(self, game_name):
        if game_name == "Tic-Tac-Toe":
            self._game = TicTacToe(self)
        elif game_name == "Gallows":
            self._game = Gallows(self)

    def set_language(self, language):
        self.translator.change_language(language)

    def send_text(self, text) -> int:
        return self._bot.send_message(self._id, text).id

    def send_help(self) -> int:
        return self.send_text(self.translator["help_text"].replace("@n", self.firstname))

    def send_inline_keyboard_markup(self, text, markup) -> int:
        return self._bot.send_message(self._id, text, reply_markup=markup).id

    def edit_message_reply_markup(self, message_id, reply_markup) -> int:
        return self._bot.edit_message_reply_markup(self._id, message_id, reply_markup=reply_markup).id

    def send_games(self):
        keyboard = types.InlineKeyboardMarkup()
        for game in GAMES_LIST:
            keyboard.add(types.InlineKeyboardButton(text=game,
                                                    callback_data=dumps({"type": "game selecting", "data": game})))
        return self.send_inline_keyboard_markup(self.translator["game_choosing_text"], keyboard)

    def send_photo(self, filepath, caption=None) -> int:

        with open(filepath, "rb") as img:
            return self._bot.send_photo(self._id, img, caption).id

    def edit_text(self, message_id, text):
        self._bot.edit_message_text(text, self._id, message_id)

    def edit_photo(self, message_id, filepath):
        with open(filepath, "rb") as img:
            self._bot.edit_message_media(types.InputMedia(type='photo', media=img),
                                         self._id,
                                         message_id)

    def start_game(self):
        self._game.start_game()

    def send_language_selection(self):
        keyboard = types.InlineKeyboardMarkup()
        for lang_file in os.listdir("language_packs"):
            lang = os.path.splitext(lang_file)[0]
            keyboard.add(types.InlineKeyboardButton(text=lang,
                                                    callback_data=dumps(
                                                        {"type": "language selecting", "data": lang})))
        return self.send_inline_keyboard_markup(self.translator["lang_choosing_text"], keyboard)

    def in_game(self):
        return self._game is not None

    def move(self, **kwargs):
        self._game.move(**kwargs)

    def game_over(self):
        self._game = None
