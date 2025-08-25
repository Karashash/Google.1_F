from typing import List, Tuple
def _score_comet(src: str, hyps: List[str]) -> List[float]:
    try:
        from comet import load_from_checkpoint
        model = load_from_checkpoint("Unbabel/wmt22-comet-da")
        data = [{"src": src, "mt": h} for h in hyps]
        scores, _ = model.predict(data, batch_size=8, gpus=0)
        return [float(s) for s in scores]
    except Exception:
        return [0.0]*len(hyps)

def _score_heuristic(src: str, hyp: str) -> float:
    import re
    def nums(s): return sorted(re.findall(r"\d+(?:[.,]\d+)?", s))
    score = 0.0
    score += 1.0 if nums(src)==nums(hyp) else 0.0
    lr = len(hyp)+1e-6 / (len(src)+1e-6)
    score += max(0.0, 1.0 - abs(lr-1.0))
    for a,b in [("(",")"),("[","]"),("«","»")]:
        score += 0.5 if hyp.count(a)==hyp.count(b) else 0.0
    return score

def choose_best(src: str, hyps: List[str]) -> Tuple[str, float]:
    if not hyps: return "", 0.0
    comet = _score_comet(src, hyps)
    if any(comet):
        i = max(range(len(hyps)), key=lambda k: comet[k])
        return hyps[i], comet[i]
    best_i, best_s = 0, -1e9
    for i,h in enumerate(hyps):
        s = _score_heuristic(src, h)
        if s>best_s: best_s, best_i = s, i
    return hyps[best_i], best_s
