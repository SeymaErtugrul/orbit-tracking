# Space Debris Guard 

## Amaç
Gerçek CelesTrak TLE verilerini kullanarak (ISS + Starlink + aktif enkaz) yörüngelerde **yakın geçişleri** tespit eden bir Python tabanlı araç.

## Veri Kaynağı
- CelesTrak Current GP Data
- Dosyalar: `data/iss.txt`, `data/starlink.txt`, `data/debris.txt`

## Yöntem
1. **TLE Yükleme** → `tle_loader.py`
2. **Yörünge Yayılımı** → `propagate.py` (SGP4)
3. **Yakın Yaklaşım Taraması** → `screen.py` / `screen2.py`
4. **Risk Skoru** → `scoring.py`
5. **Çıktılar**:
   - `alerts.csv` → tüm olaylar
   - `alerts_summary_by_pair.csv` → özet
   - `top10_conjunctions.png` → grafik

## Çalıştırma
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py
python viz.py
