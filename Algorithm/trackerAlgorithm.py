import json
from datetime import datetime, timedelta
import numpy as np
from sgp4.api import Satrec, jday

class SGP4Calculator:
    def __init__(self, line1, line2):
        """TLE satırlarını alarak Satrec nesnesini başlatır."""
        self.satellite = Satrec.twoline2rv(line1, line2)

    def get_position_velocity(self, ts=None):
        """Verilen zaman damgası için ECI (x, y, z) konumunu ve hızı hesaplar."""
        if ts is None:
            ts = datetime.utcnow()
        
        # Julian gün ve günün kesri hesaplama
        jd, fr = jday(ts.year, ts.month, ts.day,
                      ts.hour, ts.minute, ts.second + ts.microsecond*1e-6)
        
        e, r, v = self.satellite.sgp4(jd, fr)
        
        if e != 0:
            raise RuntimeError(f"SGP4 hesaplama hatası (Kod: {e}).")
            
        return np.array(r), np.array(v)

    def generate_orbit_data(self, start_ts, duration_seconds, step_seconds=60):
        """Belirtilen süre boyunca yörünge noktalarını üretir."""
        orbit_data = []
        current_ts = start_ts
        end_ts = start_ts + timedelta(seconds=duration_seconds)
        
        while current_ts < end_ts:
            try:
                r, _ = self.get_position_velocity(current_ts)
                orbit_data.append({
                    "time": current_ts.isoformat(),
                    "x": r[0],
                    "y": r[1],
                    "z": r[2]
                })
            except RuntimeError:
                pass 

            current_ts += timedelta(seconds=step_seconds)
            
        return orbit_data
