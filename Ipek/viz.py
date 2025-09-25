import pandas as pd
import matplotlib.pyplot as plt

# CSV dosyasını oku
df = pd.read_csv("alerts_summary_by_pair.csv")

# En yakın 10 eşleşme
top10 = df.sort_values("miss_distance_km").head(10)

labels = [f"{a} vs {b}" for a,b in zip(top10["obj_a"], top10["obj_b"])]
values = top10["miss_distance_km"]

plt.figure(figsize=(10,6))
plt.barh(labels, values)
plt.xlabel("Mesafe (km)")
plt.title("En Yakın 10 Uydu Yaklaşımı")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("top10_conjunctions.png", dpi=150)
print("top10_conjunctions.png kaydedildi")
