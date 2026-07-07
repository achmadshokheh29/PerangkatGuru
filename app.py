import streamlit as st
import google.generativeai as genai
import re

# Config Halaman Utama
st.set_page_config(page_title="Generator AI Perangkat Ajar 1 Tahun", layout="wide", page_icon="📚")

# Inisialisasi Session State agar data tidak hilang saat pindah halaman
if 'dokumen_data' not in st.session_state:
    st.session_state['dokumen_data'] = {
        "cp": "Belum digenerate.", "tp": "Belum digenerate.", "atp": "Belum digenerate.",
        "prota": "Belum digenerate.", "prosem1": "Belum digenerate.", "prosem2": "Belum digenerate.",
        "kktp": "Belum digenerate.", "modul": "Belum digenerate."
    }
if 'is_generated' not in st.session_state:
    st.session_state['is_generated'] = False

# --- SIDEBAR NAVIGASI ---
st.sidebar.markdown("### 🤖 Gemini Generator AI")
st.sidebar.caption("Perangkat Ajar 1 Tahun")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigasi Dokumen:",
    [
        "📁 Data Global (Input)",
        "📄 1. Analisis CP",
        "📄 2. Tujuan Pemb. (TP)",
        "📄 3. Alur (ATP)",
        "📄 4. Prota",
        "📄 5a. Prosem Sem 1",
        "📄 5b. Prosem Sem 2",
        "📄 6. KKTP",
        "📄 7. Modul Ajar"
    ]
)

st.sidebar.markdown("---")
# Input API Key diletakkan di bawah sidebar agar rapi
api_key = st.sidebar.text_input("🔑 Masukkan Gemini API Key:", type="password")
model_choice = st.sidebar.selectbox("Pilih Model:", ["gemini-1.5-flash", "gemini-1.5-pro"])

# --- HALAMAN 1: DATA GLOBAL (INPUT) ---
if menu == "📁 Data Global (Input)":
    st.title("Data Global (Input)")
    st.markdown("### **Input Data Global 1 Tahun**")
    st.caption("Isi identitas dan komponen dasar (TP & Materi akan ditarik otomatis oleh AI saat Generate).")
    
    # Grid Form 3 Kolom
    col1, col2, col3 = st.columns(3)
    
    with col1:
        provinsi = st.text_input("Provinsi / Kota", "Jawa Timur")
        alamat_sekolah = st.text_input("Alamat Sekolah", "Jl. Pb. Sudirman No.50 Gunungsari Umbulsari")
        fase_kelas = st.text_input("Fase / Kelas", "Fase F / Kelas XII")
        jp_minggu = st.text_input("JP per Minggu", "12 JP/Minggu") # Disesuaikan dengan input terbaru Anda
        kota_ttd = st.text_input("Kota, Tanggal TTD", "Jember, 17 Juli 2026")
        
    with col2:
        Yayasan = st.text_input("Yayasan", "Yayasan Sosial Akbar Sejahtera")
        mata_pelajaran = st.text_input("Mata Pelajaran", "Dasar-Dasar Pengembangan Perangkat Lunak dan Gim")
        tahun_pelajaran = st.text_input("Tahun Pelajaran", "2026/2027")
        durasi_pertemuan = st.text_input("Durasi 1x Pertemuan", "4 JP (80 Menit)") # Disesuaikan dengan input terbaru Anda
        nama_kepsek = st.text_input("Nama Kepsek", "Indah Purwandari, S.Pd.I")
        
    with col3:
        satuan_pendidikan = st.text_input("Satuan Pendidikan", "SMK AKBAR UMBULSARI")
        
        singkatan_mapel = st.text_input("Singkatan Mapel (Mis: DDPPLG)", "DDPPLG") # Disesuaikan dengan input terbaru Anda
        alokasi_waktu = st.text_input("Alokasi Waktu Total", "432 JP / Tahun") # Disesuaikan dengan input terbaru Anda
        nama_guru = st.text_input("Nama Guru", "Achmad Muhtarus Shokheh, S.Kom")

    st.markdown("---")
    
    # Tombol Utama Generate
    if st.button("🚀 Generate Dokumen 1 s.d. 7 Sekaligus", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Mohon isi Gemini API Key di sidebar sebelah kiri terlebih dahulu!")
        else:
            with st.spinner("🧠 AI sedang memproses seluruh dokumen kurikulum secara sinkronos... Mohon tunggu..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # PERBAIKAN: Menambahkan prefiks 'models/' agar tidak terjadi Error 404 pada Streamlit Cloud
                    full_model_name = f"models/{model_choice}"
                    model = genai.GenerativeModel(full_model_name)
                    
                    # Prompt terstruktur menggunakan XML tags untuk mempermudah pemisahan halaman
                    prompt = f"""
                    Anda adalah sistem pakar Kurikulum Merdeka Kemendikbud RI. Buatlah perangkat ajar komprehensif berformat Markdown dan tabel HTML berdasarkan data berikut:
                    - Sekolah: {satuan_pendidikan} ({Yayasan}, {provinsi})
                    - Guru: {nama_guru}
                    - Kepsek: {nama_kepsek}
                    - Mapel: {mata_pelajaran} ({singkatan_mapel}) - {fase_kelas} - TP {tahun_pelajaran}
                    - Waktu: {alokasi_waktu} ({jp_minggu}, {durasi_pertemuan})
                    - TTD: {kota_ttd}

                    Wajib kembalikan output dalam format tag XML persis seperti di bawah ini tanpa terputus:
                    
                    <cp>Disini isi Analisis Capaian Pembelajaran (CP) per elemen</cp>
                    <tp>Disini isi Daftar Tujuan Pembelajaran (TP) terstruktur beserta kodenya</tp>
                    <atp>Disini isi tabel HTML Alur Tujuan Pembelajaran (ATP) lengkap</atp>
                    <prota>Disini isi Program Tahunan (PROTA) dalam bentuk tabel HTML distribusi jam</prota>
                    <prosem1>Disini isi Program Semester 1 (PROSEM Sem 1) tabel HTML lengkap bulanan</prosem1>
                    <prosem2>Disini isi Program Semester 2 (PROSEM Sem 2) tabel HTML lengkap bulanan</prosem2>
                    <kktp>Disini isi Kriteria Ketercapaian Tujuan Pembelajaran (KKTP) dengan interval nilai</kktp>
                    <modul>Disini isi 1 Contoh Modul Ajar utuh standar Kurikulum Merdeka lengkap dengan langkah inti & asesmen</modul>
                    """
                    
                    response = model.generate_content(prompt)
                    text = response.text
                    
                    # Regex Parsing untuk memisahkan teks ke masing-masing halaman menu
                    keys = ["cp", "tp", "atp", "prota", "prosem1", "prosem2", "kktp", "modul"]
                    for key in keys:
                        match = re.search(f"<{key}>(.*?)</{key}>", text, re.DOTALL)
                        if match:
                            st.session_state['dokumen_data'][key] = match.group(1).strip()
                    
                    st.session_state['is_generated'] = True
                    st.success("🎉 Semua dokumen berhasil dibuat! Silakan klik menu di sidebar kiri untuk melihat hasilnya satu per satu.")
                    
                except Exception as e:
                    st.error(f"Gagal generate dokumen: {e}")

# --- FUNGSI MERENDER HALAMAN DOKUMEN ---
else:
    # Mapping menu ke key session state
    menu_mapping = {
        "📄 1. Analisis CP": "cp",
        "📄 2. Tujuan Pemb. (TP)": "tp",
        "📄 3. Alur (ATP)": "atp",
        "📄 4. Prota": "prota",
        "📄 5a. Prosem Sem 1": "prosem1",
        "📄 5b. Prosem Sem 2": "prosem2",
        "📄 6. KKTP": "kktp",
        "📄 7. Modul Ajar": "modul"
    }
    
    current_key = menu_mapping[menu]
    st.title(menu)
    
    if not st.session_state['is_generated']:
        st.warning("⚠️ Dokumen belum di-generate. Silakan kembali ke menu **📁 Data Global (Input)** untuk membuat dokumen terlebih dahulu.")
    else:
        # Style khusus biar tampilan tabel HTML rapi ala cetakan kertas printer
        st.markdown("""
        <style>
        .print-box { background: white; padding: 25px; border: 1px solid #d1d5db; border-radius: 6px; color: black; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
        th, td { border: 1px solid #4b5563; padding: 8px; text-align: left; }
        th { background-color: #f3f4f6; }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="print-box">', unsafe_allow_html=True)
        st.markdown(st.session_state['dokumen_data'][current_key], unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        # Tombol download mandiri per halaman
        st.download_button(
            label=f"📥 Download {menu[4:]} (.md)",
            data=st.session_state['dokumen_data'][current_key],
            file_name=f"{current_key}.md",
            mime="text/markdown"
        )
