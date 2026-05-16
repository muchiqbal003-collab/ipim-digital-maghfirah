import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# ========== KONFIGURASI SUPABASE (GANTI DENGAN MILIK ANDA) ==========
SUPABASE_URL = "https://mvhrnrvdhibdtvulmqkr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12aHJucnZkaGliZHR2dWxtcWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MTc5MjksImV4cCI6MjA5NDQ5MzkyOX0.IsS1wSXtGb0Keroc3UvsiVT38u-gea0_IVdAm1snBVw"
# ====================================================================

# Inisialisasi koneksi Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Sistem Presensi Dosen", layout="wide")
st.title("📋 Sistem Presensi Digital Dosen")

# Inisialisasi session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'guru_data' not in st.session_state:
    st.session_state.guru_data = None

# ==================== FUNGSI-FUNGSI ====================

def login_guru(nidn, password):
    """Fungsi untuk login guru"""
    try:
        response = supabase.table("guru").select("*").eq("nidn", nidn).eq("password", password).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error koneksi ke database: {e}")
        return None

def get_siswa_by_kelas(kelas):
    """Ambil daftar siswa berdasarkan kelas"""
    try:
        response = supabase.table("siswa").select("*").eq("kelas", kelas).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error ambil data siswa: {e}")
        return []

def simpan_presensi(tanggal, nidn_guru, mata_kuliah, kelas, nisn_siswa, nama_siswa, jp_ke, status):
    """Simpan data presensi"""
    try:
        data = {
            "tanggal": tanggal,
            "nidn_guru": nidn_guru,
            "mata_kuliah": mata_kuliah,
            "kelas": kelas,
            "nisn_siswa": nisn_siswa,
            "nama_siswa": nama_siswa,
            "jp_ke": jp_ke,
            "status": status
        }
        supabase.table("presensi").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error simpan presensi: {e}")
        return False

def cek_sudah_presensi(tanggal, nidn_guru, kelas, jp_ke):
    """Cek apakah sudah presensi untuk JP ini"""
    try:
        response = supabase.table("presensi").select("*").eq("tanggal", tanggal).eq("nidn_guru", nidn_guru).eq("kelas", kelas).eq("jp_ke", jp_ke).execute()
        return len(response.data) > 0
    except Exception as e:
        return False

def get_rekap_presensi(mata_kuliah, kelas):
    """Ambil rekap presensi per siswa"""
    try:
        response = supabase.table("presensi").select("*").eq("mata_kuliah", mata_kuliah).eq("kelas", kelas).execute()
        return response.data if response.data else []
    except Exception as e:
        return []

# ==================== HALAMAN LOGIN ====================

if not st.session_state.logged_in:
    st.subheader("🔐 Silakan Login")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        nidn_input = st.text_input("NIDN", placeholder="Contoh: 1001")
        password_input = st.text_input("Password", type="password", placeholder="Masukkan password")
        
        tombol_login = st.button("Login", type="primary")
        
        if tombol_login:
            if nidn_input and password_input:
                with st.spinner("Memeriksa data..."):
                    guru = login_guru(nidn_input, password_input)
                    
                    if guru:
                        st.session_state.logged_in = True
                        st.session_state.guru_data = guru
                        st.success(f"Selamat datang, {guru['nama']}!")
                        st.rerun()
                    else:
                        st.error("❌ NIDN atau Password salah! Silakan coba lagi.")
            else:
                st.warning("Silakan isi NIDN dan Password terlebih dahulu.")
    
    with col2:
        st.info("""
        **Demo Login:**
        - NIDN: `1001`
        - Password: `123456`
        
        Atau coba NIDN lain:
        - `1002` (Fisika)
        - `1003` (Kimia)
        - `1004` (Biologi)
        """)

# ==================== HALAMAN UTAMA (SETELAH LOGIN) ====================

else:
    guru = st.session_state.guru_data
    
    # SIDEBAR
    with st.sidebar:
        st.header(f"👤 {guru['nama']}")
        st.write(f"📚 **Mata Kuliah:** {guru['mata_kuliah']}")
        st.write(f"🏫 **Kelas:** {guru['kelas_diajar']}")
        st.write(f"🆔 **NIDN:** {guru['nidn']}")
        st.divider()
        
        # Pilihan Jam Pelajaran (JP)
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
        
        if st.button("🚪 Logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.guru_data = None
            st.rerun()
    
    # MAIN CONTENT
    today = datetime.now().strftime('%Y-%m-%d')
    hari_indonesia = {
        'Monday': 'Senin', 'Tuesday': 'Selasa', 'Wednesday': 'Rabu',
        'Thursday': 'Kamis', 'Friday': 'Jumat', 'Saturday': 'Sabtu', 'Sunday': 'Minggu'
    }
    hari_ini = hari_indonesia[datetime.now().strftime('%A')]
    
    st.header(f"📖 Presensi Kelas - {hari_ini}, {datetime.now().strftime('%d/%m/%Y')}")
    
    kelas_guru = guru['kelas_diajar']
    mata_kuliah = guru['mata_kuliah']
    nidn_guru = guru['nidn']
    
    # CEK SUDAH PRESENSI
    sudah = cek_sudah_presensi(today, nidn_guru, kelas_guru, selected_jp)
    
    if sudah:
        st.warning(f"⚠️ Anda **sudah melakukan presensi** untuk kelas {kelas_guru} pada JP {selected_jp} hari ini!")
    else:
        # Ambil daftar siswa
        siswa_list = get_siswa_by_kelas(kelas_guru)
        
        if not siswa_list:
            st.info(f"ℹ️ Belum ada data siswa untuk kelas {kelas_guru}")
            st.info("Silakan tambahkan data siswa terlebih dahulu di dashboard Supabase.")
        else:
            st.subheader(f"🏫 Kelas: {kelas_guru}")
            st.write(f"📚 Mata Kuliah: {mata_kuliah}")
            st.write(f"👨‍🏫 Dosen: {guru['nama']}")
            st.write(f"👨‍🎓 Jumlah Siswa: {len(siswa_list)} orang")
            st.divider()
            
            # FORM PRESENSI
            with st.form("form_presensi"):
                st.write("### ✅ Beri Tanda Kehadiran Siswa")
                
                # Tampilkan dalam 3 kolom
                siswa_status = []
                cols = st.columns(3)
                
                for idx, siswa in enumerate(siswa_list):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        status = st.selectbox(
                            f"📌 {siswa['nama_siswa']} (NISN: {siswa['nisn']})",
                            options=["Hadir", "Sakit", "Izin", "Alpha"],
                            key=f"siswa_{siswa['nisn']}"
                        )
                        siswa_status.append({
                            "nisn": siswa['nisn'],
                            "nama": siswa['nama_siswa'],
                            "status": status
                        })
                
                st.divider()
                submit = st.form_submit_button("💾 Simpan Semua Presensi", type="primary")
                
                if submit:
                    success_count = 0
                    with st.spinner("Menyimpan data presensi..."):
                        for s in siswa_status:
                            if simpan_presensi(today, nidn_guru, mata_kuliah, kelas_guru, s["nisn"], s["nama"], selected_jp, s["status"]):
                                success_count += 1
                    
                    if success_count == len(siswa_status):
                        st.success(f"✅ Berhasil menyimpan {success_count} data presensi!")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ Tersimpan {success_count} dari {len(siswa_status)} data.")
    
    # ==================== REKAP PRESENSI ====================
    st.divider()
    st.header("📊 Rekap Kehadiran Siswa")
    
    data_presensi = get_rekap_presensi(mata_kuliah, kelas_guru)
    
    if data_presensi:
        df = pd.DataFrame(data_presensi)
        
        # Hitung rekap per siswa
        rekap = df.groupby(['nisn_siswa', 'nama_siswa']).agg(
            total_hadir=('status', lambda x: (x == 'Hadir').sum()),
            total_sakit=('status', lambda x: (x == 'Sakit').sum()),
            total_izin=('status', lambda x: (x == 'Izin').sum()),
            total_alpha=('status', lambda x: (x == 'Alpha').sum())
        ).reset_index()
        
        # Hitung total pertemuan dan persentase
        rekap['total_pertemuan'] = rekap['total_hadir'] + rekap['total_sakit'] + rekap['total_izin'] + rekap['total_alpha']
        rekap['persentase'] = rekap.apply(
            lambda row: round((row['total_hadir'] / row['total_pertemuan'] * 100), 1) if row['total_pertemuan'] > 0 else 0,
            axis=1
        )
        
        # Sorting berdasarkan persentase
        rekap = rekap.sort_values('persentase', ascending=False)
        
        # Tampilkan
        st.dataframe(rekap, use_container_width=True)
        
        # Download button
        csv = rekap.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Rekap (CSV)",
            csv,
            f"rekap_{mata_kuliah}_{kelas_guru}_{today}.csv",
            "text/csv"
        )
    else:
        st.info("ℹ️ Belum ada data presensi untuk mata kuliah ini.")
