import base64
import json
import streamlit as st
import anthropic

# ==============================================================================
# KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(page_title="desdes media", page_icon="🎬", layout="wide")

# ==============================================================================
# SETUP CLIENT ANTHROPIC
# ==============================================================================
# API key diambil dari .streamlit/secrets.toml (key: ANTHROPIC_API_KEY)
# atau dari environment variable ANTHROPIC_API_KEY.
# Cara isi secrets.toml:
#   ANTHROPIC_API_KEY = "sk-ant-xxxxxxxx"
def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", None) if hasattr(st, "secrets") else None
    if not api_key:
        import os
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)


def encode_image(uploaded_file):
    """Encode file upload Streamlit jadi base64 + media_type buat dikirim ke Claude."""
    media_type = uploaded_file.type or "image/jpeg"
    b64 = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
    return b64, media_type


# ==============================================================================
# FUNGSI GENERATOR - MENU 1: VIDEO JUALAN
# ==============================================================================
def generate_konten_video(nama_produk, masalah, usia_text, gaya_visual, alur_video,
                           foto_model=None, foto_produk=None):
    """Panggil Claude buat generate brief produksi video jualan lengkap (JSON)."""
    client = get_client()
    if client is None:
        return None, "API key belum diatur. Isi ANTHROPIC_API_KEY di secrets.toml dulu ya."

    system_prompt = (
        "Kamu adalah asisten pembuat brief produksi video jualan pendek untuk media sosial "
        "(TikTok/Reels/Shorts) berbahasa Indonesia yang santai dan menarik, setara brief "
        "videografer profesional. "
        "Balas HANYA dalam format JSON valid, tanpa teks lain, tanpa markdown code fence. "
        "Kalau ada foto model/produk yang dilampirkan, deskripsikan ciri asli dari foto itu "
        "(jangan mengarang wajah/warna/bentuk yang beda dari foto). "
        "Kalau gaya visual 'Hanya Tangan & Produk (Tanpa Muka)', jangan sebutkan wajah model "
        "sama sekali, fokus ke tangan dan produk saja. "
        "Gunakan kata kunci utama (nama produk) secara konsisten di narasi, voice_over, "
        "caption, dan thumbnail_desc supaya SEO-nya nyambung. "
        "Semua bagian harus singkat dan padat (maksimal 1-2 kalimat pendek per field)."
    )

    user_prompt = f"""
Buatkan brief konten dengan struktur JSON persis seperti ini:
{{
  "prompt_video": "perintah singkat untuk AI video generator, 1 kalimat",
  "narasi": "narasi/naskah video, singkat, pakai kata kunci nama produk",
  "voice_over": "teks voice over, kata kunci sama dengan narasi, singkat",
  "caption": "caption media sosial, singkat, ada 1 hashtag utama nama produk",
  "thumbnail_desc": "deskripsi visual thumbnail, singkat",
  "hashtag_utama": "#satuHashtagDariNamaProduk",
  "hashtag_seo": ["#tag1", "#tag2", "#tag3", "#tag4"],
  "detail_produksi": {{
    "model": "deskripsi singkat model: ciri fisik, ekspresi, outfit (kosongkan kalau gaya visual tanpa muka)",
    "produk": "deskripsi singkat produk: bentuk, warna, kemasan",
    "tempat": "lokasi/setting syuting yang cocok",
    "gerakan": "gerakan talent & kamera selama adegan",
    "angle_kamera": "sudut kamera (eye-level/low angle/high angle/dutch angle dll)",
    "zoom_kamera": "pergerakan zoom (static/slow zoom in/zoom out/push-in dll)",
    "visual_style": "gaya visual & warna (cinematic, warm tone, dsb)",
    "ugc_style_komersial": "arahan gaya UGC commercial: santai, otentik, kayak konten organik tapi tetap jualan",
    "identity_lock": "instruksi supaya wajah model & bentuk produk konsisten di setiap frame/adegan",
    "negative_prompt": "hal yang harus dihindari AI video (misal: wajah berubah, produk berubah bentuk, teks salah eja, tangan cacat, dll)"
  }},
  "variasi_konten": {{
    "mirroring": "1 kalimat arahan versi video di-mirror/flip biar lolos deteksi algoritma tanpa ganggu keterbacaan",
    "pegang_hp": "1 kalimat arahan versi POV model pegang HP sambil ngomong ke kamera (gaya UGC review)",
    "podcast": "1 kalimat arahan versi cuplikan gaya podcast: model ngobrol santai membahas produk seolah di podcast"
  }}
}}

Data produk:
- Nama Produk: {nama_produk}
- Masalah yang diselesaikan: {masalah}
- Target Umur Penonton: {usia_text}
- Gaya Visual: {gaya_visual}
- Alur & Format Video: {alur_video}
- Foto Model tersedia: {"Ya" if foto_model else "Tidak"}
- Foto Produk tersedia: {"Ya" if foto_produk else "Tidak"}
"""

    content = []
    if foto_model:
        b64, media_type = encode_image(foto_model)
        content.append({"type": "text", "text": "Foto Model:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}})
    if foto_produk:
        b64, media_type = encode_image(foto_produk)
        content.append({"type": "text", "text": "Foto Produk:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}})
    content.append({"type": "text", "text": user_prompt})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1800,
            system=system_prompt,
            messages=[{"role": "user", "content": content}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)
        return data, None
    except json.JSONDecodeError:
        return None, "Gagal membaca hasil dari AI (format bukan JSON). Coba klik tombolnya lagi."
    except Exception as e:
        return None, f"Gagal menghubungi AI: {e}"


# ==============================================================================
# FUNGSI GENERATOR - MENU 2: EDIT FOTO
# ==============================================================================
def generate_prompt_gaya(foto_asli, gaya):
    """Panggil Claude (vision) buat bikin prompt ubah gaya foto berdasarkan foto asli."""
    client = get_client()
    if client is None:
        return None, "API key belum diatur. Isi ANTHROPIC_API_KEY di secrets.toml dulu ya."

    b64, media_type = encode_image(foto_asli)
    system_prompt = (
        "Kamu asisten yang membuat instruksi edit foto untuk AI image editor. "
        "Lihat foto yang diberikan, lalu buat SATU kalimat perintah singkat berbahasa "
        "Indonesia yang menyebutkan ciri penting orang/objek di foto (pose, ekspresi, "
        "warna baju/latar) supaya hasil edit tetap mirip orangnya, hanya gayanya yang berubah."
    )
    user_prompt = f"Foto ini mau diubah ke gaya: {gaya}. Buatkan perintah editnya."

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                    {"type": "text", "text": user_prompt},
                ],
            }],
        )
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        return text, None
    except Exception as e:
        return None, f"Gagal menghubungi AI: {e}"


def generate_prompt_swap(sumber, target, tujuan):
    """Panggil Claude (vision) buat bikin prompt tukar wajah/baju berdasarkan 2 foto."""
    client = get_client()
    if client is None:
        return None, "API key belum diatur. Isi ANTHROPIC_API_KEY di secrets.toml dulu ya."

    b64_sumber, media_sumber = encode_image(sumber)
    b64_target, media_target = encode_image(target)

    system_prompt = (
        "Kamu asisten yang membuat instruksi untuk AI image editor. "
        "Lihat kedua foto (Sumber dan Target), lalu buat SATU kalimat perintah singkat "
        "berbahasa Indonesia yang menyebutkan ciri penting tiap foto (baju/wajah, pose, "
        "latar) supaya hasil editnya tepat sasaran dan natural."
    )
    if tujuan == "Tukar Baju (Virtual Try-On)":
        user_prompt = "Pasangkan baju dari Foto Sumber ke orang di Foto Target. Buatkan perintah editnya."
    else:
        user_prompt = "Tukar wajah dari Foto Sumber ke orang di Foto Target. Buatkan perintah editnya."

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Foto Sumber:"},
                    {"type": "image", "source": {"type": "base64", "media_type": media_sumber, "data": b64_sumber}},
                    {"type": "text", "text": "Foto Target:"},
                    {"type": "image", "source": {"type": "base64", "media_type": media_target, "data": b64_target}},
                    {"type": "text", "text": user_prompt},
                ],
            }],
        )
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        return text, None
    except Exception as e:
        return None, f"Gagal menghubungi AI: {e}"


# ==============================================================================
# SIDEBAR
# ==============================================================================
st.sidebar.title("🎬 desdes media")
st.sidebar.markdown("**Aplikasi AI untuk Pemula**")
st.sidebar.markdown("---")
pilihan = st.sidebar.radio("Pilih mau buat apa hari ini:", ["🎥 Bikin Video Jualan", "🎭 Edit Foto & Ganti Baju"])

st.sidebar.markdown("---")
if get_client() is None:
    st.sidebar.warning("⚠️ API key belum diatur. Lihat CARA_SETUP.md")
else:
    st.sidebar.caption("✅ Terhubung ke AI")

# ==============================================================================
# MENU 1: BIKIN VIDEO JUALAN
# ==============================================================================
if pilihan == "🎥 Bikin Video Jualan":
    st.title("🎥 Bikin Video Jualan")
    st.write("Isi data di bawah, nanti AI kami yang buatkan naskah dan arahannya!")

    st.subheader("1. Gaya & Format Video")
    col_gaya, col_alur = st.columns(2)
    with col_gaya:
        gaya_visual = st.radio(
            "Gaya Tampilan Visual:",
            ["Hanya Tangan & Produk (Tanpa Muka)", "Tampilkan Wajah Model (Face Lock)"],
            key="gaya_visual",
        )
    with col_alur:
        alur_video = st.selectbox(
            "Pilih Alur & Format Gaya Video:",
            ["POV", "Cinematic Product Showcase", "Testimoni Santai", "Unboxing", "Before-After"],
            key="alur_video",
        )

    st.markdown("---")
    st.subheader("2. Masukkan Bahan")
    col1, col2 = st.columns(2)

    with col1:
        foto_model = None
        if gaya_visual == "Tampilkan Wajah Model (Face Lock)":
            foto_model = st.file_uploader(
                "Upload Foto Model (wajib untuk Face Lock):",
                type=["png", "jpg", "jpeg"],
                key="foto_model",
            )
            if foto_model:
                st.image(foto_model, width=200, caption="Foto Model Siap")
        else:
            st.caption("Gaya visual 'Hanya Tangan & Produk' dipilih — upload foto model tidak diperlukan.")

        foto_produk = st.file_uploader(
            "Upload Foto Produk:",
            type=["png", "jpg", "jpeg"],
            key="foto_produk",
        )
        if foto_produk:
            st.image(foto_produk, width=200, caption="Foto Produk Siap")

    with col2:
        st.subheader("3. Detail Produk")
        nama_produk = st.text_input("Nama Produk:", key="nama_produk")
        masalah = st.text_area("Apa masalah yang mau diselesaikan?", key="masalah")
        usia = st.slider("Target Umur Penonton:", 18, 60, (24, 40), key="usia")

    st.markdown("---")

    if st.button("🚀 Buat Konten Sekarang"):
        error_list = []
        if not nama_produk:
            error_list.append("Nama Produk belum diisi")
        if not masalah:
            error_list.append("Masalah yang diselesaikan belum diisi")
        if gaya_visual == "Tampilkan Wajah Model (Face Lock)" and not foto_model:
            error_list.append("Gaya visual Face Lock dipilih, tapi Foto Model belum diupload")

        if error_list:
            st.error("Ada yang belum lengkap: " + ", ".join(error_list))
        else:
            usia_text = f"{usia[0]}-{usia[1]} tahun"

            with st.spinner("AI lagi mikir naskah, narasi, sama hashtag-nya..."):
                data, err = generate_konten_video(
                    nama_produk, masalah, usia_text, gaya_visual, alur_video,
                    foto_model, foto_produk
                )

            if err:
                st.error(err)
            else:
                st.success("Konten berhasil dibuat!")
                st.write("Tinggal salin masing-masing bagian di bawah ini:")

                st.markdown("**🎬 Prompt Video**")
                st.code(data.get("prompt_video", ""), language="text")

                st.markdown("**📝 Narasi**")
                st.code(data.get("narasi", ""), language="text")

                st.markdown("**🎙️ Voice Over**")
                st.code(data.get("voice_over", ""), language="text")

                st.markdown("**💬 Caption**")
                st.code(data.get("caption", ""), language="text")

                st.markdown("**🖼️ Deskripsi Thumbnail**")
                st.code(data.get("thumbnail_desc", ""), language="text")

                hashtag_utama = data.get("hashtag_utama", "")
                hashtag_seo = data.get("hashtag_seo", [])
                st.markdown("**#️⃣ Hashtag**")
                st.code((hashtag_utama + " " + " ".join(hashtag_seo)).strip(), language="text")

                st.markdown("---")
                st.subheader("🎬 Detail Produksi")
                dp = data.get("detail_produksi", {})
                label_dp = {
                    "model": "👤 Model",
                    "produk": "📦 Produk",
                    "tempat": "📍 Tempat",
                    "gerakan": "🏃 Gerakan",
                    "angle_kamera": "📐 Angle Kamera",
                    "zoom_kamera": "🔍 Zoom Kamera",
                    "visual_style": "🎨 Visual Style",
                    "ugc_style_komersial": "📱 UGC Style Komersial",
                    "identity_lock": "🔒 Identity Lock",
                    "negative_prompt": "🚫 Negative Prompt",
                }
                for field, label in label_dp.items():
                    st.markdown(f"**{label}**")
                    st.code(dp.get(field, ""), language="text")

                st.markdown("---")
                st.subheader("🎞️ Variasi Konten Tambahan")
                vk = data.get("variasi_konten", {})
                label_vk = {
                    "mirroring": "🪞 Versi Mirroring",
                    "pegang_hp": "📱 Versi Pegang HP (POV Review)",
                    "podcast": "🎙️ Versi Gaya Podcast",
                }
                for field, label in label_vk.items():
                    st.markdown(f"**{label}**")
                    st.code(vk.get(field, ""), language="text")

                if not foto_produk:
                    st.warning("Tips: Upload foto produk juga supaya deskripsi produk & identity lock lebih akurat sesuai foto asli.")

# ==============================================================================
# MENU 2: EDIT FOTO & GANTI BAJU
# ==============================================================================
elif pilihan == "🎭 Edit Foto & Ganti Baju":
    st.title("🎭 Edit Foto & Ganti Baju")
    st.write("Pilih alat yang kamu butuhin di bawah ini:")

    fitur = st.selectbox("Apa yang mau kamu lakukan?", ["Ubah Gaya Foto", "Tukar Wajah atau Baju"])

    if fitur == "Ubah Gaya Foto":
        foto_asli = st.file_uploader("Upload Foto:", type=["png", "jpg", "jpeg"], key="foto_asli")
        if foto_asli:
            st.image(foto_asli, width=300)
        gaya = st.selectbox("Mau diubah jadi gaya apa?", ["Foto Profesional", "Kartun", "Gaya Mewah"])

        if st.button("Proses Foto"):
            if not foto_asli:
                st.error("Upload foto dulu ya sebelum diproses!")
            else:
                with st.spinner("AI lagi lihat fotonya dan bikin perintahnya..."):
                    prompt_gaya, err = generate_prompt_gaya(foto_asli, gaya)

                if err:
                    st.error(err)
                else:
                    st.success("Teks perintah sudah siap!")
                    st.code(prompt_gaya, language="text")

    else:
        c1, c2 = st.columns(2)
        with c1:
            sumber = st.file_uploader("Foto Sumber (Ambil baju/wajah dari sini):", type=["png", "jpg", "jpeg"], key="sumber")
            if sumber:
                st.image(sumber, width=200)
        with c2:
            target = st.file_uploader("Foto Target (Mau dipasang ke orang ini):", type=["png", "jpg", "jpeg"], key="target")
            if target:
                st.image(target, width=200)

        tujuan = st.selectbox("Mau pindahin apa?", ["Tukar Baju (Virtual Try-On)", "Tukar Wajah"])

        if st.button("Pasang Sekarang"):
            if not sumber or not target:
                st.error("Upload Foto Sumber dan Foto Target dulu ya, dua-duanya wajib!")
            else:
                with st.spinner("AI lagi lihat kedua fotonya dan bikin perintahnya..."):
                    prompt_swap, err = generate_prompt_swap(sumber, target, tujuan)

                if err:
                    st.error(err)
                else:
                    st.success("Teks perintah untuk AI sudah siap!")
                    st.code(prompt_swap, language="text")

# ==============================================================================
# PENGATURAN TAMBAHAN
# ==============================================================================
with st.expander("⚙️ Pengaturan Tambahan (Opsional)"):
    st.write("Kalau kamu baru belajar, lewati saja bagian ini.")
    st.slider("Tingkat Detail", 1, 10, 5, key="tingkat_detail")
