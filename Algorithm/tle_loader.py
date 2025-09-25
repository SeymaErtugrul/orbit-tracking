import requests

class TLEDownloader:
    @staticmethod
    def download_tle(url):
        """TLE verilerini indir ve parse et"""
        try:
            print(f"📡 Veriler indiriliyor: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            lines = response.text.strip().splitlines()

            satellites = []
            for i in range(0, len(lines), 3):
                if i + 2 < len(lines):
                    name = lines[i].strip()
                    line1 = lines[i+1].strip()
                    line2 = lines[i+2].strip()
                    if line1.startswith("1 ") and line2.startswith("2 "):
                        satellites.append({
                            "name": name,
                            "line1": line1,
                            "line2": line2,
                            "catalog_id": line1[2:7].strip()
                        })
            print(f"✅ {len(satellites)} uydu bulundu")
            return satellites

        except requests.RequestException as e:
            print(f"İndirme hatası: {e}")
            return []

