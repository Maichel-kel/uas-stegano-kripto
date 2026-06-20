"""
stego.py — Modul Steganografi untuk HideIT UAS
Berisi implementasi LSB (Least Significant Bit):
  1. Sequential LSB — embed bit secara berurutan dari pixel (0,0)
  2. Random LSB     — embed bit ke posisi pixel acak (pakai PRNG + seed dari key)

Juga berisi:
  - PSNR / MSE quality metric
  - Histogram comparison data
  - Bit-plane slicing
  - Error map generator
  - Capacity calculator
"""

import numpy as np
from PIL import Image
import io
import math
def embed_sequential(image, data):
    # sementara dulu biar gak error
    return image


# ─── DELIMITER (penanda akhir pesan) ────────────────────────────────────────
DELIMITER = '1111111111111110'   # 16 bit unik sebagai EOF marker


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def _text_to_bin(text: str) -> str:
    """Ubah string teks ke representasi biner 8-bit per karakter."""
    return ''.join(format(ord(c), '08b') for c in text)


def _bin_to_text(binary: str) -> str:
    """Ubah string biner (kelipatan 8 bit) kembali ke teks."""
    chars = [chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)]
    return ''.join(chars)


def _pil_to_numpy(img: Image.Image) -> np.ndarray:
    """Konversi PIL Image ke numpy array uint8 (pastikan RGB)."""
    return np.array(img.convert('RGB'), dtype=np.uint8)


def _numpy_to_pil(arr: np.ndarray) -> Image.Image:
    """Konversi numpy array uint8 ke PIL Image RGB."""
    return Image.fromarray(arr.astype(np.uint8), 'RGB')


def _key_to_seed(key: str) -> int:
    """Hash string key ke integer seed untuk numpy random."""
    return sum(ord(c) * (i + 1) for i, c in enumerate(key)) % (2**31)


# ─────────────────────────────────────────────
# 1. SEQUENTIAL LSB EMBEDDING
# ─────────────────────────────────────────────
def embed_sequential(cover_img: Image.Image, secret_text: str) -> tuple:
    """
    Sisipkan secret_text ke dalam cover_img menggunakan Sequential LSB.

    Cara kerja:
    - Ubah teks ke biner + tambahkan DELIMITER (EOF marker)
    - Dari pixel (0,0), ubah LSB (bit ke-0) setiap channel RGB secara berurutan
    - Satu pixel RGB = 3 bit yang bisa disimpan

    Returns:
        (stego_img: Image.Image, error: str|None)
    """
    img_array = _pil_to_numpy(cover_img)
    flat_img = img_array.flatten()  # Buat 1D array

    # Hitung kapasitas maksimal gambar
    max_bits = len(flat_img)
    binary_msg = _text_to_bin(secret_text) + DELIMITER

    if len(binary_msg) > max_bits:
        chars_max = (max_bits - len(DELIMITER)) // 8
        return None, f"Pesan terlalu besar! Maksimal {chars_max} karakter untuk gambar ini."

    # Sisipkan bit pesan ke LSB secara berurutan
    flat_copy = flat_img.copy()
    for i, bit in enumerate(binary_msg):
        # Hapus LSB lama (& 0xFE = ...11111110) lalu set LSB baru
        flat_copy[i] = (flat_copy[i] & 0xFE) | int(bit)

    stego_array = flat_copy.reshape(img_array.shape)
    return _numpy_to_pil(stego_array), None


def extract_sequential(stego_img: Image.Image) -> tuple:
    """
    Ekstrak pesan tersembunyi dari stego image (Sequential LSB).

    Returns:
        (message: str, error: str|None)
    """
    img_array = _pil_to_numpy(stego_img)
    flat_img = img_array.flatten()

    binary_data = ''
    for val in flat_img:
        binary_data += str(val & 1)  # Ambil LSB
        if binary_data.endswith(DELIMITER):
            break
    else:
        return None, "Delimiter tidak ditemukan. Gambar mungkin tidak mengandung pesan."

    # Buang delimiter di akhir
    binary_data = binary_data[:-len(DELIMITER)]

    # Pastikan panjang biner kelipatan 8
    if len(binary_data) % 8 != 0:
        return None, "Data biner tidak valid (panjang tidak kelipatan 8)."

    return _bin_to_text(binary_data), None


# ─────────────────────────────────────────────
# 2. RANDOM LSB EMBEDDING
# ─────────────────────────────────────────────
def embed_random(cover_img: Image.Image, secret_text: str, key: str) -> tuple:
    """
    Sisipkan secret_text ke dalam cover_img menggunakan Random LSB.

    Cara kerja:
    - Sama seperti Sequential, tapi URUTAN index pixel diacak
    - Acakan menggunakan numpy PRNG dengan seed dari hash(key)
    - Tanpa key yang benar, tidak bisa diekstrak

    Returns:
        (stego_img: Image.Image, error: str|None)
    """
    img_array = _pil_to_numpy(cover_img)
    flat_img = img_array.flatten()

    max_bits = len(flat_img)
    binary_msg = _text_to_bin(secret_text) + DELIMITER

    if len(binary_msg) > max_bits:
        chars_max = (max_bits - len(DELIMITER)) // 8
        return None, f"Pesan terlalu besar! Maksimal {chars_max} karakter untuk gambar ini."

    # Buat array index dan acak urutan pakai seed dari key
    indices = np.arange(len(flat_img))
    seed = _key_to_seed(key)
    rng = np.random.default_rng(seed)
    rng.shuffle(indices)

    flat_copy = flat_img.copy()
    for i, bit in enumerate(binary_msg):
        idx = indices[i]
        flat_copy[idx] = (flat_copy[idx] & 0xFE) | int(bit)

    stego_array = flat_copy.reshape(img_array.shape)
    return _numpy_to_pil(stego_array), None


def extract_random(stego_img: Image.Image, key: str) -> tuple:
    """
    Ekstrak pesan dari stego image (Random LSB).
    Key harus sama dengan yang dipakai saat embed.

    Returns:
        (message: str, error: str|None)
    """
    img_array = _pil_to_numpy(stego_img)
    flat_img = img_array.flatten()

    # Rekonstruksi urutan index yang sama dengan embed
    indices = np.arange(len(flat_img))
    seed = _key_to_seed(key)
    rng = np.random.default_rng(seed)
    rng.shuffle(indices)

    binary_data = ''
    for idx in indices:
        binary_data += str(flat_img[idx] & 1)
        if binary_data.endswith(DELIMITER):
            break
    else:
        return None, "Delimiter tidak ditemukan. Key salah atau gambar tidak mengandung pesan."

    binary_data = binary_data[:-len(DELIMITER)]

    if len(binary_data) % 8 != 0:
        return None, "Data biner tidak valid. Pastikan key benar."

    return _bin_to_text(binary_data), None


# ─────────────────────────────────────────────
# 3. QUALITY METRICS
# ─────────────────────────────────────────────
def calculate_mse(original: Image.Image, stego: Image.Image) -> float:
    """
    Mean Squared Error (MSE) antara gambar asli dan stego.
    Semakin kecil = semakin mirip.
    Rumus: MSE = (1/N) * Σ(original_i - stego_i)²
    """
    orig_arr = _pil_to_numpy(original).astype(np.float64)
    stego_arr = _pil_to_numpy(stego).astype(np.float64)
    return float(np.mean((orig_arr - stego_arr) ** 2))


def calculate_psnr(original: Image.Image, stego: Image.Image) -> float:
    """
    Peak Signal-to-Noise Ratio (PSNR) dalam dB.
    Semakin tinggi = semakin bagus (target > 30 dB agar tidak terlihat mata).
    Rumus: PSNR = 10 * log10(MAX² / MSE)
    Untuk 8-bit image: MAX = 255
    """
    mse = calculate_mse(original, stego)
    if mse == 0:
        return float('inf')
    return 10 * math.log10((255.0 ** 2) / mse)


def calculate_capacity(img: Image.Image) -> dict:
    """
    Hitung kapasitas maksimal gambar untuk menyimpan pesan LSB.
    Returns dict dengan info ukuran gambar dan kapasitas.
    """
    arr = _pil_to_numpy(img)
    h, w, c = arr.shape
    total_pixels = h * w
    total_channels = h * w * c
    delimiter_bits = len(DELIMITER)

    usable_bits = total_channels - delimiter_bits
    max_chars = usable_bits // 8

    return {
        'width': w,
        'height': h,
        'channels': c,
        'total_pixels': total_pixels,
        'total_channels': total_channels,
        'max_chars': max_chars,
        'max_bits': usable_bits,
    }


# ─────────────────────────────────────────────
# 4. STEGANALYSIS TOOLS
# ─────────────────────────────────────────────
def get_histogram_data(img: Image.Image) -> dict:
    """
    Hitung histogram RGB untuk analisis steganalisis.
    Returns dict dengan arrays histogram untuk channel R, G, B.
    """
    arr = _pil_to_numpy(img)
    hist_r, _ = np.histogram(arr[:, :, 0].flatten(), bins=256, range=(0, 256))
    hist_g, _ = np.histogram(arr[:, :, 1].flatten(), bins=256, range=(0, 256))
    hist_b, _ = np.histogram(arr[:, :, 2].flatten(), bins=256, range=(0, 256))
    return {'R': hist_r.tolist(), 'G': hist_g.tolist(), 'B': hist_b.tolist()}


def generate_error_map(original: Image.Image, stego: Image.Image) -> Image.Image:
    """
    Buat error map: gambar hitam-putih yang menunjukkan pixel mana yang berubah.
    Hitam = tidak berubah, Putih = berubah.
    Berguna untuk membuktikan pola Sequential vs Random.
    """
    orig_arr = _pil_to_numpy(original)
    stego_arr = _pil_to_numpy(stego)

    diff = np.abs(orig_arr.astype(np.int16) - stego_arr.astype(np.int16))
    # Kalau ada perbedaan di channel mana pun, tandai putih
    mask = np.any(diff > 0, axis=2).astype(np.uint8) * 255

    # Kembalikan sebagai grayscale PIL image
    return Image.fromarray(mask, 'L')


def bit_plane_slice(img: Image.Image, channel: int = 0) -> list:
    """
    Bit-plane slicing: pecah gambar menjadi 8 lapisan bit.
    channel: 0=R, 1=G, 2=B
    Layer ke-0 (LSB) adalah yang dimodifikasi oleh steganografi.
    Returns list of 8 numpy arrays (0 atau 255).
    """
    arr = _pil_to_numpy(img)
    ch = arr[:, :, channel]
    planes = []
    for bit in range(8):
        plane = ((ch >> bit) & 1) * 255
        planes.append(plane.astype(np.uint8))
    return planes


# ─────────────────────────────────────────────
# 5. IMAGE I/O HELPERS
# ─────────────────────────────────────────────
def pil_to_bytes(img: Image.Image, fmt: str = 'PNG') -> bytes:
    """Konversi PIL Image ke bytes untuk download di Streamlit."""
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def bytes_to_pil(raw: bytes) -> Image.Image:
    """Konversi bytes (dari st.file_uploader) ke PIL Image."""
    return Image.open(io.BytesIO(raw)).convert('RGB')