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

    def send_text(self, text):
        self.bot.send_message(self.id, text)

    def send_help(self):
        self.send_text(HELP_TEXT.replace("@n", self.firstname))

    def send_games(self):
        keyboard = types.InlineKeyboardMarkup()
        for game in GAMES_LIST:
            keyboard.add(types.InlineKeyboardButton(text=game,
                                                    callback_data=dumps({"type": "game selecting", "data": game})))

        self.bot.send_message(self.id, "Choose a game", reply_markup=keyboard)

    def start_game(self):
        pass
