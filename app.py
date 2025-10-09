import streamlit as st
import pandas as pd
import plotly.express as px
import ast  # untuk parsing dict string
import subprocess  # untuk jalankan main.py
import math

st.set_page_config(page_title="Dashboard MagangHub", layout="wide")

st.title("📊 Dashboard Lowongan MagangHub")

# --- Tombol Refresh Data ---
if st.button("🔄 Refresh Data dari API"):
    st.write("Mengambil data terbaru dari MagangHub...")
    subprocess.run(["python", "main.py"])
    st.success("Data berhasil diperbarui!")

# --- Load CSV ---
df = pd.read_csv("data/maganghub_jobs.csv")

# --- Normalisasi kolom nested (perusahaan, jadwal, status) ---
def normalize_column(df, col_name, prefix):
    if col_name in df.columns:
        parsed = df[col_name].dropna().apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else {}
        )
        normalized = pd.json_normalize(parsed)
        normalized = normalized.add_prefix(prefix + ".")
        df = df.drop(columns=[col_name])
        df = pd.concat([df, normalized], axis=1)
    return df

df = normalize_column(df, "perusahaan", "perusahaan")
df = normalize_column(df, "jadwal", "jadwal")
df = normalize_column(df, "ref_status_posisi", "status")

# --- Pastikan kolom penting ada ---
if "perusahaan.nama_perusahaan" not in df.columns:
    df["perusahaan.nama_perusahaan"] = "Tidak diketahui"
if "perusahaan.nama_kabupaten" not in df.columns:
    df["perusahaan.nama_kabupaten"] = "Tidak diketahui"
if "perusahaan.nama_provinsi" not in df.columns:
    df["perusahaan.nama_provinsi"] = "Tidak diketahui"

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

# slice data sesuai halaman
df_page = df.iloc[start:end][cols_show].copy()

# tambahkan kolom No (1,2,3,...)
df_page.insert(0, "No", range(start + 1, start + 1 + len(df_page)))

# jadikan kolom No sebagai index (mengganti index default)
df_page = df_page.set_index("No")

st.dataframe(df_page, use_container_width=True)

st.caption(f"Menampilkan {start+1}-{min(end,total_items)} dari {total_items} data")

# --- Download Button ---
if not df.empty:
    st.download_button("⬇️ Download Data (CSV)",
                       df.to_csv(index=False).encode("utf-8"),
                       "filtered_jobs.csv", "text/csv")
