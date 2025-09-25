import numpy as np

RE_KM = 6378.137  # Dünya yarıçapı (km)

def _dist(p, q):
    p = np.array(p, float)
    q = np.array(q, float)
    return float(np.linalg.norm(p - q))

def screen_conjunctions(state_list, threshold_km=10.0, altitude_band_km=80.0):
    """
    Aynı zaman damgasındaki cisimler arasında yakın yaklaşım taraması.
    state_list: [(name, t, x, y, z, vx, vy, vz), ...]
    """
    # 1) Zamanlara göre grupla
    by_t = {}
    for name, t, x, y, z, vx, vy, vz in state_list:
        by_t.setdefault(t, []).append(
            (name, np.array([x, y, z], float), np.array([vx, vy, vz], float))
        )

    alerts = []

    # 2) Her zaman diliminde çiftleri tara
    for t, recs in by_t.items():
        # Her kayıt için yükseklikleri önceden hesapla
        expanded = []
        for name, r, v in recs:
            alt = float(np.linalg.norm(r) - RE_KM)
            expanded.append((name, r, v, alt))

        # Aynı timestamp içinde A–B ve B–A'yı tekilleştirmek için
        seen_pairs = set()

        n = len(expanded)
        for i in range(n):
            for j in range(i + 1, n):
                n1, r1, v1, a1 = expanded[i]
                n2, r2, v2, a2 = expanded[j]

                # Aynı isimli nesneleri atla
                if n1 == n2:
                    continue

                # Yükseklik bandı filtresi (kaba eleme)
                if abs(a1 - a2) > altitude_band_km:
                    continue

                # Mesafe ve bağıl hız
                d = _dist(r1, r2)
                if d < threshold_km:
                    rel_v = float(np.linalg.norm(v1 - v2))

                    # A–B / B–A tekrarını engelle
                    pair = tuple(sorted((n1, n2)))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)

                    alerts.append({
                        "time": t.isoformat(),
                        "obj_a": n1,
                        "obj_b": n2,
                        "miss_distance_km": round(d, 3),
                        "rel_speed_kms": round(rel_v, 3),
                        "altitude_km": round((a1 + a2) / 2, 1),
                    })

    # 3) En yakından uzağa sırala ve liste döndür
    return sorted(alerts, key=lambda x: x["miss_distance_km"])
