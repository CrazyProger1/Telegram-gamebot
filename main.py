from telebot import types, TeleBot
from config import *
from json import loads, dumps
from player import Player


class App:
    def __init__(self):
        self.bot = TeleBot(TOKEN)
        self.players = {}

    def add_player(self, user: types.User):
        player: Player = self.players.get(user.id)

        if player is None:
            self.players.update({user.id: Player(user.id, self.bot, user.first_name)})
            player = self.players.get(user.id)

        return player

    def handle_command(self, command: types.Message):
        player = self.add_player(command.from_user)

        if command.text in ["/start", "/help"]:
            player.send_help()
        elif command.text == "/games":
            player.send_games()

    def callback_handler(self, call: types.CallbackQuery):
        data: dict = loads(call.data)

        player = self.add_player(call.from_user)

        if data.get("type") == "game selecting":
            player.set_game(data.get("data"))
            player.start_game()

        if player.in_game() and data.get("type") == "in game":
            player.move(data=data.get("data"))

    def run(self):
        self.bot.message_handler(commands=["start", "help", "games"])(self.handle_command)
        self.bot.callback_query_handler(func=lambda call: True)(self.callback_handler)
        self.bot.polling(True)


if __name__ == '__main__':
    app = App()
    app.run()
