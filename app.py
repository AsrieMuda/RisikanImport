import streamlit as st
import pandas as pd
import feedparser
import requests
from PIL import Image

# Tetapan Muka Surat
st.set_page_config(
    page_title="Pusat Risikan Import PKKM",
    page_icon="🇲🇾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# STYLESHEET REKA BENTUK PORTAL RASMI BKKM
st.markdown("""
    <style>
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 1.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        .top-utility-bar {
            background-color: #2c3036;
            color: #ffffff;
            padding: 5px 15px;
            font-size: 11px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 4px 4px 0 0;
        }
        .bkkm-header {
            background-color: #ffffff;
            padding: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-left: 1px solid #e0e0e0;
            border-right: 1px solid #e0e0e0;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        }
        .header-left { display: flex; align-items: center; }
        .jata-img { width: 75px; margin-right: 15px; }
        .header-text-sub { font-size: 11px; color: #555; margin: 0; font-weight: 500; }
        .header-text-main { font-size: 16px; color: #111; margin: 2px 0; font-weight: 800; font-family: sans-serif; }
        .header-text-kkm { font-size: 12px; color: #003B5C; margin: 0; font-weight: 700; }
        .header-right-icons { display: flex; gap: 12px; align-items: center; }
        .icon-box { text-align: center; font-size: 10px; color: #003B5C; font-weight: bold; }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #003B5C !important;
            padding: 2px 10px !important;
            border-radius: 0 0 4px 4px !important;
            gap: 5px;
        }
        .stTabs [data-baseweb="tab"] { color: #ffffff !important; font-weight: 600 !important; font-size: 13px !important; }
        .stTabs [aria-selected="true"] { background-color: #005689 !important; border-bottom: 3px solid #ffcc00 !important; }
        @media (max-width: 640px) {
            .bkkm-header { flex-direction: column; text-align: center; }
            .header-left { flex-direction: column; }
            .jata-img { margin-right: 0; margin-bottom: 8px; width: 60px; }
            .header-right-icons { margin-top: 10px; }
            .header-text-main { font-size: 14px; }
        }
    </style>
""", unsafe_allow_html=True)

# 1. TOP UTILITY BAR
st.markdown("""
    <div class="top-utility-bar">
        <span>Portal Rasmi Unit Risikan Import PKKM</span>
        <span>Bahasa: <b>MY 🇲🇾</b> | EN 🇬🇧</span>
    </div>
""", unsafe_allow_html=True)

# 2. HEADER BKKM
st.markdown("""
    <div class="bkkm-header">
        <div class="header-left">
            <img class="jata-img" src="https://upload.wikimedia.org/wikipedia/commons/2/26/Coat_of_arms_of_Malaysia.svg">
            <div>
                <p class="header-text-sub">Laman Web Rasmi OSINT Risikan</p>
                <h2 class="header-text-main">PROGRAM KESELAMATAN DAN KUALITI MAKANAN</h2>
                <p class="header-text-kkm">KEMENTERIAN KESIHATAN MALAYSIA</p>
            </div>
        </div>
        <div class="header-right-icons">
            <div class="icon-box">🚢<br>FoSIM Import</div>
            <div class="icon-box">📋<br>Perundangan</div>
            <div class="icon-box">🛡️<br>Risikan</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# FUNGSI INTEGRASI API OPEN FOOD FACTS (DISERAP DARI FOOD-SEARCH)
def search_global_openfoodfacts(query_text):
    try:
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query_text}&search_simple=1&action=process&json=1&page_size=10"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            result_list = []
            for p in products:
                result_list.append({
                    "Nama Produk": p.get('product_name', 'Tiada Nama'),
                    "Jenama / Pengilang": p.get('brands', 'Tiada Jenama'),
                    "Negara Asal": p.get('countries', 'Tiada Maklumat'),
                    "Barcode (EAN)": p.get('code', '-'),
                    "Ramuan Detected": p.get('ingredients_text', 'Tiada Teks Ramuan')
                })
            return pd.DataFrame(result_list)
    except Exception as e:
        print(f"Ralat API: {e}")
    return pd.DataFrame()

# 3. NAVIGASI TAB
tab1, tab2, tab3 = st.tabs([
    "🏠 UTAMA (Food Search)", 
    "📲 RISIKAN VIRAL", 
    "📷 OCR LABEL AI"
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
            except Exception:
                pass
        return pd.DataFrame(alert_list) if alert_list else pd.DataFrame(columns=["Sumber", "Tajuk / Produk", "Tarikh", "Pautan Laporan", "Ringkasan"])

    df_alerts = load_food_alerts()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # PILIHAN MOD CARIAN
    search_mode = st.radio(
        "Mod Carian Risikan:",
        ["🚨 Rekod Alert Antarabangsa (FDA/RASFF)", "📦 Carian Barcode & Produk Global (OpenFoodFacts)"],
        horizontal=True
    )

    if "Alert Antarabangsa" in search_mode:
        st.metric("Jumlah Rekod Alert Aktif", len(df_alerts))
        st.subheader("🔍 Carian Amaran Makanan Import")
        
        sumber_list = ["Semua Sumber"] + list(df_alerts['Sumber'].unique()) if not df_alerts.empty else ["Semua Sumber"]
        selected_source = st.selectbox("Tapis Portal Sumber:", sumber_list)
        query = st.text_input("Kata Kunci Carian (cth: Salmonella, Kopi, Brand):", "")

        filtered_df = df_alerts.copy()
        if selected_source != "Semua Sumber":
            filtered_df = filtered_df[filtered_df['Sumber'] == selected_source]
        if query and not filtered_df.empty:
            filtered_df = filtered_df[
                filtered_df['Tajuk / Produk'].str.contains(query, case=False, na=False) |
                filtered_df['Ringkasan'].str.contains(query, case=False, na=False)
            ]

        st.caption(f"Menunjukkan **{len(filtered_df)}** rekod maklumat dikesan:")

        if not filtered_df.empty:
            st.dataframe(filtered_df[['Sumber', 'Tajuk / Produk', 'Tarikh']], use_container_width=True, hide_index=True)
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("📄 Muat Turun Laporan Risikan (CSV)", data=csv_data, file_name="laporan_risikan_bkkm.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("Tiada rekod amaran makanan ditemui.")

    else:
        st.subheader("📦 Carian Barcode & Pangkalan Data Produk Global")
        global_query = st.text_input("Masukkan Nombor Barcode atau Nama Produk Global (cth: 8992741911110 / Samyang):", "")
        
        if global_query:
            with st.spinner("Menarik data produk dari Open Food Facts..."):
                df_global = search_global_openfoodfacts(global_query)
                if not df_global.empty:
                    st.success(f"Dikesan **{len(df_global)}** rekod produk global:")
                    st.dataframe(df_global, use_container_width=True, hide_index=True)
                else:
                    st.warning("Tiada produk ditemui untuk barcode/nama tersebut.")

# ==========================================
# TAB 2: PEMANTAUAN PRODUK VIRAL & OSINT
# ==========================================
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📲 Risikan Makanan Viral E-Dagang & Media Sosial")
    
    cat_filter = st.selectbox("Kategori Trend:", ["Semua Kategori", "Kopi / Minuman Kurus", "Snek & Gula-Gula Import", "Suplemen & Kesihatan"])
    
    viral_data = [
        {
            "Nama Produk": "Kopi Detox Slim Import",
            "Platform": "TikTok / Shopee",
            "Status Risk": "🚨 Berisiko Tinggi",
            "Isu / Pelanggaran": "Syak Bahan Terlarang (Sibutramine) & Overclaim",
            "Pautan Produk": "https://shopee.com.my",
            "SOP Tindakan": "TUL di Pintu Masuk / Semak FoSIM"
        },
        {
            "Nama Produk": "Candy Sour Chews",
            "Platform": "Facebook / TikTok",
            "Status Risk": "⚠️ Perlabelan",
            "Isu / Pelanggaran": "Tiada Sebutan Bahasa Melayu/Inggeris & Pengimport Unregistered",
            "Pautan Produk": "https://tiktok.com",
            "SOP Tindakan": "Keluarkan Notis Penahanan / Saman Label"
        },
        {
            "Nama Produk": "Jelly Collagen Overclaim",
            "Platform": "Instagram",
            "Status Risk": "🚨 Overclaim",
            "Isu / Pelanggaran": "Klaim Merawat Kencing Manis/Darah Tinggi",
            "Pautan Produk": "https://instagram.com",
            "SOP Tindakan": "Aduan Take-Down SKMM / Tindakan Seksyen 17"
        }
    ]
    df_viral = pd.DataFrame(viral_data)
    
    if cat_filter != "Semua Kategori":
        df_viral = df_viral[df_viral['Nama Produk'].str.contains(cat_filter, case=False, na=False)]
        
    st.dataframe(
        df_viral,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Pautan Produk": st.column_config.LinkColumn("Pautan Risikan (Link)")
        }
    )

    with st.expander("🛡️ Panduan Risikan Senyap (Undercover OSINT) & Pengumpulan Bukti"):
        st.markdown("""
        * **1. Sembunyikan Alamat IP:** Pastikan VPN diaktifkan sebelum menekan pautan produk.
        * **2. Simpan Bukti Digital:** Gunakan [Archive.ph](https://archive.ph) untuk menyimpan salinan asal halaman produk sebelum dipadam penjual.
        * **3. Tangkapan Skrin:** Simpan gambar halaman penuh (*full-page screenshot*) bersama tarikh dan masa.
        * **4. Akaun Risikan Khas:** Gunakan akaun *Sock Puppet* (bukan e-mel rasmi KKM) apabila melayari platform e-dagang.
        """)

# ==========================================
# TAB 3: IMBASAN LABEL IMAGE (AUTO-OCR)
# ==========================================
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📷 Imbasan Teks Label & Ramuan (Auto-OCR)")
    st.caption("Muat naik gambar label produk import. Sistem akan mengekstrak teks ramuan dan mengesan bahan berisiko secara automatik.")
    
    uploaded_file = st.file_uploader("Muat Naik / Tangkap Gambar Label Produk:", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar Label Diimbas", use_container_width=True)
        
        with st.spinner("🤖 AI sedang membaca teks pada gambar label..."):
            try:
                import easyocr
                import numpy as np
                
                reader = easyocr.Reader(['en', 'ms'], gpu=False)
                image_np = np.array(image)
                results = reader.readtext(image_np, detail=0)
                extracted_text = " ".join(results)
                
                st.divider()
                st.write("📝 **Teks Ramuan Yang Berjaya Dibaca:**")
                st.text_area("Hasil Teks Dikesan:", extracted_text, height=120)
                
                risk_keywords = [
                    "sibutramine", "sildenafil", "steroid", "rhodamine", 
                    "aflatoxin", "ethylene oxide", "pork", "lard", "pork derivative"
                ]
                
                found_risks = [word for word in risk_keywords if word.lower() in extracted_text.lower()]
                
                if found_risks:
                    st.error(f"🚨 **AMARAN RISIKAN:** Bahan/Kata Kunci Berisiko Dikesan: {', '.join(found_risks)}")
                    st.warning("📌 *Tindakan Pegawai:* Tahan kemasukan konsaimen dan buat persampelan untuk analisis makmal (TUL).")
                else:
                    st.success("✅ **STATUS PERTAMA:** Tiada bahan terlarang utama dikesan secara automatik pada teks label ini.")
                    
            except Exception as e:
                st.error(f"Gagal memproses gambar: {e}")
