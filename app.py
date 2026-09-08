import streamlit as st
import pandas as pd
import feedparser
from PIL import Image
import pytesseract

# Tetapan Muka Surat - Gunakan 'centered' untuk kesesuaian mobile
st.set_page_config(
    page_title="Pusat Risikan PKKM",
    page_icon="🇲🇾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# STYLESHEET KHAS UNTUK MOBILITY & RESPONSIVE DESIGN
st.markdown("""
    <style>
        /* Mengurangkan ruang kosong atas di skrin telefon */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        
        /* Header Responsive */
        .header-box {
            display: flex;
            flex-direction: row;
            align-items: center;
            background-color: #f8f9fa;
            padding: 12px;
            border-radius: 8px;
            border-bottom: 4px solid #003366;
            margin-bottom: 15px;
        }
        
        .header-img {
            width: 65px;
            margin-right: 12px;
        }
        
        .header-title-1 { font-size: 11px; color: #003366; font-weight: bold; margin:0; }
        .header-title-2 { font-size: 14px; color: #111; font-weight: 800; margin: 2px 0; }
        .header-title-3 { font-size: 11px; color: #555; font-weight: 600; margin:0; }
        .header-address { font-size: 10px; color: #666; margin-top: 4px; margin-bottom:0; line-height: 1.2; }

        /* Khusus untuk skrin kecil / Mobile View */
        @media (max-width: 640px) {
            .header-box {
                flex-direction: column;
                text-align: center;
            }
            .header-img {
                width: 55px;
                margin-right: 0;
                margin-bottom: 8px;
            }
            .header-title-2 { font-size: 13px; }
        }
    </style>
""", unsafe_allow_html=True)

# HEADER RASMI KERAJAAN MALAYSIA / KKM (MOBILE OPTIMIZED)
st.markdown("""
    <div class="header-box">
        <img class="header-img" src="https://upload.wikimedia.org/wikipedia/commons/2/26/Coat_of_arms_of_Malaysia.svg">
        <div>
            <h4 class="header-title-1">KEMENTERIAN KESIHATAN MALAYSIA</h4>
            <h2 class="header-title-2">PROGRAM KESELAMATAN DAN KUALITI MAKANAN</h2>
            <h5 class="header-title-3">CAWANGAN IMPORT | UNIT RISIKAN</h5>
            <p class="header-address">
                📍 Aras 4, Menara Prisma, Presint 3, Putrajaya.<br>
                💻 <b>SISTEM RISIKAN IMPORT (OSINT)</b>
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# NAVIGASI TAB UTAMA
tab1, tab2, tab3 = st.tabs([
    "🔍 Food Search", 
    "📲 Produk Viral", 
    "📷 OCR Label"
])

# ==========================================
# TAB 1: FOOD SEARCH & ALERTS GLOBAL
# ==========================================
with tab1:
    @st.cache_data(ttl=1800)
    def load_food_alerts():
        feeds = {
            "US FDA": "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/food-recalls/rss.xml",
            "UK FSA": "https://www.food.gov.uk/rss/news-and-alerts/alerts/rss.xml",
            "EU RASFF": "https://www.foodsafetynews.com/tag/rasff/feed/",
            "Singapore SFA": "https://www.foodsafetynews.com/tag/singapore-food-agency/feed/"
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

    # Metrics paparan menegak mesra mobile
    st.metric("Jumlah Alert Dikesan", len(df_alerts))

    st.subheader("🔍 Carian Risikan Makanan")
    
    sumber_list = ["Semua Sumber"] + list(df_alerts['Sumber'].unique()) if not df_alerts.empty else ["Semua Sumber"]
    selected_source = st.selectbox("Tapis Sumber:", sumber_list)
    query = st.text_input("Carian (cth: Salmonella, Kopi, Brand):", "")

    filtered_df = df_alerts.copy()
    if selected_source != "Semua Sumber":
        filtered_df = filtered_df[filtered_df['Sumber'] == selected_source]
    if query and not filtered_df.empty:
        filtered_df = filtered_df[
            filtered_df['Tajuk / Produk'].str.contains(query, case=False, na=False) |
            filtered_df['Ringkasan'].str.contains(query, case=False, na=False)
        ]

    st.caption(f"Menunjukkan **{len(filtered_df)}** rekod hasil carian:")

    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Sumber', 'Tajuk / Produk', 'Tarikh']], 
            use_container_width=True,
            hide_index=True
        )
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Muat Turun Laporan (CSV)", data=csv_data, file_name="laporan_risikan.csv", mime="text/csv", use_container_width=True)
    else:
        st.info("Tiada rekod amaran makanan ditemui.")

# ==========================================
# TAB 2: PEMANTAUAN PRODUK VIRAL (MEDSOS)
# ==========================================
with tab2:
    st.subheader("📲 Risikan Makanan Viral")
    
    cat_filter = st.selectbox("Kategori Trend:", ["Semua Kategori", "Kopi / Minuman Kurus", "Snek & Gula-Gula Import", "Suplemen & Kesihatan"])
    
    viral_data = [
        {"Kategori": "Kopi / Minuman Kurus", "Nama Produk": "Kopi Detox Slim Import", "Platform": "TikTok / Shopee", "Status Risk": "🚨 Berisiko Tinggi", "Nota": "Syak Sibutramine"},
        {"Kategori": "Snek & Gula-Gula Import", "Nama Produk": "Candy Sour Chews", "Platform": "Facebook / TikTok", "Status Risk": "⚠️ Perlabelan", "Nota": "Tiada maklumat pengimport"},
        {"Kategori": "Suplemen & Kesihatan", "Nama Produk": "Jelly Collagen Overclaim", "Platform": "Instagram", "Status Risk": "🚨 Overclaim", "Nota": "Klaim merawat penyakit"}
    ]
    df_viral = pd.DataFrame(viral_data)
    
    if cat_filter != "Semua Kategori":
        df_viral = df_viral[df_viral['Kategori'] == cat_filter]
        
    st.dataframe(df_viral[['Nama Produk', 'Platform', 'Status Risk']], use_container_width=True, hide_index=True)

# ==========================================
# TAB 3: IMBASAN LABEL IMAGE (OCR AI)
# ==========================================
with tab3:
    st.subheader("📷 Imbasan Teks Label (OCR)")
    
    uploaded_file = st.file_uploader("Upload Gambar Label:", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar Label", use_container_width=True)
        
        with st.spinner("Mengekstrak teks..."):
            try:
                extracted_text = pytesseract.image_to_string(image)
                st.text_area("Teks Dikesan:", extracted_text, height=120)
                
                risk_keywords = ["sibutramine", "sildenafil", "steroid", "rhodamine", "aflatoxin"]
                found_risks = [word for word in risk_keywords if word.lower() in extracted_text.lower()]
                
                if found_risks:
                    st.error(f"🚨 **AMARAN:** Bahan Berisiko: {', '.join(found_risks)}")
                else:
                    st.success("✅ Tiada bahan berisiko utama dikesan.")
            except Exception:
                st.info("Modul OCR memerlukan persekitaran Tesseract Engine.")
