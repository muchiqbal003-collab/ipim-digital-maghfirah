import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# ========== GANTI DENGAN MILIK ANDA ==========
SUPABASE_URL = "https://mvhrnrvdhibdtvulmqkr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12aHJucnZkaGliZHR2dWxtcWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MTc5MjksImV4cCI6MjA5NDQ5MzkyOX0.IsS1wSXtGb0Keroc3UvsiVT38u-gea0_IVdAm1snBVw"
# ============================================

# Koneksi ke Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Konfigurasi halaman
st.set_page_config(page_title="Presensi Digital Dosen", layout="wide")
st.title("📋 Presensi Digital Dosen")

# Inisialisasi session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'guru_data' not in st.session_state:
    st.session_state.guru_data = None

# Fungsi login
def do_login(nidn, password):
    response = supabase.table("guru").select("*").eq("nidn", nidn).eq("password", password).execute()
    if response.data:
        return response.data[0]
    return None

# Fungsi ambil siswa per kelas
def get_siswa_by_kelas(kelas):
    response = supabase.table("siswa").select("*").eq("kelas", kelas).execute()
    return response.data

# Fungsi simpan presensi
def save_presensi(tanggal, nidn_guru, mata_kuliah, kelas, nisn_siswa, nama_siswa, jp_ke, status):
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

# Fungsi cek sudah presensi
def sudah_presensi(tanggal, nidn_guru, kelas, jp_ke):
    response = supabase.table("presensi").select("*").eq("tanggal", tanggal).eq("nidn_guru", nidn_guru).eq("kelas", kelas).eq("jp_ke", jp_ke).execute()
    return len(response.data) > 0

# ==================== HALAMAN LOGIN ====================
if not st.session_state.logged_in:
    st.subheader("🔐 Login Dosen")
    
    col1, col2 = st.columns(2)
    with col1:
        nidn = st.text_input("NIDN")
        password = st.text_input("Password", type="password")
        login_btn = st.button("Login")
    
    if login_btn:
        guru = do_login(nidn, password)
        if guru:
            st.session_state.logged_in = True
            st.session_state.guru_data = guru
            st.rerun()
        else:
            st.error("NIDN atau Password salah!")
    
    st.info("💡 Demo: NIDN 1001, Password 123456")

# ==================== HALAMAN UTAMA ====================
else:
    # SIDEBAR
    with st.sidebar:
        st.header(f"👋 {st.session_state.guru_data['nama']}")
        st.write(f"📚 {st.session_state.guru_data['mata_kuliah']}")
        st.write(f"🏫 {st.session_state.guru_data['kelas_diajar']}")
        st.divider()
        
        # Pilih JP (Jam Pelajaran)
        jp_options = {1: "JP 1 (08:00-08:50)", 2: "JP 2 (08:55-09:45)", 3: "JP 3 (10:05-10:55)", 4: "JP 4 (11:00-11:50)", 5: "JP 5 (12:30-13:20)"}
        selected_jp = st.selectbox("Pilih Jam Pelajaran", options=list(jp_options.keys()), format_func=lambda x: jp_options[x])
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.guru_data = None
            st.rerun()
    
    # MAIN CONTENT
    today = datetime.now().strftime('%Y-%m-%d')
    hari_ini = datetime.now().strftime('%A')
    hari_map = {'Monday':'Senin', 'Tuesday':'Selasa', 'Wednesday':'Rabu', 'Thursday':'Kamis', 'Friday':'Jumat', 'Saturday':'Sabtu', 'Sunday':'Minggu'}
    
    st.header(f"📖 Presensi Kelas - {hari_map[hari_ini]}, {datetime.now().strftime('%d/%m/%Y')}")
    
    kelas_guru = st.session_state.guru_data['kelas_diajar']
    mata_kuliah = st.session_state.guru_data['mata_kuliah']
    nidn_guru = st.session_state.guru_data['nidn']
    
    # Cek apakah sudah presensi untuk JP ini
    sudah = sudah_presensi(today, nidn_guru, kelas_guru, selected_jp)
    
    if sudah:
        st.warning(f"⚠️ Anda sudah melakukan presensi untuk {kelas_guru} pada JP {selected_jp} hari ini!")
    else:
        # Ambil daftar siswa di kelas ini
        siswa_list = get_siswa_by_kelas(kelas_guru)
        
        if not siswa_list:
            st.info(f"Belum ada data siswa untuk kelas {kelas_guru}")
        else:
            st.subheader(f"🏫 Kelas: {kelas_guru}")
            st.write(f"📚 Mata Kuliah: {mata_kuliah}")
            st.write(f"👨‍🏫 Dosen: {st.session_state.guru_data['nama']}")
            
            st.divider()
            
            # Form presensi
            with st.form("form_presensi"):
                st.write("### ✅ Beri Tanda Kehadiran Siswa")
                
                # Buat 3 kolom untuk tampilan yang rapi
                cols_per_row = 3
                siswa_buttons = []
                
                for i, siswa in enumerate(siswa_list):
                    col = st.columns(cols_per_row)[i % cols_per_row]
                    with col:
                        status = st.selectbox(
                            f"{siswa['nama_siswa']} (NISN: {siswa['nisn']})",
                            options=["Hadir", "Sakit", "Izin", "Alpha"],
                            key=f"siswa_{siswa['nisn']}"
                        )
                        siswa_buttons.append({
                            "nisn": siswa['nisn'],
                            "nama": siswa['nama_siswa'],
                            "status": status
                        })
                
                submit = st.form_submit_button("💾 Simpan Semua Presensi")
                
                if submit:
                    for s in siswa_buttons:
                        save_presensi(today, nidn_guru, mata_kuliah, kelas_guru, s["nisn"], s["nama"], selected_jp, s["status"])
                    st.success("✅ Semua presensi berhasil disimpan!")
                    st.rerun()
    
    # ==================== REKAP ====================
    st.divider()
    st.header("📊 Rekap Kehadiran Siswa")
    
    # Ambil semua presensi untuk mata kuliah ini
    response = supabase.table("presensi").select("*").eq("mata_kuliah", mata_kuliah).eq("kelas", kelas_guru).execute()
    data_presensi = response.data
    
    if data_presensi:
        df = pd.DataFrame(data_presensi)
        
        # Hitung rekap per siswa
        rekap = df.groupby(['nisn_siswa', 'nama_siswa']).agg(
            total_hadir=('status', lambda x: (x == 'Hadir').sum()),
            total_sakit=('status', lambda x: (x == 'Sakit').sum()),
            total_izin=('status', lambda x: (x == 'Izin').sum()),
            total_alpha=('status', lambda x: (x == 'Alpha').sum())
        ).reset_index()
        
        total_jp = rekap[['total_hadir', 'total_sakit', 'total_izin', 'total_alpha']].sum(axis=1)
        rekap['persentase'] = (rekap['total_hadir'] / total_jp * 100).round(1).fillna(0).astype(str) + '%'
        rekap['total_pertemuan'] = total_jp
        
        # Urutkan dari persentase tertinggi
        rekap['persentase_angka'] = rekap['persentase'].str.replace('%', '').astype(float)
        rekap = rekap.sort_values('persentase_angka', ascending=False)
        rekap = rekap.drop(columns=['persentase_angka'])
        
        st.dataframe(rekap, use_container_width=True)
        
        # Download Excel
        csv = rekap.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Rekap (CSV)", csv, f"rekap_{mata_kuliah}_{kelas_guru}.csv", "text/csv")
    else:
        st.info("Belum ada data presensi untuk mata kuliah ini")
