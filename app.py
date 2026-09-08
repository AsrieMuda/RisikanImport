import streamlit as st
import pandas as pd
import feedparser
from PIL import Image
import pytesseract

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

# NAVIGASI TAB UTAMA
tab1, tab2, tab3 = st.tabs([
    "🔍 Food Search & Alerts Global", 
    "📲 Pemantauan Produk Viral (Medsos)", 
    "📷 Imbasan Label Image (OCR AI)"
])

# ==========================================
# TAB 1: FOOD SEARCH & ALERTS GLOBAL
# ==========================================
with tab1:
    @st.cache_data(ttl=1800)
    def load_food_alerts():
        feeds = {
            "US FDA Food Recalls": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml",
            "UK Food Standards Agency": "https://www.food.gov.uk/rss/news-and-alerts/alerts/rss.xml",
            "EU RASFF / Safety News": "https://www.foodsafetynews.com/tag/rasff/feed/",
            "Singapore SFA / Food Alerts": "https://www.foodsafetynews.com/tag/singapore-food-agency/feed/"
        }
        alert_list = []
        for source, url in feeds.items():
            try:
                parsed = feedparser.parse(url)
                for entry in parsed.entries[:10]:
                    alert_list.append({
                        "Sumber": source,
                        "Tajuk / Produk": getattr(entry, 'title', 'Tiada Tajuk'),
                        "Tarikh": getattr(entry, 'published', getattr(entry, 'updated', 'Tiada Tarikh')),
                        "Pautan Laporan": getattr(entry, 'link', '#'),
                        "Ringkasan": getattr(entry, 'summary', 'Tiada Ringkasan')
                    })
            except Exception as e:
                pass
        return pd.DataFrame(alert_list) if alert_list else pd.DataFrame(columns=["Sumber", "Tajuk / Produk", "Tarikh", "Pautan Laporan", "Ringkasan"])

    df_alerts = load_food_alerts()

    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Alert Dikesan", len(df_alerts))
    col2.metric("Sumber Monitor Utama", "US FDA, UK FSA, EU RASFF & SFA")
    col3.metric("Status Integrasi", "Aktif (Multi-Source Sync)")

    st.divider()
    st.subheader("🔍 Carian Risikan Makanan Bersepadu")
    
    col_search, col_filter = st.columns([3, 1])
    with col_filter:
        sumber_list = ["Semua Sumber"] + list(df_alerts['Sumber'].unique()) if not df_alerts.empty else ["Semua Sumber"]
        selected_source = st.selectbox("Tapis Mengikut Sumber:", sumber_list)
    with col_search:
        query = st.text_input("Masukkan nama produk, ramuan, atau pengilang:", "")

    filtered_df = df_alerts.copy()
    if selected_source != "Semua Sumber":
        filtered_df = filtered_df[filtered_df['Sumber'] == selected_source]
    if query and not filtered_df.empty:
        filtered_df = filtered_df[
            filtered_df['Tajuk / Produk'].str.contains(query, case=False, na=False) |
            filtered_df['Ringkasan'].str.contains(query, case=False, na=False)
        ]

    if not filtered_df.empty:
        st.dataframe(filtered_df[['Sumber', 'Tajuk / Produk', 'Tarikh', 'Pautan Laporan']], use_container_width=True)
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Muat Turun Laporan Risikan (CSV)", data=csv_data, file_name="laporan_risikan.csv", mime="text/csv")
    else:
        st.info("Tiada rekod amaran makanan ditemui.")

# ==========================================
# TAB 2: PEMANTAUAN PRODUK VIRAL (MEDSOS)
# ==========================================
with tab2:
    st.subheader("📲 Risikan Produk Makanan Import Viral")
    st.caption("Modul tumpuan pengesanan trend snek/minuman import berisiko yang sedang hangat di pasaran tempatan.")
    
    cat_filter = st.selectbox("Kategori Trend Risikan:", ["Semua Kategori", "Kopi / Minuman Kurus", "Snek & Gula-Gula Import", "Suplemen & Kesihatan"])
    
    # Sample Data Risikan Medsos
    viral_data = [
        {"Kategori": "Kopi / Minuman Kurus", "Nama Produk": "Kopi Detox Slim Import", "Platform": "TikTok / Shopee", "Status Risk": "🚨 Berisiko Tinggi (Syak Sibutramine)", "Nota": "Viral dakwaan turun 5kg seminggu"},
        {"Kategori": "Snek & Gula-Gula Import", "Nama Produk": "Candy Sour Chews (Tanpa Label BM/Inggeris)", "Platform": "Facebook / TikTok", "Status Risk": "⚠️ Isu Perlabelan", "Nota": "Tiada maklumat pengimport tempatan"},
        {"Kategori": "Suplemen & Kesihatan", "Nama Produk": "Jelly Collagen Overclaim", "Platform": "Instagram", "Status Risk": "🚨 Overclaim Kesihatan", "Nota": "Klaim merawat penyakit kronik"}
    ]
    df_viral = pd.DataFrame(viral_data)
    
    if cat_filter != "Semua Kategori":
        df_viral = df_viral[df_viral['Kategori'] == cat_filter]
        
    st.dataframe(df_viral, use_container_width=True)

# ==========================================
# TAB 3: IMBASAN LABEL IMAGE (OCR AI)
# ==========================================
with tab3:
    st.subheader("📷 Imbasan Teks Label & Semakan Bahan Terlarang (OCR)")
    st.caption("Muat naik gambar label produk import untuk mengekstrak ramuan dan mengesan bahan berisiko secara automatik.")
    
    uploaded_file = st.file_uploader("Pilih gambar label produk (PNG / JPG / JPEG):", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar Label Diunggah", use_column_width=True)
        
        with st.spinner("Pengecam OCR sedang membaca teks pada gambar..."):
            try:
                # Proses OCR menggunakan Pytesseract
                extracted_text = pytesseract.image_to_string(image)
                
                st.divider()
                st.write("📝 **Hasil Teks Diekstrak:**")
                st.text_area("Teks Label Detected:", extracted_text, height=150)
                
                # Semakan kata kunci berisiko
                risk_keywords = ["sibutramine", "sildenafil", "steroid", "rhodamine", "aflatoxin", "preservative", "colorant"]
                found_risks = [word for word in risk_keywords if word.lower() in extracted_text.lower()]
                
                if found_risks:
                    st.error(f"🚨 **AMARAN:** Bahan/Kata Kunci Berisiko Dikesan: {', '.join(found_risks)}")
                else:
                    st.success("✅ Tiada bahan berisiko utama dikesan secara automatik. Sila buat semakan manual lanjut.")
            except Exception as e:
                st.warning("Peringatan: Modul OCR memerlukan enjin Tesseract dipasang pada pelayan. Teks sampel dipaparkan untuk mod ujian.")
