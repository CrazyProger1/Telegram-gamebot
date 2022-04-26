from json import load


class Translator:
    def __init__(self, language):
        self.language = language
        self.loaded_pack = None
        self.load_pack()

    def change_language(self, lang):
        self.language = lang
        self.load_pack()

    def load_pack(self):
        with open(f"language_packs/{self.language}.json", "r", encoding="utf-8") as lp:
            self.loaded_pack = load(lp)

    def __getitem__(self, word):
        return self.loaded_pack.get(word)
