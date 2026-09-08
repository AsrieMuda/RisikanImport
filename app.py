import streamlit as st
import pandas as pd
import feedparser

# Tetapan Muka Surat Aplikasi
st.set_page_config(
    page_title="Pusat Risikan & Food Search Import PKKM",
    page_icon="🔍",
    layout="wide"
)

# Tajuk & Penerangan
st.title("🛡️ Pusat Risikan Makanan & Food Search (Import)")
st.caption("Aplikasi Pemantauan OSINT & Semakan Food Alert Antarabangsa untuk Cawangan Import PKKM")

# Fungsi Ambil Data RSS Feed Antarabangsa
@st.cache_data(ttl=1800) # Simpan data dalam memori selama 30 minit
def load_food_alerts():
    feeds = {
        "US FDA Food Recalls": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml"
    }
    
    alert_list = []
    
    for source, url in feeds.items():
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            alert_list.append({
                "Sumber": source,
                "Tajuk / Produk": entry.title,
                "Tarikh": getattr(entry, 'published', 'Tiada Tarikh'),
                "Pautan Laporan": entry.link,
                "Ringkasan": getattr(entry, 'summary', 'Tiada Ringkasan')
            })
            
    return pd.DataFrame(alert_list)

# Memuat naik data
with st.spinner("Menarik data amaran makanan antarabangsa terkini..."):
    df_alerts = load_food_alerts()

# BAHAGIAN 1: METRIK SUMMARY
st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("Jumlah Alert Dikesan", len(df_alerts))
col2.metric("Sumber Monitor Utama", "US FDA & EU RASFF")
col3.metric("Status Integrasi", "Aktif (Auto-Sync)")

st.divider()

# BAHAGIAN 2: FOOD SEARCH ENGINE
st.subheader("🔍 Carian Risikan Makanan (Food Search)")
query = st.text_input("Masukkan nama produk, ramuan (cth: Salmonella, Ethylene Oxide), atau pengilang:", "")

# Tapis Data Mengikut Carian
if query:
    filtered_df = df_alerts[
        df_alerts['Tajuk / Produk'].str.contains(query, case=False, na=False) |
        df_alerts['Ringkasan'].str.contains(query, case=False, na=False)
    ]
else:
    filtered_df = df_alerts

# Paparan Hasil Carian
st.write(f"Menunjukkan **{len(filtered_df)}** rekod hasil carian:")

# Guna data editor / table Streamlit
st.dataframe(
    filtered_df[['Sumber', 'Tajuk / Produk', 'Tarikh', 'Pautan Laporan']],
    use_container_width=True,
    column_config={
        "Pautan Laporan": st.column_config.LinkColumn("Pautan Laporan Lanjut")
    }
)

# BAHAGIAN 3: EKSPORT DATA UNTUK DOSIER RISIKAN / FOSIM
st.divider()
st.subheader("📥 Muat Turun Data Risikan")

csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📄 Muat Turun Laporan Risikan (CSV)",
    data=csv_data,
    file_name="laporan_risikan_import_food_alert.csv",
    mime="text/csv"
)
