import io
import streamlit as st
from PIL import Image

# ==============================================================================
# KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(page_title="desdes media - AI Affiliate Studio", page_icon="🎬", layout="wide")

KATA_HIPNOTIS = ["Bayangkan", "Rahasia", "Terbukti", "Instan", "Karena", "Dijamin", "Sekarang"]

# ==============================================================================
# SETUP CLIENT GEMINI (khusus untuk fitur TEKS, masih gratis)
# ==============================================================================
def get_client():
    try:
        from google import genai
    except ImportError:
        return None, "Library 'google-genai' belum terinstall. Cek requirements.txt."

    api_key = st.secrets.get("GEMINI_API_KEY", None) if hasattr(st, "secrets") else None
    if not api_key:
        import os
        api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, "API key belum diatur. Isi GEMINI_API_KEY di secrets.toml dulu ya."
    return genai.Client(api_key=api_key), None


def generate_text(prompt, images=None):
    """Panggil Gemini buat generate teks (masih gratis, no billing)."""
    client, err = get_client()
    if client is None:
        return None, err
    contents = list(images) if images else []
    contents.append(prompt)
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)
        return response.text, None
    except Exception as e:
        return None, f"Gagal generate teks: {e}"


def show_and_save(image, filename, key_prefix):
    st.image(image, width=350)
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    st.download_button("💾 Download gambar", data=buf.getvalue(), file_name=filename,
                        mime="image/png", key=f"dl_{key_prefix}")


def simpan_ke_galeri(image, label):
    st.session_state.setdefault("galeri_model", [])
    st.session_state["galeri_model"].append({"label": label, "image": image})
    st.success(f"Tersimpan ke galeri sebagai '{label}'!")


def prompt_dan_upload(prompt, key_prefix, catatan_foto=""):
    """
    Alur GRATIS untuk generate gambar:
    1. Tampilkan prompt siap-copy
    2. User paste manual ke Gemini App (gemini.google.com) — gratis, tanpa billing
    3. User upload balik hasil gambarnya di sini
    """
    st.markdown("### 📋 Langkah Generate Gambar (Gratis, tanpa billing)")
    st.write("**1.** Klik tombol di bawah untuk buka Gemini App di tab baru:")
    st.link_button("🔗 Buka Gemini App", "https://gemini.google.com")

    if catatan_foto:
        st.info(catatan_foto)

    st.write("**2.** Copy prompt di bawah ini (klik ikon copy di pojok kanan atas kotak), lalu paste ke Gemini App bareng foto yang diminta:")
    st.code(prompt, language="text")

    st.write("**3.** Setelah Gemini App selesai bikin gambarnya, download hasilnya, lalu upload di sini:")
    hasil_upload = st.file_uploader(
        "Upload hasil gambar dari Gemini App:",
        type=["png", "jpg", "jpeg"],
        key=f"upload_hasil_{key_prefix}",
    )
    if hasil_upload:
        return Image.open(hasil_upload)
    return None


# ==============================================================================
# SESSION STATE DEFAULTS
# ==============================================================================
for key, default in [
    ("galeri_model", []), ("model_final", None), ("foto_produk", None),
    ("deskripsi_produk", ""), ("narasi", ""), ("storyboard", None),
    ("video_concept", ""),
]:
    st.session_state.setdefault(key, default)

# ==============================================================================
# SIDEBAR
# ==============================================================================
st.sidebar.title("🎬 desdes media")
st.sidebar.caption("AI Affiliate Content Studio — pakai Gemini (gratis)")
st.sidebar.markdown("---")

client_check, err_check = get_client()
if client_check is None:
    st.sidebar.warning(f"⚠️ {err_check}")
else:
    st.sidebar.success("✅ Terhubung ke Gemini (fitur teks)")
st.sidebar.caption("💡 Fitur gambar pakai Gemini App manual (gratis, no billing)")

tahap = st.sidebar.radio("Pilih Tahap:", [
    "1️⃣ Character Sheet",
    "2️⃣ Image to Image (Ganti Wajah/Baju)",
    "3️⃣ Pilih Model Tersimpan",
    "4️⃣ Upload Produk",
    "5️⃣ Deskripsi Produk",
    "6️⃣ Narasi",
    "7️⃣ Pilihan Gaya Konten",
    "8️⃣ Generate Storyboard",
    "9️⃣ Konsep Prompt Video",
    "🔟 Generate Video (link)",
])

# ==============================================================================
# TAHAP 1: CHARACTER SHEET
# ==============================================================================
if tahap.startswith("1"):
    st.title("1️⃣ Buat Character Reference Sheet")
    st.write("Upload foto model, lalu ikuti langkah manual di bawah untuk bikin 1 lembar referensi karakter (beberapa pose & ekspresi) via Gemini App — gratis.")

    foto_model_mentah = st.file_uploader("Upload Foto Model:", type=["png", "jpg", "jpeg"], key="up_model_mentah")
    if foto_model_mentah:
        st.image(foto_model_mentah, width=250, caption="Foto Asli")

        prompt = (
            "Buatkan character reference sheet dari foto model yang saya lampirkan. "
            "Tampilkan dalam 1 lembar gambar: pose depan, pose samping kiri, pose samping kanan, "
            "ekspresi netral, dan ekspresi tersenyum — disusun rapi dalam grid. "
            "PENTING (Identity Lock): wajah, bentuk tubuh, warna kulit, dan ciri fisik harus 100% identik "
            "dengan foto asli, jangan mengubah wajah orangnya sama sekali. "
            "Latar belakang putih polos studio, pencahayaan merata, gaya foto referensi profesional."
        )

        hasil = prompt_dan_upload(
            prompt, "charsheet",
            catatan_foto="Di Gemini App, lampirkan Foto Model di atas sebelum paste prompt-nya."
        )
        if hasil:
            st.session_state["hasil_charsheet"] = hasil
            st.success("Character sheet berhasil diupload!")

    if st.session_state.get("hasil_charsheet"):
        st.markdown("---")
        st.subheader("Hasil Character Sheet")
        show_and_save(st.session_state["hasil_charsheet"], "character_sheet.png", "charsheet")
        if st.button("📥 Simpan ke Galeri Model"):
            simpan_ke_galeri(st.session_state["hasil_charsheet"], "Character Sheet")

# ==============================================================================
# TAHAP 2: IMAGE TO IMAGE
# ==============================================================================
elif tahap.startswith("2"):
    st.title("2️⃣ Image to Image — Ganti Wajah / Baju / Celana")
    st.write("Upload foto referensi (sumber yang mau diambil) dan foto model (yang mau diedit).")

    col1, col2 = st.columns(2)
    with col1:
        foto_referensi = st.file_uploader("Foto Referensi (sumber wajah/baju/celana):", type=["png", "jpg", "jpeg"], key="up_referensi")
        if foto_referensi:
            st.image(foto_referensi, width=220)
    with col2:
        st.write("Pilih Foto Model yang mau diedit:")
        sumber_model = st.radio("Sumber foto model:", ["Upload baru", "Dari Galeri Model"], key="sumber_model_i2i")
        foto_model_target = None
        if sumber_model == "Upload baru":
            foto_model_target = st.file_uploader("Upload Foto Model:", type=["png", "jpg", "jpeg"], key="up_model_i2i")
            if foto_model_target:
                foto_model_target = Image.open(foto_model_target)
        else:
            if st.session_state["galeri_model"]:
                labels = [g["label"] for g in st.session_state["galeri_model"]]
                pilih = st.selectbox("Pilih dari galeri:", labels, key="pilih_galeri_i2i")
                foto_model_target = next(g["image"] for g in st.session_state["galeri_model"] if g["label"] == pilih)
            else:
                st.info("Galeri masih kosong. Simpan character sheet dulu di Tahap 1, atau upload baru.")
        if foto_model_target:
            st.image(foto_model_target, width=220, caption="Foto Model Target")

    jenis_edit = st.multiselect("Mau ganti apa?", ["Wajah/Muka", "Baju", "Celana"], key="jenis_edit_i2i")

    if foto_referensi and foto_model_target and jenis_edit:
        bagian = ", ".join(jenis_edit)
        prompt = (
            f"Edit Foto Model berikut dengan mengambil {bagian} dari Foto Referensi yang saya lampirkan. "
            "Pertahankan identitas Foto Model tetap konsisten (wajah, bentuk tubuh, pose) kecuali bagian "
            f"yang diminta ({bagian}) yang diambil dari Foto Referensi. "
            "Hasil harus natural, pencahayaan menyatu, tanpa artefak aneh, resolusi tinggi."
        )
        hasil = prompt_dan_upload(
            prompt, "i2i",
            catatan_foto="Di Gemini App, lampirkan KEDUA foto (Foto Model + Foto Referensi) sebelum paste prompt-nya."
        )
        if hasil:
            st.session_state["hasil_i2i"] = hasil
            st.success("Hasil edit berhasil diupload!")
    else:
        st.warning("Lengkapi Foto Referensi, Foto Model, dan pilihan (wajah/baju/celana) dulu ya.")

    if st.session_state.get("hasil_i2i"):
        st.markdown("---")
        st.subheader("Hasil Edit")
        show_and_save(st.session_state["hasil_i2i"], "hasil_edit.png", "i2i")
        if st.button("📥 Simpan ke Galeri Model", key="simpan_i2i"):
            simpan_ke_galeri(st.session_state["hasil_i2i"], f"Hasil Edit ({', '.join(jenis_edit) if jenis_edit else 'edit'})")

# ==============================================================================
# TAHAP 3: PILIH MODEL TERSIMPAN
# ==============================================================================
elif tahap.startswith("3"):
    st.title("3️⃣ Pilih Model yang Dipakai")
    st.write("Pilih foto model final (dari Character Sheet atau hasil Image to Image) yang akan dipakai di storyboard nanti.")

    if not st.session_state["galeri_model"]:
        st.info("Galeri masih kosong. Balik ke Tahap 1 atau 2 dulu, simpan hasilnya ke galeri.")
    else:
        labels = [g["label"] for g in st.session_state["galeri_model"]]
        cols = st.columns(min(4, len(labels)))
        for i, g in enumerate(st.session_state["galeri_model"]):
            with cols[i % len(cols)]:
                st.image(g["image"], width=150, caption=g["label"])

        pilih = st.selectbox("Pilih model final:", labels, key="pilih_model_final")
        if st.button("✅ Gunakan Model Ini"):
            st.session_state["model_final"] = next(g["image"] for g in st.session_state["galeri_model"] if g["label"] == pilih)
            st.success(f"Model '{pilih}' dipakai untuk tahap selanjutnya!")

    if st.session_state["model_final"] is not None:
        st.markdown("---")
        st.write("**Model yang sedang aktif dipakai:**")
        st.image(st.session_state["model_final"], width=200)

# ==============================================================================
# TAHAP 4: UPLOAD PRODUK
# ==============================================================================
elif tahap.startswith("4"):
    st.title("4️⃣ Upload Foto Produk")
    foto_produk = st.file_uploader("Upload Foto Produk:", type=["png", "jpg", "jpeg"], key="up_produk")
    if foto_produk:
        img = Image.open(foto_produk)
        st.session_state["foto_produk"] = img
        st.image(img, width=250, caption="Foto Produk Tersimpan")
        st.success("Foto produk sudah tersimpan untuk tahap selanjutnya.")

# ==============================================================================
# TAHAP 5: DESKRIPSI PRODUK (masih otomatis, gratis)
# ==============================================================================
elif tahap.startswith("5"):
    st.title("5️⃣ Deskripsi Produk")
    mode_deskripsi = st.radio("Cara isi deskripsi:", ["Ketik manual", "Buatkan oleh AI", "Upload screenshot deskripsi"], key="mode_deskripsi")

    if mode_deskripsi == "Ketik manual":
        nama_produk = st.text_input("Nama Produk:", key="nama_produk_manual")
        usp = st.text_area("USP / Keunggulan Produk (opsional):", key="usp_manual")
        if st.button("Simpan Deskripsi"):
            st.session_state["deskripsi_produk"] = f"Nama Produk: {nama_produk}\nUSP: {usp}"
            st.success("Deskripsi tersimpan!")

    elif mode_deskripsi == "Buatkan oleh AI":
        nama_produk = st.text_input("Nama Produk:", key="nama_produk_ai")
        petunjuk = st.text_area("Kasih petunjuk singkat (kategori produk, target pasar, dll):", key="petunjuk_ai")
        if st.button("🚀 Buatkan Deskripsi & USP"):
            images = [st.session_state["foto_produk"]] if st.session_state["foto_produk"] is not None else None
            prompt = (
                f"Buatkan deskripsi produk singkat dan 3-4 poin USP (Unique Selling Point) untuk produk "
                f"bernama '{nama_produk}'. Petunjuk tambahan: {petunjuk}. "
                "Kalau ada foto produk dilampirkan, sesuaikan deskripsi dengan yang terlihat di foto. "
                "Bahasa Indonesia, singkat, menarik untuk konten jualan affiliate."
            )
            with st.spinner("AI lagi bikin deskripsi..."):
                hasil, err = generate_text(prompt, images)
            if err:
                st.error(err)
            else:
                st.session_state["deskripsi_produk"] = hasil
                st.success("Deskripsi berhasil dibuat!")

    else:  # Upload screenshot
        ss_deskripsi = st.file_uploader("Upload screenshot deskripsi produk:", type=["png", "jpg", "jpeg"], key="up_ss_deskripsi")
        if ss_deskripsi and st.button("🚀 Ambil Teks dari Screenshot"):
            img = Image.open(ss_deskripsi)
            prompt = "Baca dan tuliskan ulang semua teks deskripsi produk yang ada di gambar ini secara lengkap dan rapi."
            with st.spinner("AI lagi baca screenshotnya..."):
                hasil, err = generate_text(prompt, [img])
            if err:
                st.error(err)
            else:
                st.session_state["deskripsi_produk"] = hasil
                st.success("Teks berhasil diambil!")

    if st.session_state["deskripsi_produk"]:
        st.markdown("---")
        st.subheader("Deskripsi Tersimpan")
        st.text_area("Bisa diedit manual di sini:", value=st.session_state["deskripsi_produk"], key="edit_deskripsi", height=150)
        st.session_state["deskripsi_produk"] = st.session_state["edit_deskripsi"]

# ==============================================================================
# TAHAP 6: NARASI (masih otomatis, gratis)
# ==============================================================================
elif tahap.startswith("6"):
    st.title("6️⃣ Narasi")
    mode_narasi = st.radio("Cara isi narasi:", ["Ketik manual", "Buatkan oleh AI"], key="mode_narasi")

    if mode_narasi == "Ketik manual":
        narasi_manual = st.text_area("Tulis narasi kamu:", key="narasi_manual", height=150)
        if st.button("Simpan Narasi"):
            st.session_state["narasi"] = narasi_manual
            st.success("Narasi tersimpan!")
    else:
        if st.button("🚀 Buatkan Narasi oleh AI"):
            prompt = (
                f"Buatkan narasi video jualan singkat berbahasa Indonesia berdasarkan deskripsi produk berikut:\n"
                f"{st.session_state['deskripsi_produk']}\n\n"
                f"WAJIB selipkan 7 kata pemicu hipnotis berikut secara natural di dalam narasi: "
                f"{', '.join(KATA_HIPNOTIS)}. "
                "Narasi harus terasa mengalir natural (bukan template kaku), bikin orang penasaran di 2 detik pertama (hook kuat), "
                "dan enak dibaca sebagai voice over."
            )
            with st.spinner("AI lagi nulis narasi..."):
                hasil, err = generate_text(prompt)
            if err:
                st.error(err)
            else:
                st.session_state["narasi"] = hasil
                st.success("Narasi berhasil dibuat!")

    if st.session_state["narasi"]:
        st.markdown("---")
        st.subheader("Narasi Tersimpan")
        st.text_area("Bisa diedit manual di sini:", value=st.session_state["narasi"], key="edit_narasi", height=150)
        st.session_state["narasi"] = st.session_state["edit_narasi"]

# ==============================================================================
# TAHAP 7: PILIHAN GAYA KONTEN
# ==============================================================================
elif tahap.startswith("7"):
    st.title("7️⃣ Pilihan Gaya Konten")
    gaya_konten = st.multiselect(
        "Pilih gaya konten (boleh lebih dari satu):",
        ["POV", "One Take UGC", "Mirroring", "Model Pegang HP", "Podcast", "Testimoni Santai", "Unboxing", "Before-After"],
        key="gaya_konten_pilih",
    )
    durasi = st.selectbox("Durasi video:", ["10 detik", "15 detik", "25 detik"], key="durasi_pilih")

    if st.button("Simpan Pilihan"):
        st.session_state["gaya_konten"] = gaya_konten
        st.session_state["durasi"] = durasi
        st.success("Pilihan gaya konten & durasi tersimpan!")

    if st.session_state.get("gaya_konten"):
        st.markdown("---")
        st.write(f"**Gaya konten aktif:** {', '.join(st.session_state['gaya_konten'])}")
        st.write(f"**Durasi aktif:** {st.session_state.get('durasi', '-')}")

# ==============================================================================
# TAHAP 8: GENERATE STORYBOARD
# ==============================================================================
elif tahap.startswith("8"):
    st.title("8️⃣ Generate Storyboard (6 Scene dalam 1 Lembar)")

    siap = st.session_state["model_final"] is not None and st.session_state["foto_produk"] is not None
    if not siap:
        st.warning("Pastikan Tahap 3 (pilih model) dan Tahap 4 (upload produk) sudah selesai dulu.")
    else:
        st.image(st.session_state["model_final"], width=150, caption="Model")
        st.image(st.session_state["foto_produk"], width=150, caption="Produk")

        gaya = ", ".join(st.session_state.get("gaya_konten", [])) or "UGC santai"
        durasi = st.session_state.get("durasi", "10 detik")
        prompt = f"""Buatkan 1 lembar storyboard berisi 6 panel gambar (grid 2x3 atau 3x2), untuk video affiliate berdurasi {durasi}.

Gunakan Foto Model dan Foto Produk yang saya lampirkan sebagai referensi wajib (Identity Lock — wajah model dan bentuk/warna produk harus konsisten identik di semua 6 panel, jangan berubah antar panel).

Deskripsi Produk: {st.session_state['deskripsi_produk']}
Narasi: {st.session_state['narasi']}
Gaya Konten: {gaya}

Ketentuan tiap panel:
- Panel 1 = HOOK (adegan pembuka paling menarik perhatian dalam 1-2 detik pertama)
- Panel 2-5 = pengembangan cerita: masalah -> penggunaan produk -> hasil/manfaat
- Panel 6 = closing/CTA (call to action)
- Setiap panel WAJIB jelas menunjukkan: angle kamera (eye-level/low/high/dutch), pergerakan zoom kamera,
  gerakan model termasuk gerakan kecil (mata, kedipan, rambut, bulu mata, alis, gerakan mulut/bicara),
  posisi & interaksi model dengan produk.
- Beri caption singkat kecil di bawah tiap panel yang menjelaskan angle, zoom, dan gerakan di panel itu.
- Style visual: cinematic, UGC commercial, warna hangat, terlihat seperti konten organik tapi tetap menjual.
"""
        hasil = prompt_dan_upload(
            prompt, "storyboard",
            catatan_foto="Di Gemini App, lampirkan Foto Model dan Foto Produk (keduanya) sebelum paste prompt-nya."
        )
        if hasil:
            st.session_state["storyboard"] = hasil
            st.success("Storyboard berhasil diupload!")

    if st.session_state["storyboard"] is not None:
        st.markdown("---")
        st.subheader("Hasil Storyboard")
        st.image(st.session_state["storyboard"], use_container_width=True)
        buf = io.BytesIO()
        st.session_state["storyboard"].save(buf, format="PNG")
        st.download_button("💾 Download Storyboard", data=buf.getvalue(), file_name="storyboard.png", mime="image/png")

# ==============================================================================
# TAHAP 9: KONSEP PROMPT VIDEO (masih otomatis, gratis)
# ==============================================================================
elif tahap.startswith("9"):
    st.title("9️⃣ Konsep Prompt Video + Narasi + Voice Over")

    if st.session_state["storyboard"] is None:
        st.warning("Generate storyboard dulu di Tahap 8.")
    else:
        st.image(st.session_state["storyboard"], width=500)

        if st.button("🚀 Buatkan Konsep Prompt Video"):
            gaya = ", ".join(st.session_state.get("gaya_konten", [])) or "UGC santai"
            durasi = st.session_state.get("durasi", "10 detik")
            prompt = f"""Berdasarkan storyboard 6 panel yang sudah dibuat (lihat gambar terlampir), buatkan brief produksi video lengkap dalam Bahasa Indonesia dengan struktur berikut:

1. PROMPT VIDEO (untuk AI video generator seperti Veo/Omni): jelaskan tiap scene secara berurutan sesuai storyboard —
   sebutkan angle kamera, zoom kamera, deskripsi model (fisik, ekspresi), deskripsi produk (bentuk, warna),
   dan SEMUA gerakan termasuk gerakan kecil (kedipan mata, gerak rambut, bulu mata, alis, mulut saat bicara).
   Sertakan instruksi Identity Lock supaya wajah model & bentuk produk konsisten di semua scene.
   Durasi total: {durasi}. Gaya: {gaya}.
2. NARASI LENGKAP: gunakan/kembangkan dari narasi ini: "{st.session_state['narasi']}" — WAJIB mengandung 7 kata
   pemicu hipnotis berikut secara natural: {', '.join(KATA_HIPNOTIS)}.
3. VOICE OVER: versi narasi yang dioptimalkan untuk diucapkan (jeda, penekanan kata).
4. NEGATIVE PROMPT: hal yang harus dihindari AI video (wajah berubah, produk berubah bentuk, tangan cacat, teks salah eja).
5. CATATAN ENGAGEMENT: analisa singkat kenapa struktur video ini berpotensi engagement tinggi dan cara menghindari
   video "stuck"/shadowban di sistem (variasi hook, pacing, dan call-to-action).
"""
            with st.spinner("AI lagi nyusun konsep video..."):
                hasil, err = generate_text(prompt, [st.session_state["storyboard"]])
            if err:
                st.error(err)
            else:
                st.session_state["video_concept"] = hasil
                st.success("Konsep video berhasil dibuat!")

    if st.session_state["video_concept"]:
        st.markdown("---")
        st.subheader("Konsep Prompt Video")
        st.code(st.session_state["video_concept"], language="text")

# ==============================================================================
# TAHAP 10: GENERATE VIDEO (LINK)
# ==============================================================================
elif tahap.startswith("10") or tahap.startswith("🔟"):
    st.title("🔟 Generate Video di Google")
    st.write("Salin storyboard dan konsep prompt video dari tahap sebelumnya, lalu paste di salah satu tools Google berikut:")

    st.markdown("""
- **Gemini App (Nano Banana / Veo akses konsumer, gratis dengan batas harian):**
  [gemini.google.com](https://gemini.google.com)
- **Google Flow (akses Veo, perlu langganan AI Pro/Ultra untuk kuota lebih besar):**
  [labs.google/flow](https://labs.google/flow)
""")

    if st.session_state["video_concept"]:
        st.subheader("Konsep Prompt Video (siap paste)")
        st.code(st.session_state["video_concept"], language="text")
    else:
        st.info("Belum ada konsep video. Balik ke Tahap 9 dulu.")

    if st.session_state["storyboard"] is not None:
        st.subheader("Storyboard (siap upload sebagai referensi)")
        st.image(st.session_state["storyboard"], width=400)
