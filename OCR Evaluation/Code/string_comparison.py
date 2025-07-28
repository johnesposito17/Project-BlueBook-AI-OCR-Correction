import re
import Levenshtein  # pip install python-Levenshtein

def clean_string(s: str) -> str:
    # Remove all ǂ...ǂ blocks (including delimiters)
    s = re.sub(r'ǂ.*?ǂ', '', s)

    # Replace ʘ...ʘ with just the inner content
    s = re.sub(r'ʘ(.*?)ʘ', r'\1', s)

    # Remove line breaks
    s = re.sub(r'[\r\n]+', ' ', s)

    # Collapse multiple spaces and strip
    s = re.sub(r'\s+', ' ', s).strip()

    return s


def distance(reference:str, hypothesis: str):
    ref_clean = clean_string(reference)
    hyp_clean = clean_string(hypothesis)
    if len(ref_clean) == 0:
        if len(hyp_clean) > 0:
            # Either return 1.0 (max CER), or a custom flag
            return 1.0
        else:
            return 0.0
    return Levenshtein.distance(ref_clean, hyp_clean)
    

def character_error_rate(reference: str, hypothesis: str) -> float:
    ref_clean = clean_string(reference)
    hyp_clean = clean_string(hypothesis)

    distance = Levenshtein.distance(ref_clean, hyp_clean)
    return distance / max(len(ref_clean), len(hyp_clean))








