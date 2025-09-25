from datetime import timedelta
from sgp4.api import Satrec, WGS72, jday

def propagate_positions(tle_records, start_dt, minutes=120, step_min=2):
    ts = [start_dt + timedelta(minutes=m) for m in range(0, minutes+1, step_min)]
    out = []
    for name, l1, l2 in tle_records:
        # sgp4 >= 2.x: keyword arg yok; positional veya defaults kullan
        # sat = Satrec.twoline2rv(l1, l2)            # default (WGS72)
        sat = Satrec.twoline2rv(l1, l2, WGS72)       # explicit positional
        for t in ts:
            # jday: saniyeye mikro-saniyeyi ekliyoruz ki hassasiyet kaybolmasın
            jd, fr = jday(t.year, t.month, t.day,
                          t.hour, t.minute, t.second + t.microsecond*1e-6)
            e, r, v = sat.sgp4(jd, fr)
            if e == 0:
                out.append((name, t, r[0], r[1], r[2], v[0], v[1], v[2]))
    return out
