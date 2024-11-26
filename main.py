import os
from src.translator import Translator

translator = Translator()

for file in os.listdir("input"):
    translator.translate_file(os.path.join("input", file))
