from json import load


class Translator:
    def __init__(self, language):
        self._language = language
        self._loaded_pack = None
        self._load_pack()

    def _load_pack(self):
        with open(f"language_packs/{self._language}.json", "r", encoding="utf-8") as lp:
            self._loaded_pack = load(lp)

    def change_language(self, lang):
        self._language = lang
        self._load_pack()

    def __getitem__(self, word):
        return self._loaded_pack.get(word)

    def get_translation(self, word):
        return self._loaded_pack.get(word)
