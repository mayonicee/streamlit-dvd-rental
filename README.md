# DVD Rental Analytics Dashboard 📊

Dashboard analitik interaktif berbasis **Streamlit** untuk menganalisis data transaksi penyewaan DVD. Project ini mengintegrasikan kueri basis data PostgreSQL, analisis performa bisnis, visualisasi data interaktif, dan algoritma *Machine Learning* untuk segmentasi pelanggan.

---

## 🚀 Fitur Utama

Dashboard ini dibagi menjadi beberapa modul analisis utama yang dapat diakses melalui menu navigasi samping:

1. **Customer Segmentation & Recommendation**
   - Melakukan segmentasi pelanggan menggunakan analisis **RFM (Recency, Frequency, Monetary)**.
   - Menggunakan algoritma **K-Means Clustering** untuk mengelompokkan pelanggan ke dalam kategori tertentu (seperti VIP, Loyal, Churn Risk, dll).
   - Memberikan rekomendasi pemasaran/strategi bisnis spesifik untuk setiap segmen pelanggan.

2. **Global & Store Insight**
   - Menganalisis metrik global seperti distribusi genre film terpopuler yang mendominasi permintaan pasar.
   - Menampilkan kontribusi genre utama terhadap total permintaan penyewaan.
   - Visualisasi peringkat pelanggan teratas (*Top Customers*) berdasarkan total transaksi.

3. **Customer Prediction**
   - Form interaktif untuk memprediksi segmen pelanggan baru secara langsung dengan memasukkan nilai metrik RFM (*Recency*, *Frequency*, *Monetary*).
   - Memberikan wawasan instan terkait risiko *churn* dan tingkat keterlibatan pelanggan (*engagement*).

4. **Content Profitability & Catalog Strategy**
   - Menyajikan analisis profitabilitas berdasarkan kategori film.
   - Visualisasi tren pendapatan bulanan serta perbandingan antara volume sewa (*Rental Count*) dan pendapatan (*Revenue*).
   - Analisis hubungan harga sewa terhadap permintaan film (*Price vs Demand*).

5. **Store Performance & Revenue Leakage**
   - Menganalisis perbandingan performa antar cabang toko (misalnya Jakarta vs Surabaya).
   - Melacak metrik kinerja toko: total pendapatan, pelanggan aktif, rata-rata transaksi, hingga kebocoran pendapatan (*Revenue Leakage*) yang disebabkan oleh keterlambatan pengembalian atau faktor operasional lainnya.

6. **Engagement & Timing Analysis**
   - Menganalisis perilaku waktu penyewaan oleh pelanggan (hari/jam sibuk).
   - Memetakan waktu aktif transaksi pelanggan untuk membantu menentukan jam operasional optimal atau strategi promosi berbasis waktu.

---

## 🛠️ Teknologi yang Digunakan

- **Bahasa Pemrograman**: Python 3.x
- **Framework Dashboard**: Streamlit
- **Basis Data**: PostgreSQL (koneksi menggunakan `psycopg2-binary` dan `SQLAlchemy`)
- **Manipulasi Data**: Pandas, NumPy
- **Visualisasi**: Plotly Express & Plotly Graph Objects
- **Machine Learning**: Scikit-Learn (K-Means Clustering, StandardScaler)
- **Penyimpanan Model**: Joblib (`.pkl` files)

---

## 📁 Struktur Folder

```directory
streamlitproject/
│
├── stremlitproject/
│   ├── app.py                      # File utama (Entry Point Streamlit)
│   ├── requirements.txt            # Daftar pustaka (dependencies) Python
│   │
│   ├── config/                     # Konfigurasi koneksi database
│   │   └── database.py
│   │
│   ├── data/                       # Kueri SQL untuk penarikan data
│   │   └── queries.py
│   │
│   ├── components/                 # Komponen UI modular (KPI, Chart, Tabel)
│   │   ├── charts.py
│   │   ├── kpi.py
│   │   └── table.py
│   │
│   ├── lib/                        # Modul utilitas sistem, gaya (theme), dan pemrosesan data
│   │   ├── data.py
│   │   ├── db.py
│   │   ├── style.py
│   │   └── utils.py
│   │
│   ├── pages/                      # Menu/Halaman Dashboard
│   │   ├── 1. Customer Segmentation.py
│   │   ├── 2. global Insight.py
│   │   ├── 3. Prediction.py
│   │   ├── Profitability Dashboard.py
│   │   ├── Store Performance & Revenue Leakage.py
│   │   └── engagement_dashboard.py
│   │
│   ├── assets/                     # Aset pelengkap seperti berkas CSS custom
│   │   └── style.css
│   │
│   # Model ML terlatih & data CSV cadangan jika DB tidak terhubung
│   ├── kmeans_customer_model.pkl
│   ├── scaler.pkl
│   ├── cluster_map.pkl
│   ├── customer_payment_dataset.csv
│   └── rental.csv
│
├── .gitignore                      # File pengecualian Git
└── README.md                       # Dokumentasi project (File ini)
```

---

## ⚙️ Cara Instalasi & Menjalankan Project

### 1. Clone Repositori
```bash
git clone https://github.com/mayonicee/streamlit-dvd-rental.git
cd streamlit-dvd-rental
```

### 2. Buat & Aktifkan Virtual Environment (Direkomendasikan)
Di Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r stremlitproject/requirements.txt
```

### 4. Konfigurasi Database (Opsional)
Aplikasi mendukung koneksi langsung ke PostgreSQL. Konfigurasi kredensial database dapat disetel melalui variabel lingkungan (*environment variables*) atau melalui file `.streamlit/secrets.toml`:
```toml
# .streamlit/secrets.toml
PGHOST = "localhost"
PGPORT = 5432
PGDATABASE = "dvdrental"
PGUSER = "postgres"
PGPASSWORD = "yourpassword"
```
*Catatan: Jika database PostgreSQL tidak terdeteksi atau tidak dapat dijangkau, aplikasi akan secara otomatis memuat data cadangan dari file CSV (`customer_payment_dataset.csv` & `rental.csv`) atau menghasilkan data tiruan agar dashboard tetap dapat berjalan.*

### 5. Jalankan Dashboard
```bash
streamlit run stremlitproject/app.py
```
Aplikasi akan otomatis terbuka pada peramban web Anda di alamat default: `http://localhost:8501`.
