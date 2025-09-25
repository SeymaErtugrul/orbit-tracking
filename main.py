import json
from datetime import datetime, timedelta
# SGP4Calculator sınıfını diğer dosyadan import ediyoruz
from trackerAlgorithm import SGP4Calculator 

# --- TLE Katalog Tanımlaması (10 Uydu Örneği) ---
TLE_CATALOG = {
    "ISS (Uluslararası Uzay İstasyonu)": {
        "line1": "1 25544U 98067A   24001.00000000  .00000800  00000+0  15664-3 0  9990",
        "line2": "2 25544  51.6413 241.6053 0006767 214.3000 145.7000 15.49479402359402"
    },
    "HUBBLE Uzay Teleskobu": {
        "line1": "1 20580U 90037B   24001.50000000  .00000500  00000+0  10000-3 0  9990",
        "line2": "2 20580  28.4705 320.3000 0002700 300.0000 250.0000 14.97000000000000"
    },
    "GPS (NAVSTAR 75)": {
        "line1": "1 48259U 21060A   24001.00000000  .00000010  00000+0  10000-4 0  9990",
        "line2": "2 48259  55.0000 180.0000 0000000 180.0000 180.0000  3.87000000000000"
    },
    "Starlink (ÖRNEK)": {
        "line1": "1 44781U 19074A   24001.20000000  .00001000  00000+0  19000-3 0  9990",
        "line2": "2 44781  53.0000 300.0000 0001000 200.0000 160.0000 15.10000000000000"
    },
    "COSMOS 2251 (Çöp)": {
        "line1": "1 22824U 93049A   24001.10000000  .00000500  00000+0  10000-3 0  9990",
        "line2": "2 22824  74.0000 100.0000 0001000 200.0000 160.0000 14.50000000000000"
    },
    "Iridium 33 (Çöp)": {
        "line1": "1 24946U 97061A   24001.10000000  .00000800  00000+0  10000-3 0  9990",
        "line2": "2 24946  86.4000 250.0000 0001000 200.0000 160.0000 14.50000000000000"
    },
}


start_time = datetime.utcnow()
duration = 7200 # 2 saatlik (7200 saniye) yörünge
step = 60 # 60 saniyelik adımlar (performans için önerilir)

all_orbit_data = {}
FILE_NAME = 'all_orbit_data.json'

print("=========================================")
print(f"Toplam {len(TLE_CATALOG)} uydunun yörüngesi hesaplanıyor...")
print("=========================================")


for sat_name, tle in TLE_CATALOG.items():
    print(f"  -> Hesaplama: {sat_name}")
    
    try:
        calculator = SGP4Calculator(tle["line1"], tle["line2"])
        orbit_path = calculator.generate_orbit_data(start_time, duration, step_seconds=step)
        
        all_orbit_data[sat_name] = orbit_path
        
        print(f"     -> Başarılı. {len(orbit_path)} nokta kaydedildi.")

    except Exception as e:
        print(f"  HATA: {sat_name} hesaplanamadı. Hata: {e}")


# Veriyi JSON dosyasına kaydet
if all_orbit_data:
    try:
        with open(FILE_NAME, 'w') as f:
            json.dump(all_orbit_data, f, indent=4)
        print(f"\n✅ BAŞARILI: Tüm veriler '{FILE_NAME}' dosyasına kaydedildi.")
    except IOError as e:
        print(f"\n HATA: Dosya yazma hatası! Hata: {e}")
else:
    print("\n HATA: Hiçbir yörünge verisi hesaplanamadı.")