import numpy as np
RE_KM = 6378.137  # Dünya yarıçapı (km)

def _dist(p, q):
    p = np.array(p, float); q = np.array(q, float)
    return float(np.linalg.norm(p - q))
def screen_conjunctions(state_list, threshold_km=10.0, altitude_band_km=80.0):
    """
    Aynı zaman damgasındaki cisimler arasında yakın yaklaşım taraması.
    state_list: [(name, t, x,y,z, vx,vy,vz), ...]
    """
    # Zamanlara göre grupla
    by_t = {}
    for name, t, x, y, z, vx, vy, vz in state_list:
        r = np.array([x, y, z], float)
        v = np.array([vx, vy, vz], float)
        by_t.setdefault(t, []).append((name, r, v))

    alerts = []
    for t, recs in by_t.items():
        # Yükseklikleri önceden hesapla
        expanded = []
        for name, r, v in recs:
            alt = float(np.linalg.norm(r) - RE_KM)
            expanded.append((name, r, v, alt))

        # Çiftler arası karşılaştır
        n = len(expanded)
        for i in range(n):
            for j in range(i + 1, n):
                n1, r1, v1, a1 = expanded[i]
                n2, r2, v2, a2 = expanded[j]

                # aynı isimli nesneleri atla
                if n1 == n2:
                    continue

                # yükseklik bandı filtresi
                if abs(a1 - a2) > altitude_band_km:
                    continue

