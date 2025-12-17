import streamlit as st
import time
import random
import json
import os

# ==========================================
# KONFIGURASI UMUM
# ==========================================
PAKAI_FIREBASE_ASLI = True 
URL_DATABASE = 'https://smart-water-tank-f1b98-default-rtdb.asia-southeast1.firebasedatabase.app'

st.set_page_config(page_title="Smart Water Tank", layout="wide")

# ==========================================
# IMPORT LIBRARY (SAFE MODE)
# ==========================================
try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    st.error("⚠️ Library firebase-admin belum terinstall.")

try:
    from streamlit_autorefresh import st_autorefresh
    AUTO_REFRESH_INSTALLED = True
except ImportError:
    AUTO_REFRESH_INSTALLED = False
    st.warning("⚠️ Library streamlit-autorefresh belum terinstall.")

# ==========================================
# INISIALISASI FIREBASE (CLOUD & LOCAL SUPPORT)
# ==========================================
firebase_app = None

if PAKAI_FIREBASE_ASLI and FIREBASE_AVAILABLE:
    try:
        if not firebase_admin._apps:
            # 1. Cek SECRETS (Untuk Streamlit Cloud/GitHub)
            if "firebase" in st.secrets:
                key_dict = json.loads(st.secrets["firebase"]["text_key"])
                cred = credentials.Certificate(key_dict)
            
            # 2. Cek File JSON Lokal (Untuk di Laptop)
            elif os.path.exists("serviceAccountKey.json"):
                cred = credentials.Certificate("serviceAccountKey.json")
            
            else:
                st.error("❌ Kunci Akses Tidak Ditemukan. (Cek Secrets atau serviceAccountKey.json)")
                st.stop()

            # Init App
            firebase_app = firebase_admin.initialize_app(cred, {
                'databaseURL': URL_DATABASE
            })
        else:
            firebase_app = firebase_admin.get_app()
    except Exception as e:
        st.error(f"❌ Error Koneksi Firebase: {str(e)}")
        PAKAI_FIREBASE_ASLI = False

# ==========================================
# DATA STATE
# ==========================================
if 'dummy_data' not in st.session_state:
    st.session_state.dummy_data = {
        'control': {'mode': 'AUTO', 'manual_pump': False},
        'sensor': {'water_level': 75.0, 'pressure': 0.5},
        'status': {'pump': True}
    }
if 'show_dashboard' not in st.session_state:
    st.session_state.show_dashboard = False

# ==========================================
# CSS STYLING (MODERN UI)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    
    /* Background & Layout */
    .stApp {
        background: linear-gradient(135deg, #04152d 0%, #0a2540 50%, #04152d 100%);
        background-attachment: fixed;
    }
    h1, h2, h3, h4, p, span, div { color: #ffffff; }

    /* Hide Streamlit Elements */
    #MainMenu, header, footer { visibility: hidden; }

    /* Home & Titles */
    .home-title {
        font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 800; text-align: center;
        background: linear-gradient(135deg, #a8d5e2 0%, #4cc9f0 50%, #a8d5e2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: 50px; text-shadow: 0 0 30px rgba(76, 201, 240, 0.3);
    }
    .home-subtitle {
        color: #d68c45; text-align: center; letter-spacing: 3px; margin-bottom: 40px;
    }

    /* Cards */
    .data-card {
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(5px);
        border-radius: 15px; padding: 15px; margin-bottom: 10px;
        border: 1px solid rgba(168, 213, 226, 0.15);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .data-value { font-size: 1.8rem; font-weight: 700; color: #4cc9f0; }
    .data-label { color: #e0e0e0; font-size: 0.9rem; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4cc9f0 0%, #2a9fd4 100%);
        color: white; border-radius: 10px; border: none; font-weight: 600;
        width: 100%; padding: 10px;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(76,201,240,0.4); }
    .stButton > button[kind="secondary"] { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }

    /* Image Container */
    .image-container {
        border-radius: 20px; overflow: hidden;
        border: 2px solid rgba(168, 213, 226, 0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNGSI-FUNGSI LOGIKA
# ==========================================
def get_firebase_data():
    if not PAKAI_FIREBASE_ASLI or not FIREBASE_AVAILABLE: return None
    try: return db.reference('/').get()
    except: return None

def set_firebase_data(path, value):
    if not PAKAI_FIREBASE_ASLI or not FIREBASE_AVAILABLE: return False
    try: 
        db.reference(path).set(value)
        return True
    except: return False

def sync_data():
    """Sinkronisasi Data Realtime"""
    fb_data = get_firebase_data()
    if fb_data:
        for key in ['control', 'sensor', 'status']:
            if key in fb_data:
                if key not in st.session_state.dummy_data:
                    st.session_state.dummy_data[key] = {}
                st.session_state.dummy_data[key].update(fb_data[key])
    else:
        # Init jika kosong
        set_firebase_data('/', st.session_state.dummy_data)

def update_mode(mode):
    if PAKAI_FIREBASE_ASLI: set_firebase_data('/control/mode', mode)
    st.session_state.dummy_data['control']['mode'] = mode

def update_pump(status):
    if PAKAI_FIREBASE_ASLI:
        set_firebase_data('/control/manual_pump', status)
        set_firebase_data('/status/pump', status)
    st.session_state.dummy_data['control']['manual_pump'] = status
    st.session_state.dummy_data['status']['pump'] = status

# ==========================================
# HALAMAN: HOME
# ==========================================
def show_home():
    st.markdown('<div class="home-title">💧 SMART WATER TANK</div>', unsafe_allow_html=True)
    st.markdown('<div class="home-subtitle">ESP32 + FIREBASE IOT PROJECT</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; max-width: 700px; margin: 0 auto; color: #ddd; line-height: 1.6;">
        <b>We simplify water management.</b><br>
        By combining smart sensors with real-time cloud technology, we give you full control over your water supply. 
        Monitor levels, check pressure, and automate your pump—all from one beautiful dashboard.
    </div>
    <br><br>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🚀 START MONITORING", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()

# ==========================================
# HALAMAN: DASHBOARD
# ==========================================
def show_dashboard():
    # Auto Refresh 2 Detik
    if AUTO_REFRESH_INSTALLED:
        st_autorefresh(interval=2000, limit=None, key="fbr")
    
    sync_data()
    
    data = st.session_state.dummy_data
    lvl = data.get('sensor', {}).get('water_level', 0)
    pres = data.get('sensor', {}).get('pressure', 0)
    pump = data.get('status', {}).get('pump', False)
    mode = data.get('control', {}).get('mode', 'AUTO')

    # Header Kecil
    st.markdown("<h2 style='text-align:center; margin-bottom:20px;'>REALTIME DASHBOARD</h2>", unsafe_allow_html=True)

    # Layout Utama
    col_img, col_stats = st.columns([1.2, 1], gap="large")

    with col_img:
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        try: st.image("Smart Water Tank.jpg", use_container_width=True)
        except: st.warning("Gambar tidak ditemukan.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_stats:
        # Level Air
        color = "#2ecc71" if lvl > 50 else "#f39c12" if lvl > 20 else "#e74c3c"
        st.markdown(f"""
        <div class="data-card" style="border-left: 5px solid {color}">
            <div class="data-label">Level Air</div>
            <div class="data-value" style="color: {color}">{lvl}%</div>
            <div style="background:#333; height:10px; border-radius:5px; margin-top:5px;">
                <div style="background:{color}; width:{lvl}%; height:100%; border-radius:5px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tekanan
        st.markdown(f"""
        <div class="data-card">
            <div class="data-label">Tekanan Air</div>
            <div class="data-value">{pres} <span style="font-size:1rem">MPa</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Status Pompa
        p_text = "ON (MENYALA)" if pump else "OFF (MATI)"
        p_color = "#2ecc71" if pump else "#e74c3c"
        st.markdown(f"""
        <div class="data-card" style="background: {p_color}15; border-color: {p_color}">
            <div class="data-label">Status Pompa</div>
            <div class="data-value" style="color: {p_color}">{p_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mode
        st.markdown(f"""
        <div class="data-card">
            <div class="data-label">Mode Operasi</div>
            <div class="data-value" style="color: #fca311">{mode}</div>
        </div>
        """, unsafe_allow_html=True)

    # Panel Kontrol
    st.markdown("---")
    c1, c2 = st.columns(2, gap="large")
    
    with c1:
        st.info(f"**Mode Saat Ini: {mode}**")
        modes = ["AUTO", "MANUAL"]
        idx = 0 if mode == "AUTO" else 1
        new_mode = st.selectbox("Ganti Mode:", modes, index=idx)
        if new_mode != mode:
            update_mode(new_mode)
            st.rerun()

    with c2:
        if mode == "MANUAL":
            st.write("**Kontrol Manual Pompa:**")
            b1, b2 = st.columns(2)
            with b1: 
                if st.button("NYALAKAN", type="primary"): 
                    update_pump(True)
                    st.rerun()
            with b2: 
                if st.button("MATIKAN", type="secondary"): 
                    update_pump(False)
                    st.rerun()
        else:
            st.warning("🔒 Kontrol Manual terkunci karena mode AUTO aktif.")

# ==========================================
# MAIN APP
# ==========================================
if __name__ == "__main__":
    if st.session_state.show_dashboard:
        show_dashboard()
    else:
        show_home()
