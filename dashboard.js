const SUPABASE_URL = 'https://mvhrnrvdhibdtvulmqkr.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12aHJucnZkaGliZHR2dWxtcWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MTc5MjksImV4cCI6MjA5NDQ5MzkyOX0.IsS1wSXtGb0Keroc3UvsiVT38u-gea0_IVdAm1snBVw'

const supabaseDashboard = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

var dosen = JSON.parse(localStorage.getItem('dosen'))

if (!dosen) {
    window.location.href = 'index.html'
}

document.getElementById('namaDosen').textContent = '👤 ' + dosen.nama
document.getElementById('namaDosenBig').textContent = dosen.gelar + ' ' + dosen.nama
document.getElementById('gelarDosen').textContent = dosen.gelar || ''

function getHariIni() {
    var hari = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']
    return hari[new Date().getDay()]
}

async function loadJadwal() {
    try {
        var hariIni = getHariIni()

        var { data, error } = await supabaseDashboard
            .from('jadwal')
            .select('id, jam_mulai, jam_selesai, ruangan, mata_kuliah(nama_mk), kelas(nama_kelas)')
            .eq('dosen_id', dosen.id)
            .eq('hari', hariIni)
            .order('jam_mulai')

        if (error) throw error

        var jadwalList = document.getElementById('jadwalList')

        if (!data || data.length === 0) {
            jadwalList.innerHTML = '<p style="text-align: center; padding: 30px; color: #999;">🎉 Tidak ada jadwal mengajar hari ini</p>'
            return
        }

        jadwalList.innerHTML = ''

        for (var i = 0; i < data.length; i++) {
            var j = data[i]
            var card = document.createElement('div')
            card.className = 'jadwal-card'
            card.innerHTML = `
                <div class="jadwal-info">
                    <h4>📚 ${j.mata_kuliah.nama_mk}</h4>
                    <p>🏫 Kelas: ${j.kelas.nama_kelas} | ⏰ ${j.jam_mulai.substring(0,5)} - ${j.jam_selesai.substring(0,5)}</p>
                    <p>📍 ${j.ruangan || 'Ruangan belum ditentukan'}</p>
                </div>
                <button class="btn-absen" data-jadwalid="${j.id}">
                    📋 Absensi
                </button>
            `
            jadwalList.appendChild(card)
        }

        var btnAbsenList = document.querySelectorAll('.btn-absen')
        for (var k = 0; k < btnAbsenList.length; k++) {
            btnAbsenList[k].addEventListener('click', function() {
                localStorage.setItem('jadwalAktif', this.getAttribute('data-jadwalid'))
                window.location.href = 'absensi.html'
            })
        }

    } catch (error) {
        console.error('Error load jadwal:', error.message)
        document.getElementById('jadwalList').innerHTML = '<p style="text-align: center; padding: 30px; color: #dc3545;">⚠️ Gagal memuat jadwal</p>'
    }
}

document.getElementById('btnLogout').addEventListener('click', function() {
    localStorage.removeItem('dosen')
    window.location.href = 'index.html'
})

loadJadwal()