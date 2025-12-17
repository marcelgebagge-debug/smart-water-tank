import streamlit as st
import time
import random
import json
import os

# ==========================================
# 1. KONFIGURASI SISTEM
# ==========================================
PAKAI_FIREBASE_ASLI = True 
URL_DATABASE = 'https://smart-water-tank-f1b98-default-rtdb.asia-southeast1.firebasedatabase.app'

st.set_page_config(page_title="Smart Water Tank Dashboard", layout="wide", page_icon="💧")

# ==========================================
# 2. LIBRARY CHECK (SAFE MODE)
# ==========================================
try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    st.error("⚠️ Library 'firebase-admin' belum terinstall.")

try:
    from streamlit_autorefresh import st_autorefresh
    AUTO_REFRESH_INSTALLED = True
except ImportError:
    AUTO_REFRESH_INSTALLED = False
    # Tidak error, cuma warning kecil di console

# ==========================================
# 3. KONEKSI FIREBASE (SMART HYBRID)
# ==========================================
firebase_app = None

if PAKAI_FIREBASE_ASLI and FIREBASE_AVAILABLE:
    try:
        if not firebase_admin._apps:
            # A. Cek Secrets (Prioritas: Cloud)
            if "firebase" in st.secrets:
                key_dict = json.loads(st.secrets["firebase"]["text_key"])
                cred = credentials.Certificate(key_dict)
            
            # B. Cek File Lokal (Prioritas: Laptop)
            elif os.path.exists("serviceAccountKey.json"):
                cred = credentials.Certificate("serviceAccountKey.json")
            
            else:
                st.error("❌ Kunci Akses (JSON) tidak ditemukan.")
                st.stop()

            firebase_app = firebase_admin.initialize_app(cred, {
                'databaseURL': URL_DATABASE
            })
        else:
            firebase_app = firebase_admin.get_app()
    except Exception as e:
        st.error(f"❌ Error Koneksi: {str(e)}")
        PAKAI_FIREBASE_ASLI = False

# ==========================================
# 4. INISIALISASI STATE
# ==========================================
if 'dummy_data' not in st.session_state:
    st.session_state.dummy_data = {
        'control': {'mode': 'AUTO', 'manual_pump': False},
        'sensor': {'water_level': 50.0, 'pressure': 0.5},
        'status': {'pump': False}
    }
if 'show_dashboard' not in st.session_state:
    st.session_state.show_dashboard = False

# ==========================================
# 5. LOGIKA DATA (GET & SET)
# ==========================================
def get_data():
    if not PAKAI_FIREBASE_ASLI: return None
    try: return db.reference('/').get()
    except: return None

def set_data(path, value):
    if not PAKAI_FIREBASE_ASLI: return False
    try: 
        db.reference(path).set(value)
        return True
    except: return False

def sync_data():
    """Sinkronisasi data realtime"""
    real_data = get_data()
    if real_data:
        # Update dummy_data agar UI sinkron
        for section in ['control', 'sensor', 'status']:
            if section in real_data:
                if section not in st.session_state.dummy_data:
                    st.session_state.dummy_data[section] = {}
                st.session_state.dummy_data[section].update(real_data[section])
    else:
        # Jika firebase kosong/baru, push default data
        set_data('/', st.session_state.dummy_data)

def update_pump_toggle():
    """Callback khusus untuk Toggle Switch"""
    # Ambil nilai baru dari state widget toggle
    new_state = st.session_state['toggle_pump']
    
    # Kirim ke Firebase
    if PAKAI_FIREBASE_ASLI:
        set_data('/control/manual_pump', new_state)
        set_data('/status/pump', new_state)
    
    # Update state lokal
    st.session_state.dummy_data['control']['manual_pump'] = new_state
    st.session_state.dummy_data['status']['pump'] = new_state

def update_mode():
    """Callback untuk Radio Button Mode"""
    new_mode = st.session_state['radio_mode']
    if PAKAI_FIREBASE_ASLI:
        set_data('/control/mode', new_mode)
    st.session_state.dummy_data['control']['mode'] = new_mode

# ==========================================
# 6. STYLING CSS (CUSTOM VISUAL TANK)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * { font-family: 'Poppins', sans-serif !important; }

    /* Background Aplikasi */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0f2027 0%, #203a43 90%, #2c5364 100%);
        color: white;
    }

    /* GLASSMORPHISM CARD */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(76, 201, 240, 0.4);
    }

    /* JUDUL */
    .main-title {
        font-size: 2.5rem; font-weight: 700; text-align: center;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center; color: #a8b0c5; letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 40px;
    }

    /* VISUALISASI TANGKI AIR (CSS PURE) */
    .tank-wrapper {
        display: flex; justify-content: center; align-items: center; height: 320px;
    }
    .tank-body {
        position: relative;
        width: 160px; height: 280px;
        background: rgba(255, 255, 255, 0.05);
        border: 4px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        overflow: hidden;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }
    /* Air di dalam tangki */
    .water {
        position: absolute; bottom: 0; left: 0; width: 100%;
        background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%);
        transition: height 0.8s ease-in-out; /* Animasi naik turun halus */
        box-shadow: 0 0 20px #00f2fe;
    }
    /* Garis ukur */
    .measurement-line {
        position: absolute; width: 100%; height: 1px; background: rgba(255,255,255,0.2);
        left: 0;
    }
    /* Label Persentase di Tengah Air */
    .water-label {
        position: absolute; width: 100%; text-align: center;
        top: 50%; transform: translateY(-50%);
        font-size: 1.5rem; font-weight: bold; color: rgba(255,255,255,0.8);
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        z-index: 10;
    }

    /* STATISTIK VALUES */
    .stat-label { color: #a8b0c5; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { font-size: 1.8rem; font-weight: 700; color: white; margin-top: 5px; }
    .unit { font-size: 1rem; color: #4facfe; }

    /* HIDE STREAMLIT ELEMENTS */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* CUSTOM TOGGLE WARNA */
    /* Kita biarkan toggle bawaan Streamlit, dia akan adaptasi ke dark theme */
</style>
""", unsafe_allow_html=True)

# ==========================================
# 7. DASHBOARD UI
# ==========================================
def show_dashboard():
    # Auto refresh logic
    if AUTO_REFRESH_INSTALLED:
        st_autorefresh(interval=2000, limit=None, key="fbr")

    sync_data()

    # Ambil variable
    data = st.session_state.dummy_data
    lvl = float(data['sensor']['water_level'])
    pres = float(data['sensor']['pressure'])
    is_pump_on = bool(data['status']['pump'])
    mode = str(data['control']['mode'])

    # Header
    st.markdown('<div class="main-title">💧 SMART WATER TANK</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">REALTIME MONITORING SYSTEM</div>', unsafe_allow_html=True)

    # --- LAYOUT UTAMA ---
    col_left, col_right = st.columns([1, 1.5], gap="large")

    # === KOLOM KIRI: VISUALISASI TANGKI ===
    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; margin-bottom:15px; font-weight:600; color:#4facfe;'>VISUAL LEVEL</div>", unsafe_allow_html=True)
        
        # HTML/CSS TANK DENGAN DYNAMIC HEIGHT
        tank_html = f"""
        <div class="tank-wrapper">
            <div class="tank-body">
                <div class="water-label">{int(lvl)}%</div>
                
                <div class="measurement-line" style="bottom: 25%;"></div>
                <div class="measurement-line" style="bottom: 50%;"></div>
                <div class="measurement-line" style="bottom: 75%;"></div>
                
                <div class="water" style="height: {lvl}%;"></div>
            </div>
        </div>
        """
        st.markdown(tank_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # === KOLOM KANAN: DATA & KONTROL ===
    with col_right:
        # Baris 1: Statistik (Grid 2 kolom)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="glass-card">
                <div class="stat-label">Tekanan Air</div>
                <div class="stat-value">{pres} <span class="unit">MPa</span></div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            status_text = "MENYALA" if is_pump_on else "MATI"
            color_text = "#00f2fe" if is_pump_on else "#ff4b1f"
            st.markdown(f"""
            <div class="glass-card">
                <div class="stat-label">Status Pompa</div>
                <div class="stat-value" style="color: {color_text};">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

        # Baris 2: Panel Kontrol
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:15px; font-weight:600; color:#fff;'>PANEL KONTROL</div>", unsafe_allow_html=True)
        
        # Logic Kontrol
        ctrl_col1, ctrl_col2 = st.columns([1, 1])
        
        with ctrl_col1:
            st.write("📡 **Mode Operasi**")
            # Radio Button Horizontal
            st.radio(
                "Pilih Mode",
                ["AUTO", "MANUAL"],
                index=0 if mode == "AUTO" else 1,
                key="radio_mode",
                horizontal=True,
                label_visibility="collapsed",
                on_change=update_mode
            )

        with ctrl_col2:
            st.write("🔌 **Saklar Pompa**")
            # TOGGLE SWITCH (Hanya aktif jika MANUAL)
            is_disabled = (mode == "AUTO")
            
            st.toggle(
                "Power Pompa",
                value=is_pump_on,
                key="toggle_pump",
                disabled=is_disabled,
                on_change=update_pump_toggle
            )
            
            if is_disabled:
                st.caption("🔒 *Terkunci di mode AUTO*")
            else:
                st.caption("👆 *Geser untuk ON/OFF*")
                
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 8. HALAMAN LANDING PAGE
# ==========================================
def show_home():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="main-title">💧 SMART WATER TANK</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("Smart Water Tank.jpg", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 MASUK KE DASHBOARD", use_container_width=True, type="primary"):
            st.session_state.show_dashboard = True
            st.rerun()

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    if st.session_state.show_dashboard:
        show_dashboard()
    else:
        show_home()
