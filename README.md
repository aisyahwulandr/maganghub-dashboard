# 📊 MagangHub Scraper & Dashboard

Proyek ini melakukan **pengambilan data lowongan magang** dari [MagangHub Kemnaker RI](https://maganghub.kemnaker.go.id/) menggunakan **API internal**, kemudian menampilkan hasilnya dalam bentuk **dashboard interaktif** dengan **Streamlit**.

👉 **Coba langsung di website:** [https://magangdash.streamlit.app/](https://magangdash.streamlit.app/)


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
- ⚙️ Dua mode penggunaan:
  - **CSV Lokal** → membaca data dari file CSV hasil scraping
  - **API Online** → langsung mengambil data terbaru dari API (mode ini lebih cocok untuk deploy di hosting)

---

## 📂 Struktur Project

```
.
├── api_client.py       # Modul untuk request ke API MagangHub
├── utils.py            # Utility: simpan data ke CSV & JSON
├── main.py             # Script scraping utama (generate CSV/JSON)
├── app.py              # Dashboard Streamlit (dua mode: CSV & API)
├── data/               # Folder hasil scraping (CSV & JSON)
├── requirements.txt    # Daftar dependencies
├── .gitignore
├── .gitattributes
└── README.md
```

---

## 📦 Prasyarat

- Python **3.9+**
- Koneksi internet untuk mengakses API MagangHub
- Git (jika ingin clone repo)

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
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Cara Penggunaan

### 1. Mode CSV Lokal (default di laptop)
Jalankan scraper untuk mengambil data terbaru:

```bash
python main.py
```

Data akan otomatis tersimpan di:
- `data/maganghub_jobs.csv`
- `data/maganghub_jobs.json`

Lalu tampilkan dashboard:

```bash
streamlit run app.py
```

Dashboard akan bisa diakses di:  
👉 http://localhost:8501/

### 2. Mode API Online (disarankan untuk deploy)
Anda bisa memilih mode **API Online** di sidebar dashboard.  
Pada mode ini, app akan langsung mengambil data dari API tanpa membutuhkan file CSV.  

---

## 🌐 Deploy ke Streamlit Cloud

1. Pastikan file `requirements.txt` sudah ada dengan isi minimal:
   ```
   streamlit
   pandas
   plotly
   requests
   ```
2. Push kode ke repository GitHub Anda.
3. Deploy ke [Streamlit Cloud](https://streamlit.io/cloud).
4. **Gunakan mode API Online** saat di cloud.  
   ⚠️ Catatan: jika menggunakan mode CSV Lokal, file CSV akan hilang setelah restart karena storage di cloud bersifat sementara (ephemeral).

👉 Hasil deploy project ini dapat langsung dicoba di:  
🔗 [https://magangdash.streamlit.app/](https://magangdash.streamlit.app/)

---

## 🔮 Roadmap

- [ ] Auto-refresh data setiap X jam di background
- [ ] Deploy dashboard ke **Streamlit Cloud / Render / Heroku**
- [ ] Tambah filter berdasarkan **program studi** & **jenjang**
- [ ] Visualisasi timeline (jadwal magang)
- [ ] Simpan data ke database (contoh: SQLite / PostgreSQL) untuk lebih stabil

---

## 📜 Lisensi

Proyek ini dibuat untuk tujuan **belajar & personal use**.  
Tidak untuk penggunaan komersial tanpa izin.
