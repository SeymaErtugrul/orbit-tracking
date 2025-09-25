def score_event(miss_km, rel_kms, alt_km):
    # daha yakın = daha riskli; daha hızlı = daha riskli; alçak irtifa = biraz daha riskli
    dist_score = max(0, 100 - 2*miss_km)           # 0–100
    speed_bonus = min(25, rel_kms * 4.0)           # 0–25
    alt_bonus = 0 if alt_km > 700 else (700 - alt_km) / 25.0  # max ~28
    score = dist_score + speed_bonus + alt_bonus
    return int(max(1, min(score, 100)))
def add_risk_scores(df):
    """
    Yakın yaklaşım kayıtlarına risk skorları ekler.
    Basit demo metodu: düşük mesafe ve yüksek hız = daha yüksek risk.
    """
    scores = []
    for _, row in df.iterrows():
        base = 10
        if row["miss_distance_km"] < 5:
            base += 40
        elif row["miss_distance_km"] < 20:
            base += 20
        elif row["miss_distance_km"] < 50:
            base += 10

        if row["rel_speed_kms"] > 5:
            base += 20
        elif row["rel_speed_kms"] > 2:
            base += 10

        scores.append(base)

    df["risk_score"] = scores
    return df
