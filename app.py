"""
app.py — HideIT UAS: Cryptography & Steganography Tool
Penggabungan Project UAS Kriptografi + Steganografi
Mata Kuliah: TI 23 P CN - SH | Dosen: Vicky Indrawan S.T. M.Sc.

Fitur:
  Tab 1 — CIPHER LAB   : Caesar, Vigenere, Affine, AES-256
  Tab 2 — SIGNAL HIDE  : Sequential LSB + Random LSB Steganografi
  Tab 3 — DUAL-LOCK    : Enkripsi (AES/Caesar/Vigenere/Affine) + LSB Stego gabungan
  Tab 4 — ANALYSIS     : PSNR, MSE, Histogram, Error Map, Bit-Plane Slicing

Jalankan dengan: streamlit run app.py
"""

import streamlit as st
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image
import io
import os

# ── Import modul buatan sendiri ───────────────────────────────────────────────
from modules.crypto import (
    caesar_encrypt, caesar_decrypt, caesar_bruteforce,
    vigenere_encrypt, vigenere_decrypt,
    affine_encrypt, affine_decrypt, AFFINE_VALID_A,
    aes_encrypt, aes_decrypt,
)
from modules.stego import (
    embed_sequential, extract_sequential,
    embed_random, extract_random,
    calculate_mse, calculate_psnr, calculate_capacity,
    get_histogram_data, generate_error_map, bit_plane_slice,
    pil_to_bytes, bytes_to_pil,
)


# ─────────────────────────────────────────────
# PAGE CONFIG & THEME
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="HideIT — Crypto & Stego UAS",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS
css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 HideIT")
    st.markdown(
        "<p style='color:#475569;font-size:0.78rem;margin-top:-0.5rem;'>"
        "UAS Kriptografi & Steganografi<br>TI 23 P CN – SH</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "<p style='color:#64748b;font-size:0.75rem;letter-spacing:0.08em;"
        "text-transform:uppercase;font-weight:600;'>Navigasi</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style='font-size:0.82rem;color:#475569;line-height:2;'>
        🔡 <b style='color:#94a3b8;'>Cipher Lab</b> — Enkripsi teks<br>
        🖼️ <b style='color:#94a3b8;'>Signal Hide</b> — Sembunyikan pesan di gambar<br>
        🔒 <b style='color:#94a3b8;'>Dual-Lock</b> — Crypto + Stego sekaligus<br>
        📊 <b style='color:#94a3b8;'>Analysis</b> — PSNR, MSE, Histogram
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        "<p style='color:#2d3748;font-size:0.72rem;'>Dibuat dengan Python + Streamlit<br>"
        "© 2025 HideIT UAS Project</p>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(
        "<h1>🔐 HideIT</h1>"
        "<p style='color:#475569;font-size:0.88rem;margin-top:-0.4rem;'>"
        "Cryptography &amp; Steganography — UAS Project TI 23 P CN</p>",
        unsafe_allow_html=True,
    )
with col_h2:
    st.markdown(
        "<div style='text-align:right;padding-top:0.8rem;'>"
        "<span style='background:#0f2744;color:#38bdf8;border:1px solid #1a3a5c;"
        "border-radius:6px;padding:0.3rem 0.7rem;font-size:0.72rem;"
        "font-family:JetBrains Mono,monospace;letter-spacing:0.05em;'>"
        "● SYSTEM READY</span></div>",
        unsafe_allow_html=True,
    )

st.markdown("---")


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔡  CIPHER LAB",
    "🖼️  SIGNAL HIDE",
    "🔒  DUAL-LOCK",
    "📊  ANALYSIS",
])


# ══════════════════════════════════════════════
# TAB 1 — CIPHER LAB
# ══════════════════════════════════════════════
with tab1:
    st.markdown("### CIPHER LAB")
    st.markdown(
        "<p style='color:#475569;font-size:0.85rem;margin-top:-0.5rem;'>"
        "Enkripsi &amp; dekripsi teks menggunakan cipher klasik dan modern.</p>",
        unsafe_allow_html=True,
    )

    col_alg, col_io = st.columns([1, 2], gap="large")

    with col_alg:
        st.markdown(
            "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
            "text-transform:uppercase;font-weight:600;'>Pilih Algoritma</p>",
            unsafe_allow_html=True,
        )
        algorithm = st.radio(
            label="Algoritma",
            options=["Caesar Cipher", "Vigenere Cipher", "Affine Cipher", "AES-256 (CBC)"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown(
            "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
            "text-transform:uppercase;font-weight:600;'>Mode Operasi</p>",
            unsafe_allow_html=True,
        )
        mode = st.radio("Mode", ["Enkripsi", "Dekripsi"], horizontal=True, label_visibility="collapsed")

        st.markdown("---")
        # ── Parameter spesifik per algoritma ──
        st.markdown(
            "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
            "text-transform:uppercase;font-weight:600;'>Parameter</p>",
            unsafe_allow_html=True,
        )

        key_caesar = key_vig = key_aes = None
        key_aff_a = key_aff_b = None

        if algorithm == "Caesar Cipher":
            key_caesar = st.number_input("Shift (1–25)", min_value=1, max_value=25, value=3)
            with st.expander("ℹ️ Tentang Caesar"):
                st.markdown(
                    "<p style='font-size:0.8rem;color:#64748b;'>"
                    "Setiap huruf digeser sebanyak <b style='color:#94a3b8'>shift</b> posisi.<br>"
                    "Rumus: <code>C = (P + shift) mod 26</code></p>",
                    unsafe_allow_html=True,
                )

        elif algorithm == "Vigenere Cipher":
            key_vig = st.text_input("Kunci (hanya huruf)", value="RAHASIA", placeholder="contoh: KUNCI")
            if key_vig and not key_vig.isalpha():
                st.warning("Kunci hanya boleh mengandung huruf!")
            with st.expander("ℹ️ Tentang Vigenere"):
                st.markdown(
                    "<p style='font-size:0.8rem;color:#64748b;'>"
                    "Kunci diulang sepanjang plaintext.<br>"
                    "Rumus: <code>C_i = (P_i + K_i) mod 26</code></p>",
                    unsafe_allow_html=True,
                )

        elif algorithm == "Affine Cipher":
            key_aff_a = st.selectbox("Nilai a (harus koprima dengan 26)", AFFINE_VALID_A, index=1)
            key_aff_b = st.number_input("Nilai b (0–25)", min_value=0, max_value=25, value=5)
            with st.expander("ℹ️ Tentang Affine"):
                st.markdown(
                    "<p style='font-size:0.8rem;color:#64748b;'>"
                    "Rumus enkripsi: <code>C = (a×P + b) mod 26</code><br>"
                    "Rumus dekripsi: <code>P = a⁻¹×(C − b) mod 26</code></p>",
                    unsafe_allow_html=True,
                )

        elif algorithm == "AES-256 (CBC)":
            key_aes = st.text_input("Password / Kunci AES", type="password", placeholder="min. 8 karakter")
            with st.expander("ℹ️ Tentang AES-256"):
                st.markdown(
                    "<p style='font-size:0.8rem;color:#64748b;'>"
                    "Kunci 256-bit diturunkan dari password via SHA-256.<br>"
                    "IV 128-bit random disertakan di output (Base64).</p>",
                    unsafe_allow_html=True,
                )

    with col_io:
        st.markdown(
            "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
            "text-transform:uppercase;font-weight:600;'>Input Teks</p>",
            unsafe_allow_html=True,
        )
        input_text = st.text_area(
            "Input",
            height=140,
            placeholder="Ketik atau paste teks di sini...",
            label_visibility="collapsed",
        )

        run_btn = st.button(f"▶  {'ENKRIPSI' if mode == 'Enkripsi' else 'DEKRIPSI'}", use_container_width=True)

        if run_btn and input_text.strip():
            result = None
            err = None

            try:
                if algorithm == "Caesar Cipher":
                    result = caesar_encrypt(input_text, key_caesar) if mode == "Enkripsi" \
                             else caesar_decrypt(input_text, key_caesar)

                elif algorithm == "Vigenere Cipher":
                    if not key_vig or not key_vig.isalpha():
                        err = "Kunci Vigenere harus berupa huruf saja!"
                    else:
                        result = vigenere_encrypt(input_text, key_vig) if mode == "Enkripsi" \
                                 else vigenere_decrypt(input_text, key_vig)

                elif algorithm == "Affine Cipher":
                    result = affine_encrypt(input_text, key_aff_a, key_aff_b) if mode == "Enkripsi" \
                             else affine_decrypt(input_text, key_aff_a, key_aff_b)

                elif algorithm == "AES-256 (CBC)":
                    if not key_aes:
                        err = "Masukkan password untuk AES!"
                    else:
                        result = aes_encrypt(input_text, key_aes) if mode == "Enkripsi" \
                                 else aes_decrypt(input_text, key_aes)

            except Exception as e:
                err = f"Error: {str(e)}"

            if err:
                st.error(f"❌ {err}")
            elif result:
                st.markdown(
                    "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                    "text-transform:uppercase;font-weight:600;margin-top:1rem;'>Output</p>",
                    unsafe_allow_html=True,
                )
                st.code(result, language=None)
                st.success(f"✓ {'Enkripsi' if mode == 'Enkripsi' else 'Dekripsi'} berhasil — {len(result)} karakter")

        # ── Brute Force Caesar ──
        if algorithm == "Caesar Cipher" and mode == "Dekripsi":
            with st.expander("🔍 Brute-force Caesar (semua kemungkinan shift)"):
                if input_text.strip():
                    results = caesar_bruteforce(input_text)
                    for shift, text in results:
                        st.markdown(
                            f"<div style='display:flex;gap:1rem;align-items:baseline;margin:0.2rem 0;'>"
                            f"<span style='color:#38bdf8;font-family:JetBrains Mono,mono;font-size:0.75rem;"
                            f"min-width:60px;'>shift={shift:2d}</span>"
                            f"<span style='color:#94a3b8;font-size:0.82rem;'>{text}</span></div>",
                            unsafe_allow_html=True,
                        )


# ══════════════════════════════════════════════
# TAB 2 — SIGNAL HIDE (Steganografi)
# ══════════════════════════════════════════════
with tab2:
    st.markdown("### SIGNAL HIDE")
    st.markdown(
        "<p style='color:#475569;font-size:0.85rem;margin-top:-0.5rem;'>"
        "Sembunyikan pesan teks di dalam gambar PNG menggunakan LSB Steganografi.</p>",
        unsafe_allow_html=True,
    )

    s_mode = st.radio("Operasi", ["Embed (Sembunyikan)", "Extract (Baca)"], horizontal=True)
    st.markdown("---")

    if s_mode == "Embed (Sembunyikan)":
        col_up, col_cfg = st.columns([1, 1], gap="large")

        with col_up:
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Cover Image</p>",
                unsafe_allow_html=True,
            )
            cover_file = st.file_uploader("Upload gambar PNG", type=["png", "jpg", "jpeg"], key="stego_cover")

            if cover_file:
                cover_img = bytes_to_pil(cover_file.read())
                st.image(cover_img, caption="Cover Image", use_column_width=True)

                cap = calculate_capacity(cover_img)
                st.markdown(
                    f"<div style='font-size:0.78rem;color:#475569;margin-top:0.5rem;'>"
                    f"📐 {cap['width']}×{cap['height']} px &nbsp;|&nbsp; "
                    f"Kapasitas maks: <b style='color:#38bdf8'>{cap['max_chars']:,} karakter</b></div>",
                    unsafe_allow_html=True,
                )

        with col_cfg:
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Pesan Rahasia</p>",
                unsafe_allow_html=True,
            )
            secret_msg = st.text_area("Pesan", height=100, placeholder="Tulis pesan yang ingin disembunyikan...", label_visibility="collapsed")

            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;margin-top:0.8rem;'>Metode LSB</p>",
                unsafe_allow_html=True,
            )
            lsb_method = st.radio(
                "Metode",
                ["Sequential LSB", "Random LSB"],
                label_visibility="collapsed",
            )

            stego_key = None
            if lsb_method == "Random LSB":
                stego_key = st.text_input("Seed Key (wajib untuk Random)", placeholder="Masukkan kunci acak...")
                st.caption("Key ini dibutuhkan saat ekstraksi — jangan sampai lupa!")

            embed_btn = st.button("🔒 EMBED PESAN", use_container_width=True)

            if embed_btn:
                if not cover_file:
                    st.error("Upload cover image terlebih dahulu!")
                elif not secret_msg.strip():
                    st.error("Pesan tidak boleh kosong!")
                elif lsb_method == "Random LSB" and not stego_key:
                    st.error("Masukkan key untuk Random LSB!")
                else:
                    with st.spinner("Menyisipkan pesan ke gambar..."):
                        if lsb_method == "Sequential LSB":
                            stego_img, err = embed_sequential(cover_img, secret_msg)
                        else:
                            stego_img, err = embed_random(cover_img, secret_msg, stego_key)

                    if err:
                        st.error(f"❌ {err}")
                    else:
                        psnr_val = calculate_psnr(cover_img, stego_img)
                        mse_val = calculate_mse(cover_img, stego_img)

                        st.success(f"✓ Pesan berhasil disembunyikan!")

                        c1, c2 = st.columns(2)
                        c1.metric("PSNR", f"{psnr_val:.2f} dB", delta="Kualitas bagus" if psnr_val > 40 else "Cukup")
                        c2.metric("MSE", f"{mse_val:.4f}")

                        st.image(stego_img, caption="Stego Image (siap dikirim)", use_column_width=True)

                        img_bytes = pil_to_bytes(stego_img)
                        st.download_button(
                            "⬇  Download Stego Image",
                            data=img_bytes,
                            file_name="stego_hideit.png",
                            mime="image/png",
                            use_container_width=True,
                        )

                        # Simpan ke session state untuk Analysis tab
                        st.session_state['cover_img'] = cover_img
                        st.session_state['stego_img'] = stego_img

    else:  # Extract mode
        col_up2, col_res = st.columns([1, 1], gap="large")

        with col_up2:
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Stego Image</p>",
                unsafe_allow_html=True,
            )
            stego_file = st.file_uploader("Upload stego image", type=["png"], key="stego_extract")

            if stego_file:
                stego_img_ext = bytes_to_pil(stego_file.read())
                st.image(stego_img_ext, caption="Stego Image", use_column_width=True)

        with col_res:
            ext_method = st.radio("Metode Ekstraksi", ["Sequential LSB", "Random LSB"], label_visibility="collapsed")
            ext_key = None
            if ext_method == "Random LSB":
                ext_key = st.text_input("Seed Key", placeholder="Masukkan key yang sama saat embed...")

            extract_btn = st.button("🔓 EKSTRAK PESAN", use_container_width=True)

            if extract_btn:
                if not stego_file:
                    st.error("Upload stego image terlebih dahulu!")
                elif ext_method == "Random LSB" and not ext_key:
                    st.error("Masukkan key untuk Random LSB!")
                else:
                    with st.spinner("Mengekstrak pesan..."):
                        if ext_method == "Sequential LSB":
                            msg_out, err = extract_sequential(stego_img_ext)
                        else:
                            msg_out, err = extract_random(stego_img_ext, ext_key)

                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.success("✓ Pesan berhasil diekstrak!")
                        st.markdown(
                            "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                            "text-transform:uppercase;font-weight:600;margin-top:1rem;'>Pesan Tersembunyi</p>",
                            unsafe_allow_html=True,
                        )
                        st.info(f"💬 {msg_out}")
                        st.caption(f"Panjang pesan: {len(msg_out)} karakter")


# ══════════════════════════════════════════════
# TAB 3 — DUAL-LOCK (Crypto + Stego)
# ══════════════════════════════════════════════
with tab3:
    st.markdown("### DUAL-LOCK")
    st.markdown(
        "<p style='color:#475569;font-size:0.85rem;margin-top:-0.5rem;'>"
        "Gabungan kriptografi + steganografi: pesan dienkripsi <em>lalu</em> disembunyikan di gambar.</p>",
        unsafe_allow_html=True,
    )

    dl_mode = st.radio("Mode Dual-Lock", ["🔒 Lock (Enkripsi + Embed)", "🔓 Unlock (Extract + Dekripsi)"], horizontal=True)
    st.markdown("---")

    if "Lock" in dl_mode:
        col_img, col_opt = st.columns([1, 1], gap="large")

        with col_img:
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Cover Image</p>",
                unsafe_allow_html=True,
            )
            dl_cover = st.file_uploader("Upload Cover Image (PNG)", type=["png", "jpg", "jpeg"], key="dl_cover")
            if dl_cover:
                dl_cover_img = bytes_to_pil(dl_cover.read())
                st.image(dl_cover_img, use_column_width=True)
                cap = calculate_capacity(dl_cover_img)
                st.caption(f"Kapasitas: {cap['max_chars']:,} karakter")

        with col_opt:
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Pesan Rahasia</p>",
                unsafe_allow_html=True,
            )
            dl_msg = st.text_area("Pesan", height=80, placeholder="Pesan yang akan di-lock...", label_visibility="collapsed")

            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;margin-top:0.8rem;'>Kriptografi</p>",
                unsafe_allow_html=True,
            )
            dl_crypto = st.selectbox("Pilih Cipher", ["AES-256 (CBC)", "Caesar Cipher", "Vigenere Cipher", "Affine Cipher"])
            dl_crypto_key = st.text_input(
                "Kunci Enkripsi",
                type="password" if "AES" in dl_crypto else "default",
                placeholder="Password / kunci cipher",
            )
            if dl_crypto == "Caesar Cipher":
                dl_caesar_shift = st.number_input("Shift Caesar", min_value=1, max_value=25, value=7)
            if dl_crypto == "Affine Cipher":
                dl_aff_a = st.selectbox("Nilai a", AFFINE_VALID_A, index=2)
                dl_aff_b = st.number_input("Nilai b", min_value=0, max_value=25, value=8)

            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;margin-top:0.8rem;'>Steganografi</p>",
                unsafe_allow_html=True,
            )
            dl_lsb = st.radio("Metode LSB", ["Sequential LSB", "Random LSB"], horizontal=True)
            dl_stego_key = None
            if dl_lsb == "Random LSB":
                dl_stego_key = st.text_input("Seed Key Stego", placeholder="Key untuk Random LSB")

            lock_btn = st.button("🔒 DUAL-LOCK SEKARANG", use_container_width=True)

            if lock_btn:
                missing = []
                if not dl_cover: missing.append("cover image")
                if not dl_msg.strip(): missing.append("pesan")
                if not dl_crypto_key.strip(): missing.append("kunci cipher")
                if dl_lsb == "Random LSB" and not dl_stego_key: missing.append("seed key stego")

                if missing:
                    st.error(f"Lengkapi: {', '.join(missing)}")
                else:
                    try:
                        with st.spinner("Step 1/2: Mengenkripsi pesan..."):
                            if dl_crypto == "AES-256 (CBC)":
                                encrypted = aes_encrypt(dl_msg, dl_crypto_key)
                            elif dl_crypto == "Caesar Cipher":
                                encrypted = caesar_encrypt(dl_msg, dl_caesar_shift)
                            elif dl_crypto == "Vigenere Cipher":
                                if not dl_crypto_key.isalpha():
                                    st.error("Kunci Vigenere harus huruf saja!")
                                    st.stop()
                                encrypted = vigenere_encrypt(dl_msg, dl_crypto_key)
                            elif dl_crypto == "Affine Cipher":
                                encrypted = affine_encrypt(dl_msg, dl_aff_a, dl_aff_b)

                        with st.spinner("Step 2/2: Menyisipkan ke gambar..."):
                            if dl_lsb == "Sequential LSB":
                                stego_out, err = embed_sequential(dl_cover_img, encrypted)
                            else:
                                stego_out, err = embed_random(dl_cover_img, encrypted, dl_stego_key)

                        if err:
                            st.error(f"❌ Stego error: {err}")
                        else:
                            psnr_v = calculate_psnr(dl_cover_img, stego_out)
                            st.success("✅ DUAL-LOCK berhasil! Pesan terenkripsi & tersembunyi.")

                            st.markdown("**Ciphertext (sebelum disembunyikan):**")
                            st.code(encrypted[:120] + ("..." if len(encrypted) > 120 else ""), language=None)

                            c1, c2 = st.columns(2)
                            c1.metric("PSNR", f"{psnr_v:.2f} dB")
                            c2.metric("Cipher", dl_crypto.split()[0])

                            st.image(stego_out, caption="Stego Image (encrypted + hidden)", use_column_width=True)
                            st.download_button(
                                "⬇  Download Dual-Lock Image",
                                data=pil_to_bytes(stego_out),
                                file_name="duallock_hideit.png",
                                mime="image/png",
                                use_container_width=True,
                            )

                            st.session_state['cover_img'] = dl_cover_img
                            st.session_state['stego_img'] = stego_out

                    except Exception as e:
                        st.error(f"❌ {str(e)}")

    else:  # Unlock mode
        col_u1, col_u2 = st.columns([1, 1], gap="large")

        with col_u1:
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Stego Image</p>",
                unsafe_allow_html=True,
            )
            dl_stego_up = st.file_uploader("Upload Dual-Lock Image", type=["png"], key="dl_unlock")
            if dl_stego_up:
                dl_stego_img = bytes_to_pil(dl_stego_up.read())
                st.image(dl_stego_img, use_column_width=True)

        with col_u2:
            ul_lsb = st.radio("Metode Stego", ["Sequential LSB", "Random LSB"], horizontal=True)
            ul_stego_key = None
            if ul_lsb == "Random LSB":
                ul_stego_key = st.text_input("Seed Key Stego", placeholder="Key stego saat lock")

            ul_crypto = st.selectbox("Cipher yang Dipakai", ["AES-256 (CBC)", "Caesar Cipher", "Vigenere Cipher", "Affine Cipher"])
            ul_crypto_key = st.text_input(
                "Kunci Dekripsi",
                type="password" if "AES" in ul_crypto else "default",
                placeholder="Password / kunci cipher",
            )
            if ul_crypto == "Caesar Cipher":
                ul_caesar_shift = st.number_input("Shift Caesar", min_value=1, max_value=25, value=7)
            if ul_crypto == "Affine Cipher":
                ul_aff_a = st.selectbox("Nilai a", AFFINE_VALID_A, index=2)
                ul_aff_b = st.number_input("Nilai b", min_value=0, max_value=25, value=8)

            unlock_btn = st.button("🔓 UNLOCK SEKARANG", use_container_width=True)

            if unlock_btn:
                if not dl_stego_up:
                    st.error("Upload stego image terlebih dahulu!")
                else:
                    try:
                        with st.spinner("Step 1/2: Mengekstrak ciphertext..."):
                            if ul_lsb == "Sequential LSB":
                                cipher_out, err = extract_sequential(dl_stego_img)
                            else:
                                if not ul_stego_key:
                                    st.error("Masukkan seed key stego!")
                                    st.stop()
                                cipher_out, err = extract_random(dl_stego_img, ul_stego_key)

                        if err:
                            st.error(f"❌ Ekstraksi gagal: {err}")
                        else:
                            with st.spinner("Step 2/2: Mendekripsi pesan..."):
                                if ul_crypto == "AES-256 (CBC)":
                                    plain_out = aes_decrypt(cipher_out, ul_crypto_key)
                                elif ul_crypto == "Caesar Cipher":
                                    plain_out = caesar_decrypt(cipher_out, ul_caesar_shift)
                                elif ul_crypto == "Vigenere Cipher":
                                    plain_out = vigenere_decrypt(cipher_out, ul_crypto_key)
                                elif ul_crypto == "Affine Cipher":
                                    plain_out = affine_decrypt(cipher_out, ul_aff_a, ul_aff_b)

                            st.success("✅ UNLOCK berhasil!")
                            st.markdown("**Pesan Asli:**")
                            st.info(f"💬 {plain_out}")
                            st.caption(f"Ciphertext (terekstrak): {cipher_out[:60]}...")

                    except Exception as e:
                        st.error(f"❌ Dekripsi gagal: {str(e)} — Pastikan kunci benar!")


# ══════════════════════════════════════════════
# TAB 4 — ANALYSIS
# ══════════════════════════════════════════════
with tab4:
    st.markdown("### ANALYSIS")
    st.markdown(
        "<p style='color:#475569;font-size:0.85rem;margin-top:-0.5rem;'>"
        "Analisis kualitas stego image: PSNR, MSE, Histogram, Error Map, Bit-Plane Slicing.</p>",
        unsafe_allow_html=True,
    )

    col_orig, col_steg = st.columns(2, gap="large")

    with col_orig:
        st.markdown(
            "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
            "text-transform:uppercase;font-weight:600;'>Original (Cover) Image</p>",
            unsafe_allow_html=True,
        )
        orig_up = st.file_uploader("Upload cover image", type=["png", "jpg", "jpeg"], key="an_orig")
        if orig_up:
            an_orig = bytes_to_pil(orig_up.read())
            st.image(an_orig, use_column_width=True)
            st.session_state['cover_img'] = an_orig

    with col_steg:
        st.markdown(
            "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
            "text-transform:uppercase;font-weight:600;'>Stego Image</p>",
            unsafe_allow_html=True,
        )
        steg_up = st.file_uploader("Upload stego image", type=["png"], key="an_steg")
        if steg_up:
            an_steg = bytes_to_pil(steg_up.read())
            st.image(an_steg, use_column_width=True)
            st.session_state['stego_img'] = an_steg

    # Gunakan session state jika file belum di-upload manual di tab ini
    an_orig = st.session_state.get('cover_img', None)
    an_steg = st.session_state.get('stego_img', None)

    if orig_up:
        an_orig = bytes_to_pil(orig_up.read()) if False else an_orig  # already set above
    if steg_up:
        an_steg = bytes_to_pil(steg_up.read()) if False else an_steg

    analyze_btn = st.button("📊 JALANKAN ANALISIS", use_container_width=True)

    if analyze_btn:
        if an_orig is None or an_steg is None:
            st.error("Upload kedua gambar (cover + stego) terlebih dahulu, atau jalankan Embed di tab sebelumnya!")
        else:
            st.markdown("---")

            # ── 1. Metrics ──────────────────────────────────────────────────
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Metrik Kualitas</p>",
                unsafe_allow_html=True,
            )
            print("orig:" ,an_orig.shape)
            print("stego:" ,an_steg.shape)
            mse_v = calculate_mse(an_orig, an_steg)
            psnr_v = calculate_psnr(an_orig, an_steg)

            m1, m2, m3 = st.columns(3)
            m1.metric("PSNR", f"{psnr_v:.2f} dB", delta="Bagus ✓" if psnr_v > 40 else "Rendah")
            m2.metric("MSE", f"{mse_v:.6f}")
            quality_label = "Excellent (>40dB)" if psnr_v > 40 else ("Good (30-40dB)" if psnr_v > 30 else "Poor (<30dB)")
            m3.metric("Kualitas", quality_label)

            if psnr_v > 30:
                st.success(f"✓ PSNR {psnr_v:.2f} dB — Perbedaan tidak terlihat mata manusia (target >30 dB)")
            else:
                st.warning(f"⚠ PSNR {psnr_v:.2f} dB — Perbedaan mungkin terlihat. Coba gambar yang lebih besar.")

            st.markdown("---")

            # ── 2. Histogram ─────────────────────────────────────────────────
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Perbandingan Histogram RGB</p>",
                unsafe_allow_html=True,
            )

            hist_orig = get_histogram_data(an_orig)
            hist_steg = get_histogram_data(an_steg)
            channels = {'R': '#ef4444', 'G': '#22c55e', 'B': '#38bdf8'}

            fig, axes = plt.subplots(1, 3, figsize=(14, 3.5))
            fig.patch.set_facecolor('#0d0f14')

            for ax, (ch, color) in zip(axes, channels.items()):
                ax.set_facecolor('#111318')
                x = list(range(256))
                ax.plot(x, hist_orig[ch], color=color, alpha=0.6, linewidth=1, linestyle='--', label='Original')
                ax.plot(x, hist_steg[ch], color=color, linewidth=1, label='Stego')
                ax.set_title(f'Channel {ch}', color='#94a3b8', fontsize=9, pad=8)
                ax.set_xlim(0, 255)
                ax.tick_params(colors='#475569', labelsize=7)
                ax.spines[:].set_color('#1e2230')
                ax.legend(fontsize=7, framealpha=0, labelcolor='#64748b')

            plt.tight_layout(pad=1.5)
            st.pyplot(fig)
            plt.close()

            st.markdown("---")

            # ── 3. Error Map ─────────────────────────────────────────────────
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Error Map (Pixel yang Berubah)</p>",
                unsafe_allow_html=True,
            )

            err_map = generate_error_map(an_orig, an_steg)
            err_arr = np.array(err_map)
            changed_px = int(np.sum(err_arr > 0))
            total_px = err_arr.size

            col_em1, col_em2 = st.columns([2, 1])
            with col_em1:
                st.image(err_map, caption="Putih = pixel berubah | Hitam = tidak berubah", use_column_width=True)
            with col_em2:
                st.markdown(
                    f"<div style='font-size:0.85rem;color:#94a3b8;line-height:2;'>"
                    f"<b style='color:#e2e8f0;'>Pixel berubah:</b><br>{changed_px:,}<br><br>"
                    f"<b style='color:#e2e8f0;'>Total pixel:</b><br>{total_px:,}<br><br>"
                    f"<b style='color:#e2e8f0;'>Persentase:</b><br>"
                    f"<span style='color:#38bdf8;font-size:1.2rem;'>{changed_px/total_px*100:.2f}%</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            st.markdown("---")

            # ── 4. Bit-Plane Slicing ──────────────────────────────────────────
            st.markdown(
                "<p style='color:#64748b;font-size:0.72rem;letter-spacing:0.08em;"
                "text-transform:uppercase;font-weight:600;'>Bit-Plane Slicing (Channel R)</p>",
                unsafe_allow_html=True,
            )
            st.caption("Layer ke-0 (LSB) adalah yang dimodifikasi oleh steganografi. Jika berpola = indikasi stego.")

            planes_orig = bit_plane_slice(an_orig, channel=0)
            planes_steg = bit_plane_slice(an_steg, channel=0)

            fig2, axes2 = plt.subplots(2, 8, figsize=(16, 4))
            fig2.patch.set_facecolor('#0d0f14')

            for i in range(8):
                for row, (planes, label) in enumerate([(planes_orig, 'Original'), (planes_steg, 'Stego')]):
                    ax = axes2[row][i]
                    ax.imshow(planes[i], cmap='gray', vmin=0, vmax=255)
                    ax.set_title(f'Bit {i}' if row == 0 else '', color='#94a3b8', fontsize=7)
                    if i == 0:
                        ax.set_ylabel(label, color='#64748b', fontsize=7)
                    ax.axis('off')
                    if i == 0:
                        ax.spines[:].set_color('#38bdf8')  # Highlight LSB
                        for spine in ax.spines.values():
                            spine.set_linewidth(2)
                            spine.set_visible(True)

            plt.tight_layout(pad=0.5)
            st.pyplot(fig2)
            plt.close()

            st.caption("📌 Baris atas = Original | Baris bawah = Stego | Kotak biru = Bit-0 (LSB)")


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#2d3748;font-size:0.75rem;padding-bottom:1rem;'>"
    "HideIT UAS — Project Kriptografi &amp; Steganografi &nbsp;·&nbsp; "
    "TI 23 P CN-SH &nbsp;·&nbsp; Dosen: Vicky Indrawan S.T. M.Sc."
    "</div>",
    unsafe_allow_html=True,
)