import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import math
import os
import subprocess
from api_client import fetch_all_jobs  # ambil langsung dari modul scraper
from sessions import track_sessions, admin_auth

st.set_page_config(page_title="Dashboard MagangHub", layout="wide")

# hitung sessions
sessions = track_sessions(timeout=120, max_sessions=50)

# panel admin
admin_auth(sessions)

st.title("📊 Dashboard Lowongan MagangHub")

# --- Pilih Mode Data ---
st.sidebar.header("⚙️ Mode Data")
mode = st.sidebar.radio("Pilih sumber data:", ("CSV Lokal", "API Online"))

# --- Load Data ---
df = None
if mode == "CSV Lokal":
    # tombol refresh hanya untuk CSV
    if st.button("🔄 Refresh Data dari API"):
        st.write("Mengambil data terbaru dari MagangHub...")
        subprocess.run(["python", "main.py"])
        st.success("Data berhasil diperbarui!")

    csv_path = "data/maganghub_jobs.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        st.success("✅ Data dimuat dari CSV lokal")
    else:
        st.error("❌ CSV lokal tidak ditemukan. Jalankan `main.py` dulu atau klik Refresh.")
        st.stop()

else:
    st.info("🔄 Mengambil data dari API MagangHub...")
    jobs = fetch_all_jobs(limit_total=200, per_page=20)
    if not jobs:
        st.error("❌ Gagal mengambil data dari API.")
        st.stop()
    df = pd.DataFrame(jobs)
    st.success(f"✅ Berhasil ambil {len(df)} data dari API")

# --- Normalisasi kolom nested ---
def normalize_column(df, col_name, prefix):
    if col_name in df.columns:
        parsed = df[col_name].dropna().apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
        parsed = parsed.apply(lambda x: x if isinstance(x, dict) else {})
        normalized = pd.json_normalize(parsed)
        normalized = normalized.add_prefix(prefix + ".")
        df = df.drop(columns=[col_name])
        df = pd.concat([df, normalized], axis=1)
    return df

df = normalize_column(df, "perusahaan", "perusahaan")
df = normalize_column(df, "jadwal", "jadwal")
df = normalize_column(df, "ref_status_posisi", "status")

# --- Normalisasi khusus program_studi ---
if "program_studi" in df.columns:
    def extract_programs(x):
        if pd.isna(x):
            return None
        try:
            data = ast.literal_eval(x) if isinstance(x, str) else x
            if isinstance(data, list):
                return ", ".join([d.get("title", "") for d in data if isinstance(d, dict)])
            return None
        except Exception:
            return None

    df["program_studi_clean"] = df["program_studi"].apply(extract_programs)

# --- Pastikan kolom penting ada ---
for col in ["perusahaan.nama_perusahaan", "perusahaan.nama_kabupaten", "perusahaan.nama_provinsi","perusahaan.alamat"]:
    if col not in df.columns:
        df[col] = "Tidak diketahui"

# --- Sidebar Filter ---
st.sidebar.header("🔍 Filter Data")

# Filter perusahaan
perusahaan = st.sidebar.multiselect(
    "Filter Perusahaan", df["perusahaan.nama_perusahaan"].dropna().unique()
)
if perusahaan:
    df = df[df["perusahaan.nama_perusahaan"].isin(perusahaan)]

# Filter posisi
if "posisi" in df.columns:
    posisi = st.sidebar.multiselect(
        "Filter Posisi", df["posisi"].dropna().unique()
    )
    if posisi:
        df = df[df["posisi"].isin(posisi)]

# Filter deskripsi posisi (pakai search text)
if "deskripsi_posisi" in df.columns:
    deskripsi = st.sidebar.text_input("Cari Deskripsi Posisi")
    if deskripsi:
        df = df[df["deskripsi_posisi"].str.contains(deskripsi, case=False, na=False)]
        
# Filter program studi
if "program_studi_clean" in df.columns:
    cari_prodi = st.sidebar.text_input("Cari Program Studi")
    if cari_prodi:
        df = df[df["program_studi_clean"].str.contains(cari_prodi, case=False, na=False)]

# Filter provinsi
provinsi = st.sidebar.multiselect(
    "Filter Lokasi (Provinsi)", df["perusahaan.nama_provinsi"].dropna().unique()
)
if provinsi:
    df = df[df["perusahaan.nama_provinsi"].isin(provinsi)]

# Filter kabupaten
kabupaten = st.sidebar.multiselect(
    "Filter Lokasi (Kabupaten)", df["perusahaan.nama_kabupaten"].dropna().unique()
)
if kabupaten:
    df = df[df["perusahaan.nama_kabupaten"].isin(kabupaten)]

# Filter alamat
if "perusahaan.alamat" in df.columns:
    alamat = st.sidebar.multiselect(
        "Filter Lokasi (Alamat)", df["perusahaan.alamat"].dropna().unique()
    )
    if alamat:
        df = df[df["perusahaan.alamat"].isin(alamat)]

# Filter jumlah kuota
if "jumlah_kuota" in df.columns and df["jumlah_kuota"].notna().any():
    kuota_min = int(df["jumlah_kuota"].min())
    kuota_max = int(df["jumlah_kuota"].max())
    if kuota_min != kuota_max:
        kuota_min, kuota_max = st.sidebar.slider(
            "Filter Jumlah Kuota",
            kuota_min, kuota_max, (kuota_min, kuota_max)
        )
        df = df[(df["jumlah_kuota"] >= kuota_min) & (df["jumlah_kuota"] <= kuota_max)]
    else:
        st.sidebar.info(f"Jumlah kuota semua data: {kuota_min}")

# Filter jumlah terdaftar
if "jumlah_terdaftar" in df.columns and df["jumlah_terdaftar"].notna().any():
    terdaftar_min = int(df["jumlah_terdaftar"].min())
    terdaftar_max = int(df["jumlah_terdaftar"].max())
    if terdaftar_min != terdaftar_max:
        terdaftar_min, terdaftar_max = st.sidebar.slider(
            "Filter Jumlah Terdaftar",
            terdaftar_min, terdaftar_max, (terdaftar_min, terdaftar_max)
        )
        df = df[(df["jumlah_terdaftar"] >= terdaftar_min) & (df["jumlah_terdaftar"] <= terdaftar_max)]
    else:
        st.sidebar.info(f"Jumlah terdaftar semua data: {terdaftar_min}")
        
# Filter created_at
if "created_at" in df.columns:
    # ubah ke datetime
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    created_min = df["created_at"].min()
    created_max = df["created_at"].max()

    created_range = st.sidebar.date_input(
        "Filter Tanggal Dibuat",
        value=(created_min.date(), created_max.date()),
        min_value=created_min.date(),
        max_value=created_max.date()
    )

    if created_range:
        start, end = created_range
        df = df[(df["created_at"].dt.date >= start) & (df["created_at"].dt.date <= end)]

# Filter updated_at
if "updated_at" in df.columns:
    df["updated_at"] = pd.to_datetime(df["updated_at"], errors="coerce")

    updated_min = df["updated_at"].min()
    updated_max = df["updated_at"].max()

    updated_range = st.sidebar.date_input(
        "Filter Tanggal Diupdate",
        value=(updated_min.date(), updated_max.date()),
        min_value=updated_min.date(),
        max_value=updated_max.date()
    )

    if updated_range:
        start, end = updated_range
        df = df[(df["updated_at"].dt.date >= start) & (df["updated_at"].dt.date <= end)]


# --- Grafik Lowongan per Kabupaten ---
st.subheader("📍 Jumlah Lowongan per Kabupaten")
if not df.empty:
    kabupaten_count = df["perusahaan.nama_kabupaten"].value_counts().reset_index()
    kabupaten_count.columns = ["Kabupaten", "Jumlah"]
    fig1 = px.bar(kabupaten_count, x="Kabupaten", y="Jumlah",
                  title="Jumlah Lowongan per Kabupaten")
    st.plotly_chart(fig1, use_container_width=True)

# --- Grafik Lowongan per Provinsi ---
st.subheader("🗺️ Jumlah Lowongan per Provinsi")
if not df.empty:
    provinsi_count = df["perusahaan.nama_provinsi"].value_counts().reset_index()
    provinsi_count.columns = ["Provinsi", "Jumlah"]
    fig2 = px.bar(provinsi_count, x="Provinsi", y="Jumlah",
                  title="Jumlah Lowongan per Provinsi")
    st.plotly_chart(fig2, use_container_width=True)

# --- Grafik Lowongan per Perusahaan ---
st.subheader("🏢 Top 20 Perusahaan dengan Lowongan")
if not df.empty:
    company_count = df["perusahaan.nama_perusahaan"].value_counts().reset_index()
    company_count.columns = ["Perusahaan", "Jumlah"]
    fig3 = px.bar(company_count.head(20), x="Perusahaan", y="Jumlah",
                  title="Top 20 Perusahaan dengan Lowongan")
    st.plotly_chart(fig3, use_container_width=True)

# --- Tabel dengan Pagination ---
st.subheader("📋 Daftar Lowongan")

items_per_page = 10
total_items = len(df)
total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

page = st.number_input("Halaman:", min_value=1, max_value=total_pages, value=1, step=1)

start = (page - 1) * items_per_page
end = start + items_per_page
cols_show = [
    "perusahaan.nama_perusahaan", "posisi", "deskripsi_posisi", "program_studi_clean",
    "perusahaan.nama_provinsi", "perusahaan.nama_kabupaten", "perusahaan.alamat" ,
    "jumlah_kuota", "jumlah_terdaftar", "created_at", "updated_at",
    "jadwal.tanggal_mulai", "jadwal.tanggal_selesai"
]
cols_show = [c for c in cols_show if c in df.columns]

df_page = df.iloc[start:end][cols_show].copy()
df_page.insert(0, "No", range(start + 1, start + 1 + len(df_page)))
df_page = df_page.set_index("No")

st.dataframe(df_page, use_container_width=True)
st.caption(f"Menampilkan {start+1}-{min(end,total_items)} dari {total_items} data")

# --- Download Button ---
if not df.empty:
    st.download_button("⬇️ Download Data (CSV)",
                       df.to_csv(index=False).encode("utf-8"),
                       "filtered_jobs.csv", "text/csv")
