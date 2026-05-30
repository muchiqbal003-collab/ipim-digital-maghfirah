const SUPABASE_URL = 'https://mvhrnrvdhibdtvulmqkr.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im12aHJucnZkaGliZHR2dWxtcWtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5MTc5MjksImV4cCI6MjA5NDQ5MzkyOX0.IsS1wSXtGb0Keroc3UvsiVT38u-gea0_IVdAm1snBVw'

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

async function login(username, password) {
    try {
        const { data, error } = await supabase
            .from('dosen')
            .select('*')
            .eq('username', username)
            .single()

        if (error || !data) {
            return { success: false, message: 'Username tidak ditemukan!' }
        }

        if (data.password !== password) {
            return { success: false, message: 'Password salah!' }
        }

        localStorage.setItem('dosen', JSON.stringify(data))
        return { success: true, data: data }

    } catch (error) {
        console.error('Error login:', error.message)
        return { success: false, message: 'Terjadi kesalahan!' }
    }
}

document.getElementById('formLogin').addEventListener('submit', async function(e) {
    e.preventDefault()

    const username = document.getElementById('username').value.trim()
    const password = document.getElementById('password').value.trim()
    const pesanError = document.getElementById('pesanError')

    pesanError.style.display = 'none'

    const btnLogin = this.querySelector('.btn-login')
    btnLogin.disabled = true
    btnLogin.innerHTML = '⏳ Memeriksa...'

    const result = await login(username, password)

    if (result.success) {
        btnLogin.innerHTML = '✅ Berhasil!'
        setTimeout(function() {
            window.location.href = 'dashboard.html'
        }, 1000)
    } else {
        pesanError.textContent = '⚠️ ' + result.message
        pesanError.style.display = 'block'
        btnLogin.disabled = false
        btnLogin.innerHTML = '🔐 Masuk'
    }
})