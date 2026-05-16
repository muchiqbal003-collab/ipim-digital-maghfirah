import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import plotly.express as px
from PIL import Image
import io
import base64

# ========== KONFIGURASI SUPABASE ==========
SUPABASE_URL = "https://mvhrnrvdhibdtvulmqkr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12aHJucnZkaGliZHR2dWxtcWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MTc5MjksImV4cCI6MjA5NDQ5MzkyOX0.IsS1wSXtGb0Keroc3UvsiVT38u-gea0_IVdAm1snBVw"
# ==========================================

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Konfigurasi halaman
st.set_page_config(
    page_title="IPIM ACADEMIC",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS - NUANSA HIJAU PUTIH ==========
st.markdown("""
<style>
    /* Warna utama hijau segar */
    :root {
        --primary: #2E7D32;
        --primary-light: #4CAF50;
        --primary-soft: #E8F5E9;
        --accent: #1B5E20;
        --text: #333333;
        --bg-light: #F5F9F5;
        --white: #FFFFFF;
        --gray: #F5F5F5;
        --shadow: 0 2px 12px rgba(0,0,0,0.08);
        --shadow-hover: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #F0F7F0 0%, #FFFFFF 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        padding: 1.2rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-size: 0.9rem;
    }
    
    /* Card styling */
    .card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: var(--shadow);
        transition: transform 0.2s, box-shadow 0.2s;
        border: 1px solid rgba(46, 125, 50, 0.1);
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    /* Stat box */
    .stat-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #FFFFFF 100%);
        padding: 1rem;
        border-radius: 16px;
        text-align: center;
        border-left: 4px solid #2E7D32;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.2rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(46,125,50,0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #F5F9F5 100%);
        border-right: 1px solid rgba(46,125,50,0.1);
    }
    
    /* Form styling */
    .stTextInput > div > div > input, .stSelectbox > div > div {
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2E7D32;
        box-shadow: 0 0 0 2px rgba(46,125,50,0.2);
    }
    
    /* Login card khusus */
    .login-card {
        background: white;
        border-radius: 32px;
        padding: 2rem;
        max-width: 450px;
        margin: 0 auto;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border: 1px solid rgba(46,125,50,0.2);
    }
    
    /* Profile image */
    .profile-img {
        border-radius: 50%;
        border: 3px solid #2E7D32;
        padding: 3px;
        background: white;
    }
    
    /* Badge */
    .badge-success {
        background: #E8F5E9;
        color: #2E7D32;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'guru_data' not in st.session_state:
    st.session_state.guru_data = None
if 'selected_matkul' not in st.session_state:
    st.session_state.selected_matkul = None

# ==================== FUNGSI ====================

def login_guru(nidn, password):
    try:
        response = supabase.table("guru").select("*").eq("nidn", nidn).eq("password", password).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_guru_matkul(nidn):
    """Ambil semua mata kuliah yang diampu seorang guru"""
    try:
        response = supabase.table("guru").select("mata_kuliah, kelas_diajar").eq("nidn", nidn).execute()
        if response.data:
            return [(row['mata_kuliah'], row['kelas_diajar']) for row in response.data]
        return []
    except Exception:
        return []

def update_foto(nidn, foto_bytes, foto_type):
    """Update foto profil guru"""
    try:
        supabase.table("guru").update({
            "foto": base64.b64encode(foto_bytes).decode('utf-8'),
            "foto_type": foto_type
        }).eq("nidn", nidn).execute()
        return True
    except Exception as e:
        st.error(f"Error upload foto: {e}")
        return False

def update_profil(nidn, nama_baru, deskripsi_baru):
    try:
        supabase.table("guru").update({"nama": nama_baru, "deskripsi": deskripsi_baru}).eq("nidn", nidn).execute()
        return True
    except Exception as e:
        st.error(f"Error update profil: {e}")
        return False

def get_siswa_by_kelas(kelas):
    try:
        response = supabase.table("siswa").select("*").eq("kelas", kelas).execute()
        return response.data if response.data else []
    except Exception:
        return []

def simpan_presensi(tanggal, nidn_guru, mata_kuliah, kelas, nisn_siswa, nama_siswa, jp_ke, status, semester="Genap 2025/2026"):
    try:
        data = {
            "tanggal": tanggal,
            "nidn_guru": nidn_guru,
            "mata_kuliah": mata_kuliah,
            "kelas": kelas,
            "nisn_siswa": nisn_siswa,
            "nama_siswa": nama_siswa,
            "jp_ke": jp_ke,
            "status": status,
            "semester": semester,
            "tahun_akademik": "2025/2026"
        }
        supabase.table("presensi").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error simpan: {e}")
        return False

def cek_sudah_presensi(tanggal, nidn_guru, kelas, jp_ke, mata_kuliah):
    try:
        response = supabase.table("presensi").select("*").eq("tanggal", tanggal).eq("nidn_guru", nidn_guru).eq("kelas", kelas).eq("jp_ke", jp_ke).eq("mata_kuliah", mata_kuliah).execute()
        return len(response.data) > 0
    except Exception:
        return False

def get_data_presensi(mata_kuliah, kelas, semester="Genap 2025/2026"):
    try:
        response = supabase.table("presensi").select("*").eq("mata_kuliah", mata_kuliah).eq("kelas", kelas).eq("semester", semester).execute()
        return response.data if response.data else []
    except Exception:
        return []

def hitung_pertemuan(data_presensi):
    if not data_presensi:
        return 0
    df = pd.DataFrame(data_presensi)
    return df['tanggal'].nunique()

# ==================== HALAMAN LOGIN ====================

if not st.session_state.logged_in:
    # Header kecil
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem 0;">
            <div style="background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%); width: 70px; height: 70px; border-radius: 20px; margin: 0 auto 1rem auto; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 2.5rem;">🌿</span>
            </div>
            <h1 style="color: #2E7D32; font-size: 2rem; margin-bottom: 0.25rem;">IPIM ACADEMIC</h1>
            <p style="color: #666;">Sistem Presensi Digital Terintegrasi</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Login Card
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("https://ui-avatars.com/api/?background=2E7D32&color=fff&bold=true&name=IPIM", width=120)
    with col2:
        st.markdown("""
        <h3 style="color: #2E7D32; margin-bottom: 0;">Selamat Datang</h3>
        <p style="color: #666; font-size: 0.85rem;">Masukkan NIDN dan Password untuk mengakses sistem presensi</p>
        """, unsafe_allow_html=True)
    
    nidn_input = st.text_input("NIDN", placeholder="Contoh: 1001", key="login_nidn")
    password_input = st.text_input("Password", type="password", placeholder="Masukkan password", key="login_pass")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tombol_login = st.button("🔐 Masuk ke Dashboard", use_container_width=True)
    
    if tombol_login:
        if nidn_input and password_input:
            with st.spinner("Memeriksa data..."):
                guru = login_guru(nidn_input, password_input)
                if guru:
                    st.session_state.logged_in = True
                    st.session_state.guru_data = guru
                    # Cek apakah guru punya multiple matkul
                    matkul_list = get_guru_matkul(nidn_input)
                    if len(matkul_list) > 1:
                        st.session_state.show_matkul_selector = True
                    st.rerun()
                else:
                    st.error("❌ NIDN atau Password salah!")
        else:
            st.warning("Silakan isi NIDN dan Password.")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #E0E0E0;">
        <p style="color: #999; font-size: 0.7rem;">Demo: NIDN 1001 | Password: 123456</p>
        <p style="color: #999; font-size: 0.7rem;">© 2026 IPIM ACADEMIC</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== HALAMAN UTAMA ====================

else:
    guru = st.session_state.guru_data
    
    # HEADER
    st.markdown(f"""
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1>🌿 Selamat Datang, {guru['nama']}</h1>
                <p>{guru.get('deskripsi', 'Dosen Pengampu')} | IPIM ACADEMIC Academic Year 2025/2026</p>
            </div>
            <div style="text-align: right;">
                <span class="badge-success">{datetime.now().strftime('%d %B %Y')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # SIDEBAR
    with st.sidebar:
        # Foto Profil
        col1, col2 = st.columns([1, 2])
        with col1:
            if guru.get('foto'):
                try:
                    foto_data = base64.b64decode(guru['foto'])
                    st.image(foto_data, width=80, output_format='auto')
                except:
                    st.image(f"https://ui-avatars.com/api/?background=2E7D32&color=fff&bold=true&name={guru['nama'].replace(' ', '+')}", width=80)
            else:
                st.image(f"https://ui-avatars.com/api/?background=2E7D32&color=fff&bold=true&name={guru['nama'].replace(' ', '+')}", width=80)
        
        with col2:
            st.markdown(f"""
            <div>
                <strong style="color: #2E7D32;">{guru['nama']}</strong><br>
                <span style="font-size: 0.75rem; color: #666;">{guru.get('deskripsi', 'Dosen')}</span><br>
                <span style="font-size: 0.7rem; color: #999;">NIDN: {guru['nidn']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Pilih Mata Kuliah (jika mengajar lebih dari 1)
        matkul_list = get_guru_matkul(guru['nidn'])
        if len(matkul_list) > 1:
            matkul_options = [f"{m[0]} - {m[1]}" for m in matkul_list]
            selected = st.selectbox("📚 Pilih Mata Kuliah", matkul_options)
            selected_matkul, selected_kelas = selected.split(" - ")
        else:
            selected_matkul = guru['mata_kuliah']
            selected_kelas = guru['kelas_diajar']
            st.info(f"📚 {selected_matkul}\n🏫 {selected_kelas}")
        
        st.divider()
        
        # Pilih JP
        st.subheader("⏰ Pilih Jam Pelajaran")
        jp_list = {
            1: "JP 1 (08:00 - 08:50)",
            2: "JP 2 (08:55 - 09:45)",
            3: "JP 3 (10:05 - 10:55)",
            4: "JP 4 (11:00 - 11:50)",
            5: "JP 5 (12:30 - 13:20)"
        }
        selected_jp = st.selectbox("Jam Pelajaran", options=list(jp_list.keys()), format_func=lambda x: jp_list[x])
        
        st.divider()
        
        # Edit Profil Section
        with st.expander("✏️ Edit Profil"):
            nama_baru = st.text_input("Nama", value=guru['nama'])
            deskripsi_baru = st.text_area("Jabatan", value=guru.get('deskripsi', 'Dosen Pengampu'))
            
            # Upload foto
            uploaded_file = st.file_uploader("Upload Foto Profil", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                if st.button("Simpan Foto"):
                    foto_bytes = uploaded_file.read()
                    if update_foto(guru['nidn'], foto_bytes, uploaded_file.type):
                        st.success("Foto berhasil diupload!")
                        st.rerun()
            
            if st.button("Simpan Profil"):
                if update_profil(guru['nidn'], nama_baru, deskripsi_baru):
                    st.success("Profil berhasil diupdate!")
                    guru['nama'] = nama_baru
                    guru['deskripsi'] = deskripsi_baru
                    st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.guru_data = None
            st.rerun()
    
    # MAIN CONTENT
    today = datetime.now().strftime('%Y-%m-%d')
    semester = "Genap 2025/2026"
    nidn_guru = guru['nidn']
    
    # Data presensi untuk rekap
    data_presensi = get_data_presensi(selected_matkul, selected_kelas, semester)
    total_pertemuan_terlaksana = hitung_pertemuan(data_presensi)
    total_pertemuan_seharusnya = 32
    
    # TABS
    tab1, tab2, tab3 = st.tabs(["📝 Presensi Harian", "📊 Laporan Semester", "📈 Statistik"])
    
    with tab1:
        st.markdown(f"""
        <div class="card">
            <h3 style="color: #2E7D32; margin-bottom: 0;">📖 {selected_matkul}</h3>
            <p style="color: #666;">🏫 {selected_kelas} | 📅 {datetime.now().strftime('%d %B %Y')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        sudah = cek_sudah_presensi(today, nidn_guru, selected_kelas, selected_jp, selected_matkul)
        
        if sudah:
            st.warning(f"⚠️ Anda sudah melakukan presensi untuk JP {selected_jp} hari ini!")
        else:
            siswa_list = get_siswa_by_kelas(selected_kelas)
            
            if not siswa_list:
                st.info("Belum ada data siswa. Silakan tambahkan di Supabase.")
            else:
                with st.form("form_presensi"):
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.write("### ✅ Beri Tanda Kehadiran Siswa")
                    
                    siswa_status = []
                    cols = st.columns(3)
                    
                    for idx, siswa in enumerate(siswa_list):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            status = st.selectbox(
                                f"📌 {siswa['nama_siswa']}",
                                options=["Hadir", "Sakit", "Izin", "Alpha"],
                                key=f"pres_{siswa['nisn']}"
                            )
                            siswa_status.append({
                                "nisn": siswa['nisn'],
                                "nama": siswa['nama_siswa'],
                                "status": status
                            })
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if st.form_submit_button("💾 Simpan Presensi", use_container_width=True):
                        success = 0
                        for s in siswa_status:
                            if simpan_presensi(today, nidn_guru, selected_matkul, selected_kelas, s["nisn"], s["nama"], selected_jp, s["status"], semester):
                                success += 1
                        if success == len(siswa_status):
                            st.success(f"✅ {success} data presensi tersimpan!")
                            st.rerun()
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📋 LAPORAN SEMESTER DOSEN
        
        | | |
        |---|---|
        | **Matakuliah** | {selected_matkul} |
        | **Pengampu** | {guru['nama']} |
        | **Kelas/Semester** | {selected_kelas} |
        | **Tahun Akademik** | 2025/2026 |
        """)
        
        st.markdown("---")
        st.markdown("### 📚 REKAP PERTEMUAN")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Jumlah Pertemuan Terlaksana", f"{total_pertemuan_terlaksana} kali")
        with col2:
            st.metric("Jumlah Pertemuan Seharusnya", f"{total_pertemuan_seharusnya} kali")
        
        if total_pertemuan_terlaksana < total_pertemuan_seharusnya:
            st.caption("⚠️ *Harap disesuaikan apabila terdapat pengurangan/perubahan jadwal karena kondisi tertentu*")
        
        st.markdown("---")
        st.markdown("### 📊 LAPORAN KEHADIRAN MAHASISWA/I")
        st.caption("*Mahasiswa yang memiliki ketidakhadiran selama semester berjalan*")
        
        if data_presensi:
            df = pd.DataFrame(data_presensi)
            
            rekap_alpha = df[df['status'] == 'Alpha'].groupby(['nama_siswa', 'nisn_siswa']).size().reset_index(name='alpha')
            rekap_sakit = df[df['status'] == 'Sakit'].groupby(['nama_siswa', 'nisn_siswa']).size().reset_index(name='sakit')
            rekap_izin = df[df['status'] == 'Izin'].groupby(['nama_siswa', 'nisn_siswa']).size().reset_index(name='izin')
            
            rekap = pd.merge(rekap_alpha, rekap_sakit, on=['nama_siswa', 'nisn_siswa'], how='outer').fillna(0)
            rekap = pd.merge(rekap, rekap_izin, on=['nama_siswa', 'nisn_siswa'], how='outer').fillna(0)
            rekap['total_tidak_hadir'] = rekap['alpha'] + rekap['sakit'] + rekap['izin']
            rekap = rekap[rekap['total_tidak_hadir'] > 0].sort_values('total_tidak_hadir', ascending=False)
            
            if not rekap.empty:
                for idx, row in rekap.iterrows():
                    st.write(f"{idx+1}. **{row['nama_siswa']}** : {int(row['total_tidak_hadir'])} kali tidak hadir")
            else:
                st.success("✅ Semua mahasiswa hadir 100%!")
            
            st.markdown("---")
            st.markdown("### ⚠️ Batas Minimal Kehadiran")
            
            total_mahasiswa = df['nama_siswa'].nunique()
            hadir_count = df[df['status'] == 'Hadir'].groupby('nama_siswa').size()
            if len(hadir_count) > 0 and total_pertemuan_terlaksana > 0:
                persentase_terendah = (hadir_count.min() / total_pertemuan_terlaksana * 100)
                if persentase_terendah < 75:
                    st.warning(f"⚠️ Mahasiswa dengan kehadiran terendah: **{hadir_count.idxmin()}** ({persentase_terendah:.1f}%)")
                else:
                    st.success(f"✅ Semua mahasiswa memenuhi batas minimal kehadiran (≥75%)")
        
        st.markdown("---")
        st.markdown("### 📝 CATATAN AKADEMIK / KENDALA PEMBELAJARAN")
        catatan = st.text_area("", placeholder="1. ........................................\n2. ........................................", height=100)
        
        st.markdown("---")
        st.caption(f"🗓️ Tanggal laporan: {datetime.now().strftime('%d %B %Y')}")
        
        if data_presensi and not rekap.empty:
            laporan_text = f"""
📌 LAPORAN SEMESTER DOSEN

Matakuliah: {selected_matkul}
Pengampu: {guru['nama']}
Kelas/Semester: {selected_kelas}
Tahun Akademik: 2025/2026

📚 REKAP PERTEMUAN
Jumlah pertemuan terlaksana: {total_pertemuan_terlaksana} kali
Jumlah pertemuan seharusnya: {total_pertemuan_seharusnya} kali

📊 LAPORAN KEHADIRAN MAHASISWA/I
"""
            for idx, row in rekap.iterrows():
                laporan_text += f"{idx+1}. {row['nama_siswa']}: {int(row['total_tidak_hadir'])} kali\n"
            
            laporan_text += f"""
⚠️ Batas minimal kehadiran: 75%

📝 CATATAN AKADEMIK / KENDALA PEMBELAJARAN
{catatan if catatan else '1. ........................................\n2. ....................................'}

🗓️ Tanggal laporan: {datetime.now().strftime('%d %B %Y')}
"""
            st.download_button("📥 Download Laporan (TXT)", laporan_text, f"laporan_{selected_matkul}_{selected_kelas}.txt", "text/plain")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📈 Statistik Kehadiran")
        
        if data_presensi:
            df = pd.DataFrame(data_presensi)
            
            col1, col2, col3, col4 = st.columns(4)
            status_counts = df['status'].value_counts()
            
            with col1:
                st.metric("✅ Hadir", status_counts.get('Hadir', 0))
            with col2:
                st.metric("🤒 Sakit", status_counts.get('Sakit', 0))
            with col3:
                st.metric("📝 Izin", status_counts.get('Izin', 0))
            with col4:
                st.metric("❌ Alpha", status_counts.get('Alpha', 0))
            
            fig = px.pie(values=status_counts.values, names=status_counts.index, title="Distribusi Kehadiran", color_discrete_sequence=['#4CAF50', '#FFC107', '#2196F3', '#F44336'])
            st.plotly_chart(fig, use_container_width=True)
            
            tren = df.groupby('tanggal')['status'].apply(lambda x: (x == 'Hadir').sum()).reset_index()
            tren.columns = ['tanggal', 'jumlah_hadir']
            fig2 = px.line(tren, x='tanggal', y='jumlah_hadir', title="Tren Kehadiran per Hari", color_discrete_sequence=['#2E7D32'])
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Belum ada data presensi untuk ditampilkan")
        
        st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #999; font-size: 0.7rem;">
    <hr style="margin-bottom: 1rem;">
    IPIM ACADEMIC - Academic Management System | © 2026 All Rights Reserved
</div>
""", unsafe_allow_html=True)
