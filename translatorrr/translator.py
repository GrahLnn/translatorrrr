import json
import os
import re
import shutil
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from icecream import ic
from langchain_text_splitters import RecursiveCharacterTextSplitter as rcs
from pydantic_settings import BaseSettings
from tqdm import tqdm

from .llm import LLM
from .prompt import (
    BASIC_TRANSLATION_PROMPT,
    IMPROVE_TRANSLATION_PROMPT,
    REFLECTION_TRANSLATION_PROMPT,
)
from .utils import (
    calculate_chunk_size,
    num_tokens_in_string,
    remove_hash_chars_lines,
    replace_chinese_parentheses,
    replace_markdown_links,
    replace_multiple_newlines,
    replace_spaces_in_links,
)


class TranslatorSettings(BaseSettings):
    output_folder: str = "output"
    source_lang: str = "English"
    target_lang: str = "Chinese"
    country: str = "China"
    # save_as_log: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


class TranslationCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, name):
        return os.path.join(self.cache_dir, f"{name}.json")

    def load(self, name) -> Tuple[int, List[str]]:
        cache_file = self._get_cache_path(name)
        if os.path.exists(cache_file):
            with open(cache_file, encoding="utf-8") as f:
                data: Dict = json.load(f)
            return data.get("done_idx", -1), data.get("results", [])
        return -1, []

    def save(self, name, data):
        cache_file = self._get_cache_path(name)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def delete(self):
        shutil.rmtree(self.cache_dir)


@dataclass
class Translator:
    settings: TranslatorSettings = field(default_factory=TranslatorSettings)
    llm: LLM = field(default_factory=LLM)
    cacher: TranslationCache = field(default_factory=TranslationCache)

    def __post_init__(self):
        os.makedirs(self.settings.output_folder, exist_ok=True)

    def translate_file(self, path: str) -> str:
        # Read source text
        with open(path, encoding="utf-8") as file:
            source_text = file.read()

        # Call translation logic
        translation = self.translate(source_text)

        # Check if first line is a level-1 heading
        first_line = translation.split('\n')[0]
        filename = os.path.splitext(os.path.basename(path))[0]
        if first_line.strip().startswith('# '):
            heading = first_line[2:].strip()
            if heading:  # ensure heading is not empty
                filename = re.sub(r'[<>:"/\\|?*]', '', heading)

        # Set translation output path
        translation_output_path = os.path.join(
            self.settings.output_folder,
            f"{filename}.md",
        )

        # Write translation result
        with open(translation_output_path, "w", encoding="utf-8") as output_file:
            output_file.write(translation)

        # Remove source text
        os.remove(path)
        self.cacher.delete()
        return translation_output_path.strip()

    def translate(self, source_text: str) -> str:
        source_text = replace_markdown_links(source_text)
        num_tokens_in_text = num_tokens_in_string(source_text)

        ic(num_tokens_in_text)

        # if self.settings.save_log:
        #     save_cache(f"saved_cache/{textname}/{MODEL}/", source_text, "source_text")
        token_size = calculate_chunk_size(
            token_count=num_tokens_in_text, token_limit=1000
        )
        ic(token_size)

        text_splitter = rcs.from_tiktoken_encoder(
            model_name="gpt-4o",
            chunk_size=token_size,
            chunk_overlap=0,
        )

        chunks = text_splitter.split_text(source_text)
        final_chunks = self._chunk_translation(chunks)

        cleaned_text = remove_hash_chars_lines("".join(final_chunks))
        cleaned_text = replace_chinese_parentheses(cleaned_text)
        cleaned_text = replace_spaces_in_links(cleaned_text)
        final_translation = replace_multiple_newlines(cleaned_text)

        return final_translation

    def _chunk_translation(self, chunks):
        basic_trans = self._basic_translate(chunks)

        reflect_guide = self._reflect_translate(
            chunks,
            basic_trans,
        )

        final_trans = self._improve_translation(
            chunks,
            basic_trans,
            reflect_guide,
        )

        return final_trans

    def _basic_translate(self, chunks: List[str]) -> List[str]:
        done_idx, result_chunks = self.cacher.load("init_translation")

        if done_idx == len(chunks) - 1:
            return result_chunks

        for i in tqdm(range(done_idx + 1, len(chunks)), desc="1: basic translating"):
            prompt = BASIC_TRANSLATION_PROMPT.format(
                source_lang=self.settings.source_lang,
                target_lang=self.settings.target_lang,
                chunk_to_translate=chunks[i],
            )

            translation = self.llm.do(prompt)
            result_chunks.append(translation)

            self.cacher.save(
                "init_translation",
                {
                    "done_idx": i,
                    "results": result_chunks,
                },
            )

        return result_chunks

    def _reflect_translate(
        self,
        source_chunks: List[str],
        basic_trans: List[str],
    ) -> List[str]:
        done_idx, result_chunks = self.cacher.load("reflection_chunks")

        if done_idx == len(source_chunks) - 1:
            return result_chunks

        for i in tqdm(
            range(done_idx + 1, len(source_chunks)),
            desc="2: reflect guiding",
        ):
            tagged_text = (
                ("".join(source_chunks[max(i - 2, 0) : i]) if i > 0 else "")
                + "<TRANSLATE_THIS>"
                + source_chunks[i]
                + "</TRANSLATE_THIS>"
                + (
                    "".join(source_chunks[i + 1 : min(i + 2, len(source_chunks))])
                    if i < len(source_chunks) - 1
                    else ""
                )
            )
            prompt = REFLECTION_TRANSLATION_PROMPT.format(
                source_lang=self.settings.source_lang,
                target_lang=self.settings.target_lang,
                country=self.settings.country,
                tagged_text=tagged_text,
                chunk_to_translate=source_chunks[i],
                translation_1_chunk=basic_trans[i],
            )

            reflection = self.llm.do(prompt)
            result_chunks.append(reflection)

            self.cacher.save(
                "reflection_chunks",
                {
                    "done_idx": i,
                    "results": result_chunks,
                },
            )

        return result_chunks

    def _improve_translation(
        self,
        source_chunks: List[str],
        basic_trans: List[str],
        reflect_guide: List[str],
    ) -> List[str]:
        done_idx, result_chunks = self.cacher.load("improve_chunks")

        if done_idx == len(source_chunks) - 1:
            return result_chunks

        for i in tqdm(
            range(done_idx + 1, len(source_chunks)),
            desc="3: improve translating",
        ):
            tagged_text = (
                ("".join(source_chunks[max(i - 2, 0) : i]) if i > 0 else "")
                + "<TRANSLATE_THIS>"
                + source_chunks[i]
                + "</TRANSLATE_THIS>"
                + (
                    "".join(source_chunks[i + 1 : min(i + 2, len(source_chunks))])
                    if i < len(source_chunks) - 1
                    else ""
                )
            )

            prompt = IMPROVE_TRANSLATION_PROMPT.format(
                source_lang=self.settings.source_lang,
                target_lang=self.settings.target_lang,
                tagged_text=tagged_text,
                chunk_to_translate=source_chunks[i],
                translation_1_chunk=basic_trans[i],
                reflection_chunk=reflect_guide[i],
            )

            translation_2 = self.llm.do(prompt)

            result_chunks.append("\n\n" + translation_2)

            self.cacher.save(
                "improve_chunks",
                {
                    "done_idx": i,
                    "results": result_chunks,
                },
            )

        return result_chunks
