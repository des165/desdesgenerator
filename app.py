import streamlit as st
from PIL import Image

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="Ultimate AI Affiliate & Character Gen",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Ultimate AI Content & Character Generator")
st.markdown("### **Rahasia** Mengunci Karakter & Membuat Konten Affiliate Konsisten!")
st.markdown("---")

# 2. Form Input User
with st.form("generator_form"):
    st.subheader("⚙️ 1. Pilih Mode Pembuatan")
    
    # Kategori Utama
    mode_aplikasi = st.selectbox(
        "Pilih Fitur yang Ingin Digunakan:",
        ["Buat Konten Video Affiliate (10 Detik)", "Buat Character Reference Sheet (Multi-Angle Model)"]
    )
    
    st.markdown("---")
    
    # LOGIKA DINAMIS DI DALAM FORM
    if mode_aplikasi == "Buat Konten Video Affiliate (10 Detik)":
        st.subheader("📹 Pengaturan Gaya Video Affiliate")
        gaya_konten = st.radio("Gaya Tampilan Visual:", ["Hanya Tangan & Produk (Tanpa Muka)", "Tampilkan Wajah Model (Face Lock)"])
        gaya_video = st.selectbox(
            "Pilih Alur & Format Gaya Video:",
            ["POV", "One-take UGC", "Unboxing", "Review", "Before-After", "Soft Selling", "Story Selling", "Podcast"]
        )
        
        st.subheader("📋 Aset & Detail Produk")
        foto_produk = st.file_uploader("📸 Foto Produk Utama (PROD_REF):", type=["jpg", "jpeg", "png"])
        foto_model_ref = st.file_uploader("💃 Foto Referensi Pencahayaan/Latar (MODEL_REF):", type=["jpg", "jpeg", "png"])
        foto_user = st.file_uploader("👤 Foto Wajah Anda Sendiri (USER_REF):", type=["jpg", "jpeg", "png"]) if gaya_konten == "Tampilkan Wajah Model (Face Lock)" else None
        
        nama_produk = st.text_input("Nama Produk:", placeholder="Contoh: GUMORA Herbal Oil")
        target_market = st.selectbox("Target Market:", ["Ibu Muda", "Bapak Muda", "Orang Tua"])
        masalah_utama = st.text_input("Masalah Utama:", value="Anak tumpahin susu di meja")
        
    else:
        st.subheader("🎨 Pengaturan Character Reference Sheet")
        foto_target = st.file_uploader("👤 Upload Foto Wajah/Model Sumber:", type=["jpg", "jpeg", "png"])
        
        # Fitur modifikasi sesuai tips request Anda
        gaya_visual = st.selectbox("Pilih Gaya Visual Model:", ["Realistic/Photorealistic", "Anime Style", "Chibi Style", "3D Pixar Style", "Cinematic Studio Style"])
        jumlah_views = st.selectbox("Jumlah Sudut Pandang (Views):", [
            "4 views: front view, side view (left profile), back view, and 3/4 view",
            "3 views: front view, side view, and back view",
            "2 views: front view and side view"
        ])
        tambah_ekspresi = st.checkbox("Tambah Lembar Ekspresi Wajah Beda-beda (Expression Sheet)")

    submit_button = st.form_submit_button(label="Generate Master Prompt 🚀")

# 3. Logika Output setelah Tombol Diklik
if submit_button:
    # --- JALUR 1: VIDEO AFFILIATE ---
    if mode_aplikasi == "Buat Konten Video Affiliate (10 Detik)":
        if not nama_produk:
            st.error("Silakan isi nama produk terlebih dahulu!")
        else:
            st.success("Konsep Video & Prompt Berhasil Dibuat!")
            target_en = "young mother" if target_market == "Ibu Muda" else "young father" if target_market == "Bapak Muda" else "parent"
            identity_rules = "Strict No-Face Rule: Do NOT show the face." if gaya_konten == "Hanya Tangan & Produk (Tanpa Muka)" else "Character Face Lock: Use features from USER_REF."
            
            master_prompt = (
                f"Task: Advanced Image-to-Image {gaya_video} Transformation (9:16 vertical 3-panel storyboard grid layout).\n"
                f"References: PROD_REF, MODEL_REF.\n"
                f"Rules: {identity_rules}\n"
                f"- Panel 1 (Hook): POV shot showing mess from {masalah_utama.lower()}.\n"
                f"- Panel 2 (Demo): Hands using {nama_produk} to clean the mess dynamically.\n"
                f"- Panel 3 (CTA): Close-up aesthetic shot of {nama_produk} standing elegantly."
            )
            st.subheader("🤖 Master Prompt Video AI (Veo / Omni)")
            st.code(master_prompt, language="text")
            # --- TAMBAHAN UNTUK VISUAL GRID STORYBOARD (9:16) ---
st.markdown("---")
st.markdown("### 🖼️ Visual Storyboard Layout (9:16)")

# Membuat 3 kolom berdampingan untuk panel storyboard
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🎬 Panel 1: Hook")
    st.warning("Visualisasikan **masalah utama** secara instan di sini.")
    # Kotak abu-abu placeholder rasio 9:16
    st.image("https://placehold.co/450x800/262730/ffffff?text=Panel+1%0AHook+(9:16)", use_container_width=True)

with col2:
    st.markdown("#### 🖐️ Panel 2: Demo")
    st.info("Tunjukkan area **tangan & produk** sedang beraksi.")
    st.image("https://placehold.co/450x800/262730/ffffff?text=Panel+2%0ADemo+(9:16)", use_container_width=True)

with col3:
    st.markdown("#### 🛍️ Panel 3: CTA")
    st.success("Tutup dengan shot **estetik produk** + link keranjang.")
    st.image("https://placehold.co/450x800/262730/ffffff?text=Panel+3%0ACTA+(9:16)", use_container_width=True)
            
    # Download button untuk teks video
        st.download_button(
            label="📄 Save Video Prompt (.txt)",
            data=master_prompt,
            file_name="prompt_video_affiliate.txt",
            mime="text/plain"
        )

    # --- JALUR 2: CHARACTER REFERENCE SHEET ---
    else:
        if not foto_target:
            st.error("Silakan unggah foto wajah/model sumber terlebih dahulu!")
        else:
            st.success("Master Prompt Character Turnaround Sheet Berhasil Dibuat!")
            
            # Menyusun prompt berdasarkan input kustom dari user
            ekspresi_text = " Include a small expression sheet with 3 facial expressions." if tambah_ekspresi else ""
            
            char_prompt = (
                f"Visual Style: {gaya_visual}. "
                f"Show the same character in multiple consistent views: {jumlah_views}, "
                f"all in one single image arranged in a grid layout on a plain neutral background. "
                f"Keep the face, hairstyle, outfit, proportions, and color palette exactly consistent across all views. "
                f"Full body, T-pose or neutral standing pose, clean lighting, no shadows overlapping between views, "
                f"character sheet / turnaround style, high detail.{ekspresi_text}"
            
            
            st.subheader("🤖 Master Prompt Character Reference Sheet (Gemini / Imagen 3)")
            st.info("💡 **Rahasia Sukses:** Salin prompt di bawah ini ke Gemini/Google AI Studio bersamaan dengan foto wajah yang Anda unggah tadi.")
            st.code(char_prompt, language="text")
            
            # Download button untuk karakter sheet
            st.download_button(
                label="💾 Save Character Prompt to Text File (.txt)",
                data=char_prompt,
                file_name=f"prompt_char_sheet_{gaya_visual.lower().split()[0]}.txt",
                mime="text/plain"
            )
