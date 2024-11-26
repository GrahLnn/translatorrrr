BASIC_TRANSLATION_PROMPT = """Your task is to provide a professional translation from {source_lang} to {target_lang} of PART of a text.

To reiterate, you should translate only this part and ALL from this of the text, shown here between <TRANSLATE_THIS> and </TRANSLATE_THIS>:
<TRANSLATE_THIS>
{chunk_to_translate}
</TRANSLATE_THIS>

Guidelines for translate:
1. Translate ALL content between <TRANSLATE_THIS> and </TRANSLATE_THIS> part.
2. Maintain paragraph structure and line breaks.
3. Preserve all markdown, image links, LaTeX code, and titles.
4. Do not remove any single line from the <TRANSLATE_THIS> and </TRANSLATE_THIS> part.
5. Even if it is a single title or a title containing incomplete paragraphs, it still needs to be translated.

Output only the translation of the portion you are asked to translate, and nothing else.
"""

REFLECTION_TRANSLATION_PROMPT = """Your task is to carefully read a source text and part of a translation of that text from {source_lang} to {target_lang}, and then give constructive criticism and helpful suggestions for improving the translation.
    The final style and tone of the translation should match the style of {target_lang} colloquially spoken in {country}.

    The source text is below, delimited by XML tags <SOURCE_TEXT> and </SOURCE_TEXT>, and the part that has been translated
    is delimited by <TRANSLATE_THIS> and </TRANSLATE_THIS> within the source text. You can use the rest of the source text as context for critiquing the translated part. Retain all markdown image links, Latex code and multi-level title in their positions and relationships within the text.

    <SOURCE_TEXT>
    {tagged_text}
    </SOURCE_TEXT>

    To reiterate, only part of the text is being translated, shown here again between <TRANSLATE_THIS> and </TRANSLATE_THIS>:
    <TRANSLATE_THIS>
    {chunk_to_translate}
    </TRANSLATE_THIS>

    The translation of the indicated part, delimited below by <TRANSLATION> and </TRANSLATION>, is as follows:
    <TRANSLATION>
    {translation_1_chunk}
    </TRANSLATION>

    When writing suggestions, pay attention to whether there are ways to improve the translation's:\n\
    (i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text, and the content needs to be consistent.),\n\
    (ii) fluency (by applying {target_lang} grammar, spelling and punctuation rules, and ensuring there are no unnecessary repetitions),\n\
    (iii) style (by ensuring the translations reflect the style of the source text and takes into account any cultural context),\n\
    (iv) terminology (by ensuring terminology use is consistent and reflects the source text domain; and by only ensuring you use equivalent idioms {target_lang}).\n\

    Write a list of specific, helpful and constructive suggestions for improving the translation.
    Each suggestion should address one specific part of the translation.
    Output only the suggestions and nothing else."""

IMPROVE_TRANSLATION_PROMPT = """Your task is to carefully read, then improve, a translation from {source_lang} to {target_lang}, taking into
    account a set of expert suggestions and constructive criticisms. Below, the source text, initial translation, and expert suggestions are provided.

    The source text is below, delimited by XML tags <SOURCE_TEXT> and </SOURCE_TEXT>, and the part that has been translated
    is delimited by <TRANSLATE_THIS> and </TRANSLATE_THIS> within the source text. You can use the rest of the source text
    as context, but need to provide a translation only of the part indicated by <TRANSLATE_THIS> and </TRANSLATE_THIS>.

    <SOURCE_TEXT>
    {tagged_text}
    </SOURCE_TEXT>

    To reiterate, only part of the text is being translated, shown here again between <TRANSLATE_THIS> and </TRANSLATE_THIS>:
    <TRANSLATE_THIS>
    {chunk_to_translate}
    </TRANSLATE_THIS>

    The translation of the indicated part, delimited below by <TRANSLATION> and </TRANSLATION>, is as follows:
    <TRANSLATION>
    {translation_1_chunk}
    </TRANSLATION>

    The expert translations of the indicated part, delimited below by <EXPERT_SUGGESTIONS> and </EXPERT_SUGGESTIONS>, are as follows:
    <EXPERT_SUGGESTIONS>
    {reflection_chunk}
    </EXPERT_SUGGESTIONS>

    Taking into account the expert suggestions rewrite the translation to improve it, paying attention
    to whether there are ways to improve the translation's

    1. accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),
    2. fluency (by applying {target_lang} grammar, spelling and punctuation rules and ensuring there are no unnecessary repetitions), \
    3. style (by ensuring the translations reflect the style of the source text)
    4. terminology (inappropriate for context, inconsistent use)
    5. Do not remove any single line from the <TRANSLATE_THIS> and </TRANSLATE_THIS> part, even it just a single img link.
    6. do not translate the part outside of the <TRANSLATE_THIS> and <TRANSLATION> tags from <SOURCE_TEXT>.
    7. even if it is a single title or a title containing incomplete paragraphs, it still needs to be translated.
    8. Preserve all markdown, image links, LaTeX code, paragraph structure, and titles.
    9. No need to include pinyin annotations.

    Output only the new translation of the indicated part and nothing else."""
