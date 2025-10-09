import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import math
import os
import subprocess
from api_client import fetch_all_jobs  # ambil langsung dari modul scraper

st.set_page_config(page_title="Dashboard MagangHub", layout="wide")
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

# --- Pastikan kolom penting ada ---
for col in ["perusahaan.nama_perusahaan", "perusahaan.nama_kabupaten", "perusahaan.nama_provinsi"]:
    if col not in df.columns:
        df[col] = "Tidak diketahui"

# --- Sidebar Filter ---
st.sidebar.header("🔍 Filter Data")
perusahaan = st.sidebar.multiselect(
    "Filter Perusahaan", df["perusahaan.nama_perusahaan"].dropna().unique()
)
if perusahaan:
    df = df[df["perusahaan.nama_perusahaan"].isin(perusahaan)]

kabupaten = st.sidebar.multiselect(
    "Filter Lokasi (Kabupaten)", df["perusahaan.nama_kabupaten"].dropna().unique()
)
if kabupaten:
    df = df[df["perusahaan.nama_kabupaten"].isin(kabupaten)]

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
    "posisi", "deskripsi_posisi", "jumlah_kuota", "jumlah_terdaftar",
    "perusahaan.nama_perusahaan", "perusahaan.nama_kabupaten",
    "perusahaan.nama_provinsi", "jadwal.tanggal_mulai", "jadwal.tanggal_selesai"
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
