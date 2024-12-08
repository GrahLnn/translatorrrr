import os
from translatorrr import Translator

translator = Translator()

for file in os.listdir("input"):
    translator.translate_file(os.path.join("input", file))
