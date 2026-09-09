# ==========================================
# TAB 3: IMBASAN LABEL IMAGE (AUTO-OCR)
# ==========================================
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📷 Imbasan Teks Label & Ramuan (Auto-OCR)")
    st.caption("Muat naik gambar label produk import secara terus. Sistem akan membaca teks dan mengesan bahan berisiko secara automatik.")
    
    # Membenarkan muat naik gambar terus dari telefon/komputer
    uploaded_file = st.file_uploader("Muat Naik / Tangkap Gambar Label Produk:", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar Label Diimbas", use_container_width=True)
        
        with st.spinner("🤖 AI sedang membaca teks pada gambar label..."):
            try:
                import easyocr
                import numpy as np
                
                # Inisialisasi pembaca OCR (Sokongan Bahasa Inggeris & Melayu)
                reader = easyocr.Reader(['en', 'ms'], gpu=False)
                
                # Tukar gambar kepada format array
                image_np = np.array(image)
                results = reader.readtext(image_np, detail=0)
                
                # Gabungkan hasil teks
                extracted_text = " ".join(results)
                
                st.divider()
                st.write("📝 **Teks Ramuan Yang Berjaya Dibaca:**")
                st.text_area("Hasil Teks Dikesan:", extracted_text, height=120)
                
                # Semakan Kata Kunci Berisiko / Bahan Terlarang
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
