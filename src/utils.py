import json
import os

import regex as re
import tiktoken


def replace_markdown_links(text):
    pattern = re.compile(r"\[(!\[.*?\]\(.*?\))\]\(.*?\)")
    replaced_text = pattern.sub(r"\1", text)

    return replaced_text


def num_tokens_in_string(input_str: str, encoding_name: str = "o200k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(input_str))
    return num_tokens


def replace_multiple_newlines(text):
    cleaned_text = re.sub(r"\n{3,}", "\n\n", text)
    return cleaned_text


def replace_spaces_in_links(text):
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    def replacer(match):
        text_inside_brackets = match.group(1)
        link_inside_parentheses = match.group(2).replace(" ", "%20")
        return f"[{text_inside_brackets}]({link_inside_parentheses})"

    return pattern.sub(replacer, text)


def replace_chinese_parentheses(text):
    pattern = re.compile(r"\[([^\]]+)\]（([^）]+)）")

    def replacer(match):
        text_inside_brackets = match.group(1)
        link_inside_parentheses = match.group(2)
        return f"[{text_inside_brackets}]({link_inside_parentheses})"

    return pattern.sub(replacer, text)


def remove_hash_chars_lines(text):
    # 匹配包含一个或多个#的行
    pattern = r"^\s*#+\s*$"
    cleaned_text = re.sub(pattern, "", text, flags=re.MULTILINE)
    return cleaned_text


def remove_translation_tags(text: str) -> str:
    replacements = [
        ("<TRANSLATION>", ""),
        ("</TRANSLATION>", ""),
        ("</TRANSLATE_THIS>", ""),
        ("<TRANSLATE_THIS>", ""),
        ("<TRANSLATE_this>", ""),
        ("</TRANSLATE_this>", ""),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text.strip()


def calculate_chunk_size(token_count: int, token_limit: int) -> int:
    """
    Calculate the chunk size based on the token count and token limit.

    Args:
        token_count (int): The total number of tokens.
        token_limit (int): The maximum number of tokens allowed per chunk.

    Returns:
        int: The calculated chunk size.

    Description:
        This function calculates the chunk size based on the given token count and token limit.
        If the token count is less than or equal to the token limit, the function returns the token count as the chunk size.
        Otherwise, it calculates the number of chunks needed to accommodate all the tokens within the token limit.
        The chunk size is determined by dividing the token limit by the number of chunks.
        If there are remaining tokens after dividing the token count by the token limit,
        the chunk size is adjusted by adding the remaining tokens divided by the number of chunks.

    Example:
        >>> calculate_chunk_size(1000, 500)
        500
        >>> calculate_chunk_size(1530, 500)
        389
        >>> calculate_chunk_size(2242, 500)
        496
    """

    if token_count <= token_limit:
        return token_count

    num_chunks = (token_count + token_limit - 1) // token_limit
    chunk_size = token_count // num_chunks

    remaining_tokens = token_count % token_limit
    if remaining_tokens > 0:
        chunk_size += remaining_tokens // num_chunks

    return chunk_size


def load_cache(filename):
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as f:
            cache_data: dict = json.load(f)
        return cache_data.get("done_idx", -1)
