import re
from typing import Tuple, Dict

PH = "{PH_%s_%d}"

PATTERNS = [
    ("DATE", re.compile(r"\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b")),
    ("PERCENT", re.compile(r"\b\d+(?:[.,]\d+)?\s?%")),
    ("MONEY", re.compile(r"\b\d+(?:[ \u00A0]?\d{3})*(?:[.,]\d+)?\s?(?:₸|KZT|₽|RUB|USD|EUR)\b")),
    ("UNIT", re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:кг|г|м|км|мм|см|л|мл)\b", re.I)),
    ("NUM", re.compile(r"\b\d+(?:[.,]\d+)?\b")),
    ("URL", re.compile(r"https?://\S+")),
    ("EMAIL", re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")),
]

def protect(text: str) -> Tuple[str, Dict[str,str]]:
    mapping = {}
    idx = 0
    s = text
    for name, pat in PATTERNS:
        def repl(m):
            nonlocal idx
            key = PH % (name, idx); idx += 1
            mapping[key] = m.group(0)
            return key
        s = pat.sub(repl, s)
    return s, mapping

def restore(text: str, mapping: Dict[str,str]) -> str:
    for k in sorted(mapping.keys(), key=len, reverse=True):
        text = text.replace(k, mapping[k])
    return text
