from datetime import datetime, timezone
import pandas as pd

from tle_loader import load_tles
from propagate import propagate_positions

# screen_conjunctions bazı sürümlerde screen2.py’de, bazılarında screen.py’de olabilir
try:
    from screen2 import screen_conjunctions
except ImportError:
    from screen import screen_conjunctions

# risk score modülü olmayabilir; yoksa fallback
try:
    from scoring import add_risk_scores
except ImportError:
    def add_risk_scores(df):
        df["risk_score"] = 0
        return df


def main():
    print(">>> START Space Debris Guard run")

    # 1) TLE’leri yükle
    tle_files = ["data/iss.txt", "data/starlink.txt", "data/debris.txt"]
    tle_records = load_tles(tle_files)

    # 2) Başlangıç zamanı (UTC)
    start = datetime.now(timezone.utc)

    # 3) Yörünge yayılımı — özellikle geniş (96 saat, 3 dk adım)
    print(">>> Propagate başlıyor (5760 dk, step=3)...")
    states = propagate_positions(
        tle_records,
        start_dt=start,
        minutes=2880,   # 96 saat
        step_min=3
    )

    print(f"TLE sayısı: {len(tle_records)}")
    print(f"State sayısı: {len(states)}")

    # 4) Yakın yaklaşım taraması — özellikle gevşek eşikler (çıkış garantisi için)
    print(">>> Screening başlıyor (threshold=80 km, band=800 km)...")
    alerts = screen_conjunctions(
        states,
        threshold_km=40.0,      # yakınlık eşiği (km)
        altitude_band_km=300.0  # aynı irtifa bandı (km)
    )

    print(f"Bulunan yaklaşım (alert) sayısı: {len(alerts)}")

    if not alerts:
        print("No close approaches under current thresholds.")
        return

    # 5) DataFrame + risk puanı
    df = pd.DataFrame(alerts)
    df = add_risk_scores(df)

    # 6) Sırala ve göster (ilk 20 satır)
    df = df.sort_values(["risk_score", "miss_distance_km"], ascending=[False, True])
    print(">>> İlk 20 kayıt:")
    print(df.head(20).to_string(index=False))

    # 7) Kaydet
    df.to_csv("alerts.csv", index=False)

    # Çift bazında özet
    summary = (
        df.groupby(["obj_a", "obj_b"], as_index=False)
          .agg(
              time=("time", "min"),
              miss_distance_km=("miss_distance_km", "min"),
              rel_speed_kms=("rel_speed_kms", "max"),
              altitude_km=("altitude_km", "mean"),
              risk_score=("risk_score", "max"),
          )
          .sort_values(["risk_score", "miss_distance_km"], ascending=[False, True])
    )
    summary.to_csv("alerts_summary_by_pair.csv", index=False)
    print("Saved to alerts.csv & alerts_summary_by_pair.csv")
    print(">>> DONE")


if __name__ == "__main__":
    main()
