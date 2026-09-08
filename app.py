import streamlit as st
import pandas as pd
import feedparser

# Tetapan Muka Surat Aplikasi
st.set_page_config(
    page_title="Pusat Risikan & Food Search Import PKKM",
    page_icon="🇲🇾",
    layout="wide"
)

# HEADER RASMI KERAJAAN MALAYSIA / KKM
st.markdown("""
    <div style="display: flex; align-items: center; background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-bottom: 4px solid #003366; margin-bottom: 25px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/2/26/Coat_of_arms_of_Malaysia.svg" style="width: 110px; margin-right: 25px;">
        <div>
            <h4 style="margin:0; color: #003366; font-family: sans-serif; font-weight: bold; letter-spacing: 1px;">KEMENTERIAN KESIHATAN MALAYSIA</h4>
            <h2 style="margin: 2px 0; color: #111; font-family: sans-serif; font-weight: 800;">PROGRAM KESELAMATAN DAN KUALITI MAKANAN</h2>
            <h5 style="margin: 0; color: #555; font-weight: 600;">CAWANGAN IMPORT | UNIT RISIKAN DAN SIASATAN</h5>
            <p style="margin-top: 6px; margin-bottom: 0; font-size: 13px; color: #666; line-height: 1.4;">
                📍 Aras 4, Menara Prisma, No. 26, Jalan Persiaran Perdana, Presint 3, 62675 Putrajaya, Malaysia.<br>
                💻 <b>Sistem OSINT & Food Search Import (SISTEM RISIKAN IMPORT)</b>
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Fungsi Ambil Data Multi-Source RSS Feed Antarabangsa
@st.cache_data(ttl=1800)
def load_food_alerts():
    feeds = {
        "US FDA Food Recalls": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml",
        "UK Food Standards Agency (FSA)": "https://www.food.gov.uk/rss/news-and-alerts/alerts/rss.xml",
        "EU RASFF / Safety News": "https://www.foodsafetynews.com/tag/rasff/feed/",
        "Singapore SFA / Food Alerts": "https://www.foodsafetynews.com/tag/singapore-food-agency/feed/"
    }
    
    alert_list = []
    
    for source, url in feeds.items():
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:10]: # Ambil 10 teratas bagi setiap sumber
                alert_list.append({
                    "Sumber": source,
                    "Tajuk / Produk": getattr(entry, 'title', 'Tiada Tajuk'),
                    "Tarikh": getattr(entry, 'published', getattr(entry, 'updated', 'Tiada Tarikh')),
                    "Pautan Laporan": getattr(entry, 'link', '#'),
                    "Ringkasan": getattr(entry, 'summary', 'Tiada Ringkasan')
                })
        except Exception as e:
            st.warning(f"Gagal menarik data dari {source}: {e}")
            
    if not alert_list:
        return pd.DataFrame(columns=["Sumber", "Tajuk / Produk", "Tarikh", "Pautan Laporan", "Ringkasan"])
        
    return pd.DataFrame(alert_list)

# Memuat naik data
with st.spinner("Menarik data amaran makanan antarabangsa dari pelbagai portal global..."):
    df_alerts = load_food_alerts()

# BAHAGIAN 1: METRIK SUMMARY
st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("Jumlah Alert Dikesan", len(df_alerts))
col2.metric("Sumber Monitor Utama", "US FDA, UK FSA, EU RASFF & SFA")
col3.metric("Status Integrasi", "Aktif (Multi-Source Sync)")

st.divider()

# BAHAGIAN 2: FOOD SEARCH ENGINE & PENAPIS SUMBER
st.subheader("🔍 Carian Risikan Makanan Bersepadu (Food Search)")

col_search, col_filter = st.columns([3, 1])

with col_filter:
    sumber_list = ["Semua Sumber"] + list(df_alerts['Sumber'].unique()) if not df_alerts.empty else ["Semua Sumber"]
    selected_source = st.selectbox("Tapis Mengikut Sumber:", sumber_list)

with col_search:
    query = st.text_input("Masukkan nama produk, ramuan (cth: Salmonella, Ethylene Oxide), atau pengilang:", "")

# Proses Penapisan Data
filtered_df = df_alerts.copy()

if selected_source != "Semua Sumber":
    filtered_df = filtered_df[filtered_df['Sumber'] == selected_source]

if query and not filtered_df.empty:
    filtered_df = filtered_df[
        filtered_df['Tajuk / Produk'].str.contains(query, case=False, na=False) |
        filtered_df['Ringkasan'].str.contains(query, case=False, na=False)
    ]

st.write(f"Menunjukkan **{len(filtered_df)}** rekod hasil carian:")

if not filtered_df.empty:
    st.dataframe(
        filtered_df[['Sumber', 'Tajuk / Produk', 'Tarikh', 'Pautan Laporan']],
        use_container_width=True,
        column_config={
            "Pautan Laporan": st.column_config.LinkColumn("Pautan Laporan Lanjut")
        }
    )
else:
    st.info("Tiada rekod amaran makanan ditemui mengikut kriteria carian anda.")

# BAHAGIAN 3: EKSPORT DATA
st.divider()
st.subheader("📥 Muat Turun Data Risikan")

if not filtered_df.empty:
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Muat Turun Laporan Risikan (CSV)",
        data=csv_data,
        file_name="laporan_risikan_import_food_alert.csv",
        mime="text/csv"
    )
