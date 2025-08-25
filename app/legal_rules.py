import re

DEONTIC_MAP = [
    (re.compile(r"\bприказываю\b", re.I), "бұйырамын"),
    (re.compile(r"\bпостановляю\b", re.I), "қаулы етемін"),
    (re.compile(r"\bутвердить\b", re.I), "бекіту"),
    (re.compile(r"\bобязать\b", re.I), "міндеттеу"),
    (re.compile(r"\bзапрещается\b", re.I), "тыйым салынады"),
    (re.compile(r"\bразрешается\b", re.I), "рұқсат етіледі"),
    (re.compile(r"\bвступает в силу\b", re.I), "күшіне енеді"),
]

ORG_MAP = [
    (re.compile(r"\bАО\b", re.I), "АҚ"),
    (re.compile(r"\bООО\b", re.I), "ЖШС"),
    (re.compile(r"\bТОО\b", re.I), "ЖШС"),
    (re.compile(r"\bРеспублика Казахстан\b", re.I), "Қазақстан Республикасы"),
]

def enforce_intent(s: str) -> str:
    t = s
    for pat, tgt in DEONTIC_MAP:
        t = pat.sub(tgt, t)
    for pat, tgt in ORG_MAP:
        t = pat.sub(tgt, t)
    return t

def intent_flags(src: str, tgt: str) -> dict:
    flags = {}
    for pat, kk in DEONTIC_MAP:
        ru_hit = bool(pat.search(src))
        kk_hit = kk.lower() in tgt.lower()
        if ru_hit and not kk_hit:
            flags[f"missing_{kk}"] = True
    return flags
