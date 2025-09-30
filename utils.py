import re

def to_int(txt: str | None):
    if not txt:
        return None

    m = re.search(r"\d+", txt)

    if m:
        return int(m.group())
    else:
        return None


def to_float(txt: str | None):
    if not txt:
        return None
    
    m = re.search(r"(\d+(?:[.,]\d+)?)", txt)

    if m:
        return float(m.group(1).replace(",", "."))
    else:
        return None