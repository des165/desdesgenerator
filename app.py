import streamlit as st

# 1. ATURAN HALAMAN UTAMA (Wajib ditaruh paling atas)
st.set_page_config(
    page_title="AI Prompt Generator & Visual Storyboard",
    page_icon="🚀",
    layout="wide"
)

# Judul Utama Aplikasi
st.title("🚀 Master Prompt & Visual Storyboard Generator")
st.markdown("Aplikasi asisten AI untuk mempermudah pembuatan script iklan video dan referensi karakter model.")

# 2. MENU SIDEBAR (PILIHAN JALUR)
st.sidebar.header("⚙️ Pengaturan Fitur")
mode_aplikasi = st.sidebar.radio(
    "Pilih Fitur Aplikasi:",
    ["🎥 Video Affiliate", "👤 Character Reference Sheet"]
)

# --- JALUR 1: VIDEO AFFILIATE ---
if mode_aplikasi == "🎥 Video Affiliate":
    st.header("🎥 Video Affiliate Prompt Generator")
    
    # Grid input data video
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        nama_produk = st.text_input("📦 Nama Produk", placeholder="Contoh: Rak Sepatu Estetik Kayu, Serum Whitening BPOM...")
        masalah_utama = st.text_area("⚠️ Masalah Utama yang Ingin Diselesaikan", placeholder="Contoh: Sepatu berantakan bikin rumah sempit, kulit kusam susah putih...")
        gaya_video = st.selectbox(
            "🎬 Gaya Visual Video",
            ["Casual / Review Santai", "Aesthetic / Cinematic", "Unboxing & First Impression", "Drama Komedi / Storytelling"]
        )
        
    with right_col:
        # Unggah foto produk agar muncul di preview dan storyboard
        foto_produk = st.file_uploader("📸 Unggah Foto Produk Anda (Opsional)", type=["png", "jpg", "jpeg"])
        if foto_produk is not None:
            st.image(foto_produk, caption="Pratinjau Foto Produk Terunggah", use_container_width=True)

    # Tombol jalankan generator
    if st.button("Generate Master Prompt 🚀", type="primary"):
        if not nama_produk or not masalah_utama:
            st.warning("Silakan isi nama produk dan masalah utamanya terlebih dahulu!")
        else:
            # Menyusun draf teks prompt video
            master_prompt = (
                f"Create a high-converting short-form video ad script (TikTok/Reels) for the product: {nama_produk}.\n"
                f"Target Problem to address: {masalah_utama}.\n"
                f"Visual Style: {gaya_video}.\n\n"
                f"Structure the script into three parts:\n"
                f"1. HOOK (0-3s): Start with a dramatic representation of the problem.\n"
                f"2. DEMO (3-12s): Show hands using the product to solve the problem clearly.\n"
                f"3. CTA (12-15s): End with an aesthetic product shot and clear call-to-action to buy."
            )
            
            st.success("Master Prompt Video Affiliate Berhasil Dibuat!")
            
            # Tampilkan kotak teks kode prompt
            st.code(master_prompt, language="text")
            
            # Tombol download
            st.download_button(
                label="📄 Save Video Prompt (.txt)",
                data=master_prompt,
                file_name="prompt_video_affiliate.txt",
                mime="text/plain"
            )
            
            # --- TAMPILAN VISUAL GRID STORYBOARD (9:16) ---
            st.markdown("---")
            st.markdown("### 📊 Visual Storyboard Layout (Rasio 9:16)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🎬 Panel 1: Hook")
                st.warning(f"Tunjukkan visual masalah **'{masalah_utama}'** secara dramatis di 3 detik pertama.")
                st.image("https://placehold.co/450x800/262730/ffffff?text=Panel+1:+Hook+Masalah", use_container_width=True)
                
            with col2:
                st.markdown("#### 🖐️ Panel 2: Demo")
                st.info(f"Tunjukkan tangan sedang mendemonstrasikan fungsi **{nama_produk}**.")
                if foto_produk is not None:
                    st.image(foto_produk, caption="Visualisasi Menggunakan Produk Anda", use_container_width=True)
                else:
                    st.image("https://placehold.co/450x800/262730/ffffff?text=Panel+2:+Demo+Produk", use_container_width=True)
                    
            with col3:
                st.markdown("#### 🛍️ Panel 3: CTA")
                st.success("Shot estetik produk + ajakan klik link/tombol keranjang kuning.")
                if foto_produk is not None:
                    st.image(foto_produk, caption="Shot Akhir Produk Anda", use_container_width=True)
                else:
                    st.image("https://placehold.co/450x800/262730/ffffff?text=Panel+3:+CTA+Produk", use_container_width=True)

# --- JALUR 2: CHARACTER REFERENCE SHEET ---
else:
    st.header("👤 Character Reference Sheet Generator")
    
    # Grid input data karakter
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        gaya_visual = st.text_input("🎨 Gaya Visual Karakter", value="Anime Studio Ghibli style, soft lighting, vibrant colors")
        jumlah_views = st.selectbox(
            "📐 Jumlah Tampilan Sudut Pandang (Views)",
            [
                "3 views (front, side, back)",
                "4 views (front, 3/4 front, side, back)",
                "Turnaround sheet (front, side, back, detailed close-up)"
            ]
        )
        tambah_ekspresi = st.checkbox("Tambah lembar ekspresi wajah (3 ekspresi berbeda)", value=True)
        
    with right_col:
        # Menampilkan pengunggah foto model wajah
        foto_target = st.file_uploader("👤 Unggah Foto Wajah / Model Sumber", type=["png", "jpg", "jpeg"])
        if foto_target is not None:
            # FOTO MODEL AKAN LANGSUNG MUNCUL DI SINI SECARA OTOMATIS
            st.image(foto_target, caption="Foto Model Sumber Terunggah", use_container_width=True)

    # Tombol jalankan generator karakter
    if st.button("Generate Character Prompt 🚀", type="primary"):
        if not foto_target:
            st.error("Silakan unggah foto wajah/model sumber terlebih dahulu di kolom sebelah kanan!")
        else:
            st.success("Master Prompt Character Turnaround Sheet Berhasil Dibuat!")
            
            # Menyusun prompt berdasarkan input kustom dari user
            ekspresi_text = " Include a small expression sheet with 3 facial expressions." if tambah_ekspresi else ""
            
            char_prompt = (
                f"Create a character reference sheet based on the uploaded photo. "
                f"Visual Style: {gaya_visual}. "
                f"Show the same character in multiple consistent views: {jumlah_views}, "
                f"all in one single image arranged in a grid layout on a plain neutral background. "
                f"Keep the face, hairstyle, outfit, proportions, and color palette exactly consistent across all views. "
                f"Full body, T-pose or neutral standing pose, clean lighting, no shadows overlapping between views, "
                f"character sheet / turnaround style, high detail.{ekspresi_text}"
            )
            
            # Tampilkan kotak teks kode prompt karakter
            st.code(char_prompt, language="text")
            
            # Tombol download
            st.download_button(
                label="💾 Simpan Character Prompt (.txt)",
                data=char_prompt,
                file_name="prompt_character_sheet.txt",
                mime="text/plain"
            )
            
            # --- TAMPILAN PRATINJAU STRUKTUR LEMBAR KARAKTER ---
            st.markdown("---")
            st.markdown("### 📐 Pratinjau Struktur Lembar Karakter (Character Sheet)")
            
            char_cols = st.columns(3)
            with char_cols[0]:
                st.markdown("#### 👤 Model Sumber Anda")
                st.image(foto_target, caption="Model Acuan Utama", use_container_width=True)
            with char_cols[1]:
                st.markdown("#### 📐 Turnaround Pose")
                st.info(f"Karakter akan digambar ulang menggunakan gaya **{gaya_visual}** dalam pose {jumlah_views}.")
            with char_cols[2]:
                st.markdown("#### 🎭 Detail Ekspresi")
                if tambah_ekspresi:
                    st.success("Ditambahkan: 3 Varian ekspresi wajah pendukung (Gembira, Serius, Senyum).")
                else:
                    st.warning("Ekspresi wajah kustom dinonaktifkan.")
