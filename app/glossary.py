import csv, re
from typing import List, Tuple

class Glossary:
    def __init__(self, csv_path: str | None):
        self.rules: List[Tuple[re.Pattern, str]] = []
        if not csv_path: return
        with open(csv_path, encoding="utf-8") as f:
            for row in csv.reader(f):
                if not row or row[0].startswith("#"): continue
                src, tgt, *rest = row
                flags = re.IGNORECASE
                pat = re.compile(rf"(?<!\w){re.escape(src)}(?!\w)", flags)
                self.rules.append((pat, tgt))
    def apply(self, s: str) -> str:
        for pat, tgt in self.rules:
            s = pat.sub(tgt, s)
        return s
