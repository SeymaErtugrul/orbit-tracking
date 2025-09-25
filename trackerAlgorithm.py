from datetime import datetime
def eci_to_geodetic(r, ts):
    """
    ECI (x, y, z) -> yükseklik (km), enlem (deg), boylam (deg)
    ts: datetime objesi (UTC)
    """
    import math
    x, y, z = r
    r_xy = math.sqrt(x**2 + y**2)
    # Dünya'nın dönüşü: Greenwich Sidereal Time (daha hassas)
    jd = (ts - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + 2451545.0
    T = (jd - 2451545.0) / 36525.0
    GMST = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T**2 - T**3 / 38710000.0
    GMST = math.radians(GMST % 360)
    lon = math.atan2(y, x) - GMST
    lon = (lon + math.pi) % (2 * math.pi) - math.pi
    lat = math.atan2(z, r_xy)
    # Yükseklik (Dünya merkezinden uzaklık - yarıçap)
    EARTH_RADIUS_KM = 6371.0
    height = math.sqrt(x**2 + y**2 + z**2) - EARTH_RADIUS_KM
    return height, math.degrees(lat), math.degrees(lon)

def get_satellite_state_now(line1, line2, ts=None):
    """
    TLE'den anlık yörünge, hız, yükseklik, enlem, boylam hesapla
    """
    from datetime import datetime
    import numpy as np
    from sgp4.api import Satrec, jday
    if ts is None:
        ts = datetime.utcnow()
    sat = Satrec.twoline2rv(line1, line2)
    jd, fr = jday(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second + ts.microsecond*1e-6)
    e, r, v = sat.sgp4(jd, fr)
    if e != 0:
        raise RuntimeError(f"SGP4 hesaplama hatası (Kod: {e}).")
    r = np.array(r)
    v = np.array(v)
    # SGP4'ten gelen hız vektörü km/s cinsindedir!
    speed_kmh = np.linalg.norm(v) * 3.6  # km/s -> km/h
    height, lat, lon = eci_to_geodetic(r, ts)
    return {
        "x": r[0],
        "y": r[1],
        "z": r[2],
        "speed_kmh": speed_kmh,
        "height_km": height,
        "lat": lat,
        "lon": lon
    }

# Örnek kullanım: TLE ile anlık değerleri yazdır
if __name__ == "__main__":
    # Hubble örnek TLE
    line1 = "1 20580U 90037B   25268.18402778  .00000200  00000-0  00000+0 0  9990"
    line2 = "2 20580  28.4692  10.1234 0002937  90.1234 270.1234 15.09123456    10"
    state = get_satellite_state_now(line1, line2)
    print("Konum (km):", state["x"], state["y"], state["z"])
    print("Hız (km/h):", state["speed_kmh"])
    print("Yükseklik (km):", state["height_km"])
    print("Enlem (deg):", state["lat"])
    print("Boylam (deg):", state["lon"])
import json
from datetime import datetime, timedelta
import numpy as np
from sgp4.api import Satrec, jday
import requests

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
        """
        Belirtilen süre boyunca yörünge verilerini hesaplar ve bir liste döndürür.
        HIZ (magnitude) ve KONUM verisini içerir.
        """
        orbit_data = []
        current_ts = start_ts
        end_ts = start_ts + timedelta(seconds=duration_seconds)
        
        while current_ts < end_ts:
            try:
                r, v = self.get_position_velocity(current_ts)
                # Konum vektörünün uzunluğu (Dünya merkezinden uzaklık)
                position_mag = np.linalg.norm(r)
                # Hız vektörünün uzunluğu (metre/saniye cinsinden SGP4 çıktısıdır, km/s için 1000'e bölelim)
                velocity_mag_km_s = np.linalg.norm(v) 
                
                orbit_data.append({
                    "time": current_ts.isoformat(),
                    "x": r[0],
                    "y": r[1],
                    "z": r[2],
                    "dist_km": position_mag,          # Dünya merkezinden uzaklık (km)
                    "vel_kms": velocity_mag_km_s       # Hız (km/s)
                })
            except RuntimeError:
                pass 

            current_ts += timedelta(seconds=step_seconds)
            
        return orbit_data

def download_tle_file(url="https://www.celestrak.com/NORAD/elements/active.txt", out_path="downloaded_satellites.tle"):
    """
    Verilen URL'den TLE dosyasını indirir ve belirtilen dosya yoluna kaydeder.
    """
    response = requests.get(url)
    response.raise_for_status()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    print(f"TLE dosyası indirildi: {out_path}")

def generate_all_satellites_orbit_data(tle_path, output_json, duration_hours=3, step_seconds=60):
    """
    Verilen TLE dosyasındaki tüm uydular için yörünge verisi üretir ve JSON dosyasına kaydeder.
    duration_hours: Kaç saatlik yörünge verisi üretilecek (her uydu için)
    step_seconds: Kaç saniyede bir örnek alınacak
    """
    all_data = {}
    with open(tle_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    i = 0
    now = datetime.utcnow()
    duration = duration_hours * 3600
    while i < len(lines) - 2:
        name = lines[i]
        line1 = lines[i+1]
        line2 = lines[i+2]
        try:
            sat = SGP4Calculator(line1, line2)
            orbit = generate_orbit_data(sat, now, duration, step_seconds)
            all_data[name] = orbit
        except Exception as e:
            print(f"{name} için hata: {e}")
        i += 3
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Toplam {len(all_data)} uydu için yörünge verisi kaydedildi: {output_json}")

# Örnek kullanım:
if __name__ == "__main__":
    # Hubble örnek TLE
    line1 = "1 20580U 90037B   25268.18402778  .00000200  00000-0  00000+0 0  9990"
    line2 = "2 20580  28.4692  10.1234 0002937  90.1234 270.1234 15.09123456    10"
    state = get_satellite_state_now(line1, line2)
    print("Konum (km):", state["x"], state["y"], state["z"])
    print("Hız (km/h):", state["speed_kmh"])
    print("Yükseklik (km):", state["height_km"])
    print("Enlem (deg):", state["lat"])
    print("Boylam (deg):", state["lon"])
