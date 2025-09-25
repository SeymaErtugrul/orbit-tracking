import re

# Görünmeyen boşlukları normalleştir
_WS = ("\ufeff", "\u00a0", "\u2007", "\u202f")

def _norm(s: str) -> str:
    if not s:
        return ""
    for ch in _WS:
        s = s.replace(ch, " ")
    # tüm whitespace'leri soldan/bastan temizle (tab vs. dahil)
    return s.lstrip()

RE_L1 = re.compile(r"^\s*1\s")
RE_L2 = re.compile(r"^\s*2\s")

def _is_l1(s: str) -> bool:
    return bool(RE_L1.match(s))

def _is_l2(s: str) -> bool:
    return bool(RE_L2.match(s))

def _name_from_l1(l1: str) -> str:
    s = l1.lstrip()
    sat = (s[2:7].strip() if len(s) >= 7 else "")
    return f"SAT-{sat or 'UNKNOWN'}"

def _read_text_with_auto_encoding(path: str) -> str:
    """
    Dosyayı binary açar, BOM'a bakarak/deneyerek doğru şekilde decode eder.
    UTF-16/UTF-8-BOM/NUL içeren vakaları temizler.
    """
    with open(path, "rb") as f:
        data = f.read()

    if not data:
        return ""

    # UTF-16 BOM kontrolü
    if data.startswith(b"\xff\xfe"):  # UTF-16 LE
        txt = data.decode("utf-16-le", "replace")
    elif data.startswith(b"\xfe\xff"):  # UTF-16 BE
        txt = data.decode("utf-16-be", "replace")
    elif data.startswith(b"\xef\xbb\xbf"):  # UTF-8 BOM
        txt = data.decode("utf-8-sig", "replace")
    else:
        # NUL bayt varsa (UTF-16 gibi), önce sıfırları sök
        if b"\x00" in data:
            data = data.replace(b"\x00", b"")
        # önce utf-8 dene, sonra latin-1'e düş
        try:
            txt = data.decode("utf-8", "replace")
        except Exception:
            txt = data.decode("latin-1", "replace")

    return txt

def load_tles(filenames):
    recs = []
    seen = set()

    for fname in filenames:
        try:
            raw = _read_text_with_auto_encoding(fname)
        except FileNotFoundError:
            print(f"[WARN] yok: {fname}")
            continue

        # satırlara böl + normalize
        lines = [_norm(ln.rstrip("\r\n")) for ln in raw.splitlines()]
        n = len(lines)
        i = 0
        found = 0

        while i < n:
            s = lines[i]

            low = s.lower()
            if "<html" in low or "file not found" in low:
                i += 1
                continue

            # 2-satır blok: L1 + L2
            if _is_l1(s) and (i + 1 < n) and _is_l2(lines[i + 1]):
                l1 = s
                l2 = lines[i + 1]
                # İsim: varsa bir üst satır L1/L2 değilse onu al
                name = None
                if i - 1 >= 0:
                    prev = lines[i - 1].strip()
                    if prev and (not _is_l1(prev)) and (not _is_l2(prev)):
                        name = prev
                if not name:
                    name = _name_from_l1(l1)
                i += 2

            # 3-satır blok: Name + L1 + L2
            elif (i + 2 < n) and _is_l1(lines[i + 1]) and _is_l2(lines[i + 2]):
                name = lines[i].strip() or "UNKNOWN"
                l1 = lines[i + 1]
                l2 = lines[i + 2]
                i += 3

            else:
                i += 1
                continue

            key = (l1, l2)
            if key in seen:
                continue
            seen.add(key)
            recs.append((name, l1, l2))
            found += 1

        print(f"[INFO] {fname}: {found} TLE")

    print(f"[INFO] TOPLAM TLE: {len(recs)}")
    return recs
