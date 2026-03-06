import json
import re
from difflib import SequenceMatcher

def norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9\s\-\+]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def fuzzy(a, b):
    return SequenceMatcher(None, a, b).ratio()

def map_test_id(test_raw: str, tests_master_rows):
    """
    tests_master_rows: list of (id, canonical_name, synonyms_json)
    """
    tr = norm(test_raw)
    best = (None, 0.0)
    for tid, cname, syn_json in tests_master_rows:
        candidates = [cname] + json.loads(syn_json or "[]")
        for c in candidates:
            score = fuzzy(tr, norm(c))
            if score > best[1]:
                best = (tid, score)

    # conservative threshold
    if best[1] >= 0.86:
        return best[0], best[1]
    return None, best[1]