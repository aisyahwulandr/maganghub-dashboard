# 📊 MagangHub Scraper & Dashboard

Proyek ini melakukan **scraping data lowongan magang** dari [MagangHub Kemnaker RI](https://maganghub.kemnaker.go.id/) menggunakan API internal, kemudian menampilkan hasilnya dalam bentuk **dashboard interaktif** dengan **Streamlit**.

---

## 🚀 Fitur

- 🔄 **Scraping data otomatis** dari API MagangHub
- 💾 Simpan hasil ke:
  - `data/maganghub_jobs.csv`
  - `data/maganghub_jobs.json`
- 📊 **Dashboard Streamlit**:
  - Grafik jumlah lowongan per kabupaten
  - Grafik jumlah lowongan per provinsi
  - Top 20 perusahaan dengan lowongan terbanyak
  - Tabel daftar lowongan dengan pagination
- 🔍 Filter berdasarkan **perusahaan** & **lokasi**
- ⬇️ Download data hasil filter ke CSV langsung dari dashboard

---

## 📂 Struktur Project

```
.
├── api_client.py       # Modul untuk request ke API MagangHub
├── utils.py            # Utility: save ke CSV & JSON
├── main.py             # Script scraping utama
├── app.py              # Dashboard Streamlit
├── data/               # Folder hasil scraping (CSV & JSON)
├── requirements.txt    # Daftar dependencies
├── .gitignore
├── .gitattributes
└── README.md
```

---

## ⚙️ Instalasi

1. Clone repository ini:

```bash
git clone https://github.com/aisyahwulandr/maganghub-dashboard.git
cd maganghub-dashboard
```

2. Buat virtual environment (opsional tapi disarankan):

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate    # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Cara Penggunaan

### 1. Jalankan Scraper
Scraping data terbaru dari MagangHub:

```bash
python main.py
```

Data akan tersimpan otomatis di:
- `data/maganghub_jobs.csv`
- `data/maganghub_jobs.json`

### 2. Jalankan Dashboard
Tampilkan dashboard interaktif dengan Streamlit:

```bash
streamlit run app.py
```

Dashboard akan bisa diakses di:  
👉 http://localhost:8501/

---

## 🔮 Roadmap

- [ ] Auto-refresh data setiap X jam di background
- [ ] Deploy dashboard ke **Streamlit Cloud / Render / Heroku**
- [ ] Tambah filter berdasarkan **program studi** & **jenjang**
- [ ] Visualisasi timeline (jadwal magang)

---

## 📜 Lisensi

Proyek ini dibuat untuk tujuan **belajar & personal use**.  
Tidak untuk penggunaan komersial tanpa izin.
