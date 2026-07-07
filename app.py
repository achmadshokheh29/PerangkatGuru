import streamlit as st
import google.generativeai as genai
import re

# ==========================================
# 🔑 AMBIL API KEY DARI STREAMLIT SECRETS
# ==========================================
if "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    # Cadangan jika Anda lupa memasukkannya di panel Advanced Settings Streamlit
    GEMINI_API_KEY = ""

# Config Halaman Utama & Tema
st.set_page_config(
    page_title="Generator AI Perangkat Ajar 1 Tahun", 
    layout="wide", 
    page_icon="📚"
)

# Kustomisasi Style Antarmuka (Premium Dark Modern Theme)
st.markdown("""
<style>
    /* Mengubah font dan background global */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0d0f12;
        color: #e2e8f0;
    }
    
    /* Style untuk form input login & data */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1a1f26 !important;
        color: #ffffff !important;
        border: 1px solid #2d3748 !important;
        border-radius: 8px !important;
    }
    
    /* Box cetak dokumen / print-box */
    .print-box { 
        background: #ffffff; 
        padding: 30px; 
        border: 1px solid #cbd5e1; 
        border-radius: 8px; 
        color: #0f172a; 
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .print-box table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-bottom: 20px; 
    }
    .print-box th, .print-box td { 
        border: 1px solid #94a3b8; 
        padding: 10px; 
        text-align: left; 
    }
    .print-box th { 
        background-color: #f1f5f9; 
        color: #0f172a;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# URL Gambar Default / Logo
LOGO_URL = "https://lh3.googleusercontent.com/d/1iNQvoD5FsMyCrj6MN4bhE3DshZdqnIYP"

# Inisialisasi Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'dokumen_data' not in st.session_state:
    st.session_state['dokumen_data'] = {
        "cp": "Belum digenerate.", "tp": "Belum digenerate.", "atp": "Belum digenerate.",
        "prota": "Belum digenerate.", "prosem1": "Belum digenerate.", "prosem2": "Belum digenerate.",
        "kktp": "Belum digenerate.", "modul": "Belum digenerate."
    }
if 'is_generated' not in st.session_state:
    st.session_state['is_generated'] = False


# ==========================================
# 🔒 HALAMAN 1: FORM LOGIN
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔒 Login Generator Perangkat Ajar")
        st.caption("Masuk menggunakan kredensial akun guru Anda.")
        
        username = st.text_input("Username / NIP")
        password = st.text_input("Password", type="password")
        
        if st.button("Masuk Aplikasi 🚀", type="primary", use_container_width=True):
            if username == "admin" and password == "guruakbar":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Username atau Password salah! Hubungi Tim IT Kurikulum.")
    st.stop()


# ==========================================
# 🎛️ SIDEBAR NAVIGASI DASHBOARD
# ==========================================
st.sidebar.markdown("### 🤖 Gemini Generator AI")
st.sidebar.caption("Sistem Kurikulum Merdeka v2.0")
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
model_choice = st.sidebar.selectbox("Pilih Otak AI (Model):", ["gemini-1.5-flash", "gemini-1.5-pro"])

if st.sidebar.button("Logout 🚪", use_container_width=True):
    st.session_state['logged_in'] = False
    st.session_state['is_generated'] = False
    st.rerun()


# ==========================================
# 📁 DASHBOARD HALAMAN INPUT DATA
# ==========================================
if menu == "📁 Data Global (Input)":
    st.title("Data Global (Input)")
    st.markdown("### **Input Identitas Kurikulum Merdeka 1 Tahun**")
    st.caption("Lengkapi instrumen dasar sekolah di bawah ini. Dokumen capaian dan materi ajar akan diformulasikan otomatis oleh AI.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        provinsi = st.text_input("Provinsi / Kota", "Jawa Timur")
        alamat_sekolah = st.text_input("Alamat Sekolah", "Jl. Pb. Sudirman No.50 Gunungsari Umbulsari")
        fase_kelas = st.text_input("Fase / Kelas", "Fase F / Kelas XII")
        jp_minggu = st.text_input("JP per Minggu", "12 JP/Minggu")
        kota_ttd = st.text_input("Kota, Tanggal TTD", "Jember, 17 Juli 2026")
        
    with col2:
        Yayasan = st.text_input("Yayasan", "Yayasan Sosial Akbar Sejahtera")
        mata_pelajaran = st.text_input("Mata Pelajaran", "Dasar-Dasar Pengembangan Perangkat Lunak dan Gim")
        tahun_pelajaran = st.text_input("Tahun Pelajaran", "2026/2027")
        durasi_pertemuan = st.text_input("Durasi 1x Pertemuan", "4 JP (80 Menit)")
        nama_kepsek = st.text_input("Nama Kepsek", "Indah Purwandari, S.Pd.I")
        
    with col3:
        satuan_pendidikan = st.text_input("Satuan Pendidikan", "SMK AKBAR UMBULSARI")
        singkatan_mapel = st.text_input("Singkatan Mapel", "DDPPLG")
        alokasi_waktu = st.text_input("Alokasi Waktu Total", "432 JP / Tahun")
        nama_guru = st.text_input("Nama Guru", "Achmad Muhtarus Shokheh, S.Kom")

    st.markdown("---")
    
    if st.button("🚀 Generate Dokumen 1 s.d. 7 Sekaligus", type="primary", use_container_width=True):
        if not GEMINI_API_KEY:
            st.error("❌ Kunci API Gemini tidak terdeteksi! Pastikan sudah memasukkannya ke Streamlit Secrets di Dashboard Streamlit Cloud.")
        else:
            with st.spinner("🧠 AI sedang menyusun program kurikulum tahunan & tabel administrasi ajar... Silakan tunggu..."):
                try:
                    # Menggunakan metode konfigurasi pustaka bawaan yang stabil
                    genai.configure(api_key=GEMINI_API_KEY)
                    model = genai.GenerativeModel(model_choice)
                    
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
                    
                    keys = ["cp", "tp", "atp", "prota", "prosem1", "prosem2", "kktp", "modul"]
                    for key in keys:
                        match = re.search(f"<{key}>(.*?)</{key}>", text, re.DOTALL)
                        if match:
                            st.session_state['dokumen_data'][key] = match.group(1).strip()
                    
                    st.session_state['is_generated'] = True
                    st.success("🎉 Seluruh instrumen administrasi mengajar berhasil dibuat! Silakan buka panel menu sebelah kiri.")
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses data AI: {e}")


# ==========================================
# 📄 DISPLAY & UNDUH HASIL GENERATE DOKUMEN
# ==========================================
else:
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
        st.warning("⚠️ Data administrasi belum siap. Silakan kembali ke menu **📁 Data Global (Input)** untuk menjalankan proses penciptaan dokumen.")
    else:
        st.markdown('<div class="print-box">', unsafe_allow_html=True)
        st.markdown(st.session_state['dokumen_data'][current_key], unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.download_button(
            label=f"📥 Download File {menu[5:]} (.md)",
            data=st.session_state['dokumen_data'][current_key],
            file_name=f"{current_key}.md",
            mime="text/markdown",
            use_container_width=True
        )
