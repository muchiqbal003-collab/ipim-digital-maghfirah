import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import plotly.express as px

# ========== KONFIGURASI SUPABASE ==========
SUPABASE_URL = "https://mvhrnrvdhibdtvulmqkr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12aHJucnZkaGliZHR2dWxtcWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MTc5MjksImV4cCI6MjA5NDQ5MzkyOX0.IsS1wSXtGb0Keroc3UvsiVT38u-gea0_IVdAm1snBVw"
# ==========================================

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Konfigurasi halaman
st.set_page_config(page_title="IPIM ACADEMIC - Presensi Digital", layout="wide", initial_sidebar_state="expanded")

# Custom CSS untuk tampilan profesional
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0D8ABC 0%, #0a5a7a 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .stat-box {
        background: #f0f2f5;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .warning-text {
        color: #e74c3c;
        font-weight: bold;
    }
    .success-text {
        color: #27ae60;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header aplikasi
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="main-header" style="text-align: center;">
        <h1>📚 IPIM ACADEMIC</h1>
        <p>Sistem Presensi Digital | Academic Year 2025/2026</p>
    </div>
    """, unsafe_allow_html=True)

# Inisialisasi session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'guru_data' not in st.session_state:
    st.session_state.guru_data = None
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

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

def cek_sudah_presensi(tanggal, nidn_guru, kelas, jp_ke):
    try:
        response = supabase.table("presensi").select("*").eq("tanggal", tanggal).eq("nidn_guru", nidn_guru).eq("kelas", kelas).eq("jp_ke", jp_ke).execute()
        return len(response.data) > 0
    except Exception:
        return False

def get_data_presensi(mata_kuliah, kelas, semester="Genap 2025/2026"):
    try:
        response = supabase.table("presensi").select("*").eq("mata_kuliah", mata_kuliah).eq("kelas", kelas).eq("semester", semester).execute()
        return response.data if response.data else []
    except Exception:
        return []

def hitung_pertemuan(data_presensi, jp_per_hari=5):
    """Hitung jumlah pertemuan yang terlaksana"""
    if not data_presensi:
        return 0
    # Ambil tanggal unik
    df = pd.DataFrame(data_presensi)
    tanggal_unik = df['tanggal'].nunique()
    return tanggal_unik

# ==================== HALAMAN LOGIN ====================

if not st.session_state.logged_in:
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 60vh;">
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1); width: 400px;">
            <h2 style="text-align: center; color: #0D8ABC;">🔐 Login Dosen</h2>
            <p style="text-align: center; color: #666;">Masukkan NIDN dan Password Anda</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        nidn_input = st.text_input("NIDN", placeholder="Contoh: 1001")
        password_input = st.text_input("Password", type="password", placeholder="Masukkan password")
        
        tombol_login = st.button("Login", use_container_width=True)
        
        if tombol_login:
            if nidn_input and password_input:
                with st.spinner("Memeriksa data..."):
                    guru = login_guru(nidn_input, password_input)
                    if guru:
                        st.session_state.logged_in = True
                        st.session_state.guru_data = guru
                        st.rerun()
                    else:
                        st.error("❌ NIDN atau Password salah!")
            else:
                st.warning("Silakan isi NIDN dan Password.")
    
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; color: #999; font-size: 12px;">
        <p>IPIM ACADEMIC - Academic Management System</p>
        <p>© 2026 All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== HALAMAN UTAMA ====================

else:
    guru = st.session_state.guru_data
    
    # SIDEBAR PROFIL
    with st.sidebar:
        # Foto profil
        foto_url = guru.get('foto_url', f"https://ui-avatars.com/api/?background=0D8ABC&color=fff&name={guru['nama'].replace(' ', '+')}")
        st.image(foto_url, width=100)
        
        st.markdown(f"""
        <div style="text-align: center;">
            <h3>{guru['nama']}</h3>
            <p style="color: #666;">{guru.get('deskripsi', 'Dosen Pengampu')}</p>
            <hr>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"📚 **Mata Kuliah:** {guru['mata_kuliah']}")
        st.write(f"🏫 **Kelas:** {guru['kelas_diajar']}")
        st.write(f"🆔 **NIDN:** {guru['nidn']}")
        
        st.divider()
        
        # Edit profil
        if st.button("✏️ Edit Profil", use_container_width=True):
            st.session_state.edit_mode = not st.session_state.edit_mode
        
        if st.session_state.edit_mode:
            with st.form("edit_profil"):
                nama_baru = st.text_input("Nama Lengkap", value=guru['nama'])
                deskripsi_baru = st.text_area("Deskripsi/Jabatan", value=guru.get('deskripsi', 'Dosen Pengampu'))
                if st.form_submit_button("Simpan Perubahan"):
                    if update_profil(guru['nidn'], nama_baru, deskripsi_baru):
                        st.success("Profil berhasil diupdate!")
                        guru['nama'] = nama_baru
                        guru['deskripsi'] = deskripsi_baru
                        st.session_state.guru_data = guru
                        st.rerun()
        
        st.divider()
        
        # Pilihan JP
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
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.guru_data = None
            st.rerun()
    
    # MAIN CONTENT
    today = datetime.now().strftime('%Y-%m-%d')
    semester = "Genap 2025/2026"
    kelas_guru = guru['kelas_diajar']
    mata_kuliah = guru['mata_kuliah']
    nidn_guru = guru['nidn']
    
    # Ambil data presensi untuk rekap
    data_presensi = get_data_presensi(mata_kuliah, kelas_guru, semester)
    
    # Hitung statistik
    total_pertemuan_terlaksana = hitung_pertemuan(data_presensi)
    total_pertemuan_seharusnya = 32  # Bisa disesuaikan
    
    # TABS
    tab1, tab2, tab3 = st.tabs(["📝 Presensi Harian", "📊 Rekap Semester", "📈 Statistik"])
    
    with tab1:
        st.header(f"📖 Presensi Kelas - {kelas_guru}")
        st.write(f"📚 Mata Kuliah: {mata_kuliah}")
        st.write(f"📅 Tanggal: {datetime.now().strftime('%d %B %Y')}")
        
        sudah = cek_sudah_presensi(today, nidn_guru, kelas_guru, selected_jp)
        
        if sudah:
            st.warning(f"⚠️ Anda sudah melakukan presensi untuk JP {selected_jp} hari ini!")
        else:
            siswa_list = get_siswa_by_kelas(kelas_guru)
            
            if not siswa_list:
                st.info("Belum ada data siswa untuk kelas ini. Silakan tambahkan di Supabase.")
            else:
                with st.form("form_presensi"):
                    st.write("### ✅ Beri Tanda Kehadiran Siswa")
                    
                    siswa_status = []
                    cols = st.columns(3)
                    
                    for idx, siswa in enumerate(siswa_list):
                        col_idx = idx % 3
                        with cols[col_idx]:
                            status = st.selectbox(
                                f"{siswa['nama_siswa']}",
                                options=["Hadir", "Sakit", "Izin", "Alpha"],
                                key=f"pres_{siswa['nisn']}"
                            )
                            siswa_status.append({
                                "nisn": siswa['nisn'],
                                "nama": siswa['nama_siswa'],
                                "status": status
                            })
                    
                    if st.form_submit_button("💾 Simpan Presensi", use_container_width=True):
                        success = 0
                        for s in siswa_status:
                            if simpan_presensi(today, nidn_guru, mata_kuliah, kelas_guru, s["nisn"], s["nama"], selected_jp, s["status"], semester):
                                success += 1
                        if success == len(siswa_status):
                            st.success(f"✅ {success} data presensi tersimpan!")
                            st.rerun()
    
    with tab2:
        st.header("📋 LAPORAN SEMESTER DOSEN")
        st.markdown("---")
        
        # Header laporan
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **Matakuliah:** {mata_kuliah}  
            **Pengampu:** {guru['nama']}  
            **Kelas/Semester:** {kelas_guru}  
            **Tahun Akademik:** 2025/2026
            """)
        with col2:
            st.markdown(f"""
            **Jumlah SKS:** 3  
            **Semester:** Genap  
            **Program Studi:** Pendidikan Agama Islam
            """)
        
        st.markdown("---")
        
        # Rekap pertemuan
        st.subheader("📚 REKAP PERTEMUAN")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Jumlah Pertemuan Terlaksana", f"{total_pertemuan_terlaksana} kali")
        with col2:
            st.metric("Jumlah Pertemuan Seharusnya", f"{total_pertemuan_seharusnya} kali")
        
        if total_pertemuan_terlaksana < total_pertemuan_seharusnya:
            st.caption("⚠️ *Harap disesuaikan apabila terdapat pengurangan/perubahan jadwal karena kondisi tertentu*")
        
        st.markdown("---")
        
        # Laporan kehadiran mahasiswa
        st.subheader("📊 LAPORAN KEHADIRAN MAHASISWA/I")
        st.caption("*Dicantumkan mahasiswa yang memiliki ketidakhadiran selama semester berjalan*")
        
        if data_presensi:
            df = pd.DataFrame(data_presensi)
            
            # Hitung ketidakhadiran per siswa
            rekap_alpha = df[df['status'] == 'Alpha'].groupby(['nama_siswa', 'nisn_siswa']).size().reset_index(name='alpha')
            rekap_sakit = df[df['status'] == 'Sakit'].groupby(['nama_siswa', 'nisn_siswa']).size().reset_index(name='sakit')
            rekap_izin = df[df['status'] == 'Izin'].groupby(['nama_siswa', 'nisn_siswa']).size().reset_index(name='izin')
            
            # Gabungkan
            rekap = pd.merge(rekap_alpha, rekap_sakit, on=['nama_siswa', 'nisn_siswa'], how='outer').fillna(0)
            rekap = pd.merge(rekap, rekap_izin, on=['nama_siswa', 'nisn_siswa'], how='outer').fillna(0)
            rekap['total_tidak_hadir'] = rekap['alpha'] + rekap['sakit'] + rekap['izin']
            rekap = rekap[rekap['total_tidak_hadir'] > 0].sort_values('total_tidak_hadir', ascending=False)
            
            if not rekap.empty:
                for idx, row in rekap.iterrows():
                    st.write(f"{idx+1}. **{row['nama_siswa']}** : {int(row['total_tidak_hadir'])} kali tidak hadir (Alpha: {int(row['alpha'])}, Sakit: {int(row['sakit'])}, Izin: {int(row['izin'])})")
                
                # Batas minimal kehadiran
                st.markdown("---")
                st.subheader("⚠️ Batas Minimal Kehadiran")
                
                # Hitung persentase kehadiran
                total_mahasiswa = df['nama_siswa'].nunique()
                hadir_count = df[df['status'] == 'Hadir'].groupby('nama_siswa').size()
                persentase_terendah = (hadir_count.min() / total_pertemuan_terlaksana * 100) if total_pertemuan_terlaksana > 0 else 0
                
                if persentase_terendah < 75:
                    st.warning(f"⚠️ Batas minimal kehadiran: **75%**")
                    st.warning(f"⚠️ Mahasiswa dengan kehadiran terendah: **{hadir_count.idxmin()}** ({persentase_terendah:.1f}%)")
                else:
                    st.success(f"✅ Semua mahasiswa memenuhi batas minimal kehadiran (≥75%)")
            else:
                st.info("✅ Semua mahasiswa hadir 100% selama semester berjalan!")
        else:
            st.info("Belum ada data presensi untuk semester ini.")
        
        st.markdown("---")
        
        # Catatan akademik
        st.subheader("📝 CATATAN AKADEMIK / KENDALA PEMBELAJARAN")
        catatan = st.text_area("", placeholder="1. ........................................\n2. ........................................", height=100)
        
        st.markdown("---")
        st.caption(f"🗓️ Tanggal laporan: {datetime.now().strftime('%d %B %Y')}")
        
        # Tombol download
        if data_presensi:
            # Generate laporan lengkap
            laporan_text = f"""
📌 LAPORAN SEMESTER DOSEN

Matakuliah: {mata_kuliah}
Jumlah SKS: 3
Pengampu: {guru['nama']}
Kelas/Semester: {kelas_guru}
Tahun Akademik: 2025/2026

📚 REKAP PERTEMUAN
Jumlah pertemuan terlaksana: {total_pertemuan_terlaksana} kali
Jumlah pertemuan seharusnya: {total_pertemuan_seharusnya} kali
(harap disesuaikan apabila terdapat pengurangan/perubahan jadwal karena kondisi tertentu)

📊 LAPORAN KEHADIRAN MAHASISWA/I
(dicantumkan mahasiswa yang memiliki ketidakhadiran selama semester berjalan)

"""
            for idx, row in rekap.iterrows():
                laporan_text += f"{idx+1}. {row['nama_siswa']}: {int(row['total_tidak_hadir'])} kali\n"
            
            laporan_text += f"""
⚠️ Batas minimal kehadiran: 75%

📝 CATATAN AKADEMIK / KENDALA PEMBELAJARAN
(dicantumkan apabila ada)

{catatan if catatan else '1. ........................................\n2. ....................................'}

🗓️ Tanggal laporan: {datetime.now().strftime('%d %B %Y')}
"""
            
            st.download_button(
                "📥 Download Laporan Semester (TXT)",
                laporan_text,
                f"laporan_{mata_kuliah}_{kelas_guru}_semester.txt",
                "text/plain",
                use_container_width=True
            )
    
    with tab3:
        st.header("📈 Statistik Kehadiran")
        
        if data_presensi:
            df = pd.DataFrame(data_presensi)
            
            # Statistik per status
            status_counts = df['status'].value_counts()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ Hadir", status_counts.get('Hadir', 0))
            with col2:
                st.metric("🤒 Sakit", status_counts.get('Sakit', 0))
            with col3:
                st.metric("📝 Izin", status_counts.get('Izin', 0))
            with col4:
                st.metric("❌ Alpha", status_counts.get('Alpha', 0))
            
            # Grafik pie
            fig = px.pie(values=status_counts.values, names=status_counts.index, title="Distribusi Status Kehadiran")
            st.plotly_chart(fig, use_container_width=True)
            
            # Grafik tren
            tren = df.groupby('tanggal')['status'].apply(lambda x: (x == 'Hadir').sum()).reset_index()
            tren.columns = ['tanggal', 'jumlah_hadir']
            fig2 = px.line(tren, x='tanggal', y='jumlah_hadir', title="Tren Kehadiran per Hari")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Belum ada data untuk ditampilkan")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 1rem; background: #f0f2f5; border-radius: 10px; color: #666;">
    <small>IPIM ACADEMIC - Academic Management System | © 2026 All Rights Reserved</small>
</div>
""", unsafe_allow_html=True)
