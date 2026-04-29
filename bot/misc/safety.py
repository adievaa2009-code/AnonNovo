import os
import re
import unicodedata


CYRILLIC_TO_LATIN = str.maketrans({
    "а": "a",
    "е": "e",
    "ё": "e",
    "з": "z",
    "и": "i",
    "к": "k",
    "м": "m",
    "н": "h",
    "о": "o",
    "р": "p",
    "с": "c",
    "т": "t",
    "у": "y",
    "х": "x",
    "ь": "",
    "ъ": "",
})

LEETSPEAK = str.maketrans({
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "@": "a",
    "$": "s",
    "!": "i",
})


ENV_PATH = ".env"


def env_value(name: str) -> str:
    if os.getenv(name):
        return os.getenv(name, "")

    try:
        with open(ENV_PATH, encoding="utf-8") as env_file:
            for line in env_file:
                key, separator, value = line.strip().partition("=")
                if separator and key == name:
                    return value.strip().strip("'\"")
    except OSError:
        return ""

    return ""


def env_set(name: str) -> set[str]:
    return {value.strip() for value in env_value(name).split(",") if value.strip()}


STOP_WORDS = env_set("SAFETY_STOP_WORDS")
STOP_PHRASES = env_set("SAFETY_STOP_PHRASES")


STOP_PATTERNS = [
    re.compile(r"\b(?:f+[\W_]*u+[\W_]*c+[\W_]*k+)\b"),
    re.compile(r"\b(?:s+[\W_]*h+[\W_]*i+[\W_]*t+)\b"),
    re.compile(r"\b(?:b+[\W_]*i+[\W_]*t+[\W_]*c+[\W_]*h+)\b"),
    re.compile(r"\b(?:n+[\W_]*i+[\W_]*g+[\W_]*(?:g+|e+)[\W_]*r*)\b"),
    re.compile(r"\b(?:b+[\W_]*l+[\W_]*(?:y|i|j)+[\W_]*a+[\W_]*t*)\b"),
    re.compile(r"\b(?:h+|x+|kh+)[\W_]*(?:u+|y+)[\W_]*(?:i+|y+|j+)\b"),
    re.compile(r"\b(?:p+[\W_]*i+[\W_]*z+[\W_]*d+[\W_]*(?:a+|e+c+|e+t+s*))\b"),
    re.compile(r"\b(?:e+|y+e+|j+e+)[\W_]*b+[\W_]*(?:a+|u+|l+|n+)\w*\b"),
    re.compile(r"\b(?:c+[\W_]*y+[\W_]*k+[\W_]*a+|s+[\W_]*u+[\W_]*k+[\W_]*a+)\b"),
]


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    text = text.replace("ё", "е")
    text = text.translate(LEETSPEAK)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    return text


def latinized_text(text: str) -> str:
    return normalize_text(text).translate(CYRILLIC_TO_LATIN)


def extract_tokens(text: str) -> set[str]:
    normalized = normalize_text(text)
    return set(re.findall(r"[a-zа-яё0-9]+", normalized, re.IGNORECASE))


def contains_stop_word(text: str | None) -> bool:
    if not text:
        return False

    normalized = normalize_text(text)
    latinized = latinized_text(text)
    tokens = extract_tokens(text)

    if tokens & STOP_WORDS:
        return True

    for phrase in STOP_PHRASES:
        normalized_phrase = normalize_text(phrase)
        if normalized_phrase in normalized or normalized_phrase in latinized:
            return True

    for pattern in STOP_PATTERNS:
        if pattern.search(normalized) or pattern.search(latinized):
            return True

    return False
