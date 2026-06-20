# 🔒 HideIT_UAS

HideIT_UAS adalah aplikasi steganografi berbasis **Python** dan **Streamlit** yang dikembangkan sebagai proyek Ujian Akhir Semester (UAS). Aplikasi ini memungkinkan pengguna untuk menyembunyikan pesan rahasia ke dalam gambar digital menggunakan metode **Least Significant Bit (LSB)**, serta mengembalikan pesan tersebut melalui proses ekstraksi.

Selain steganografi, aplikasi ini juga mengimplementasikan **Caesar Cipher** sebagai proses enkripsi tambahan sebelum pesan disisipkan ke dalam gambar sehingga tingkat keamanan data menjadi lebih baik.

---

## 📌 Fitur

- 🔐 Enkripsi pesan menggunakan Caesar Cipher
- 🖼️ Penyisipan pesan ke dalam gambar menggunakan metode LSB
- 📤 Ekstraksi pesan dari gambar stego
- 🔓 Dekripsi pesan hasil ekstraksi
- 📊 Perhitungan Mean Squared Error (MSE)
- 📈 Perhitungan Peak Signal-to-Noise Ratio (PSNR)
- 🖥️ Antarmuka interaktif menggunakan Streamlit

---

## 🛠️ Teknologi yang Digunakan

- Python 3.14.6
- Streamlit 1.58.0
- NumPy 2.4.6
- Pillow 12.2.0
- matplotlib 3.11.0
- crytography 49.0.0
- scikit-image 0.26.0
---

## 📂 Struktur Project

```
HideIT_UAS/
│
├── app.py
├── requirements.txt
├── README.md
├── assets/
│
└── modules/
    ├── __init__.py
    ├── stego.py
    └── crypto.py
```

---

## 🚀 Cara Menjalankan Project

### 1. Clone Repository

```bash
https://github.com/Maichel-kel/uas-stegano-kripto.git
```

### 2. Masuk ke Folder Project

```bash
cd HideIT_UAS
```

### 3. Install Library

```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi

```bash
streamlit run app.py
```

atau

```bash
python -m streamlit run app.py
```

---

## 📷 Cara Penggunaan

### Embed Message

1. Upload gambar.
2. Masukkan pesan rahasia.
3. Masukkan nilai pergeseran Caesar Cipher.
4. Klik tombol **Embed**.
5. Download gambar hasil steganografi.

### Extract Message

1. Upload gambar stego.
2. Masukkan nilai Caesar Cipher yang sama.
3. Klik tombol **Extract**.
4. Pesan asli akan ditampilkan kembali.

---

## 📊 Evaluasi Kualitas Citra

Aplikasi menghitung dua parameter evaluasi kualitas gambar, yaitu:

- Mean Squared Error (MSE)
- Peak Signal-to-Noise Ratio (PSNR)

Semakin kecil nilai MSE dan semakin besar nilai PSNR, maka kualitas gambar stego semakin mendekati gambar asli.

---

## 👨‍💻 Tujuan Project

Project ini dibuat sebagai implementasi konsep:

- Steganografi Digital
- Kriptografi Dasar
- Pengolahan Citra Digital
- Keamanan Informasi

dalam bentuk aplikasi yang mudah digunakan melalui antarmuka berbasis web menggunakan Streamlit.

---

## 📄 Lisensi

Project ini dibuat untuk keperluan akademik sebagai tugas Ujian Akhir Semester (UAS).
