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
# 2. LIBRARY CHECK
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

# ==========================================
# 3. KONEKSI FIREBASE
# ==========================================
firebase_app = None
if PAKAI_FIREBASE_ASLI and FIREBASE_AVAILABLE:
    try:
        if not firebase_admin._apps:
            if "firebase" in st.secrets:
                key_dict = json.loads(st.secrets["firebase"]["text_key"])
                cred = credentials.Certificate(key_dict)
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
# 5. LOGIKA DATA
# ==========================================
def get_data():
    if not PAKAI_FIREBASE_ASLI: return None
    try: return db.reference('/').get()
    except: return None

def set_data(path, value):
    if not PAKAI_FIREBASE_ASLI: return False
    try: db.reference(path).set(value); return True
    except: return False

def sync_data():
    real_data = get_data()
    if real_data:
        for section in ['control', 'sensor', 'status']:
            if section in real_data:
                if section not in st.session_state.dummy_data:
                    st.session_state.dummy_data[section] = {}
                st.session_state.dummy_data[section].update(real_data[section])
    else:
        set_data('/', st.session_state.dummy_data)

def update_pump_toggle():
    new_state = st.session_state['toggle_pump']
    if PAKAI_FIREBASE_ASLI:
        set_data('/control/manual_pump', new_state)
        set_data('/status/pump', new_state)
    st.session_state.dummy_data['control']['manual_pump'] = new_state
    st.session_state.dummy_data['status']['pump'] = new_state

def update_mode():
    # Mapping label UI ke value database
    ui_val = st.session_state['radio_mode']
    db_val = "AUTO" if "AUTO" in ui_val else "MANUAL"
    
    if PAKAI_FIREBASE_ASLI:
        set_data('/control/mode', db_val)
    st.session_state.dummy_data['control']['mode'] = db_val

# ==========================================
# 6. STYLING CSS (CUSTOM & BIG BUTTONS)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif !important; }

    .stApp {
        background: radial-gradient(circle at 10% 20%, #0f2027 0%, #203a43 90%, #2c5364 100%);
        color: white;
    }

    /* GLASS CARD CONTAINER */
    .glass-card-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }

    .main-title {
        font-size: 2.5rem; font-weight: 700; text-align: center;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .sub-title {
        text-align: center; color: #a8b0c5; letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 40px;
    }

    /* VISUAL TANGKI */
    .tank-wrapper-fix { display: flex; justify-content: center; align-items: center; height: 350px; position: relative; }
    .tank-body-fix { position: relative; width: 150px; height: 300px; background: rgba(255, 255, 255, 0.05); border: 4px solid rgba(255, 255, 255, 0.4); border-radius: 15px; overflow: hidden; box-shadow: inset 0 0 20px rgba(0,0,0,0.5); }
    .water-fix { position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%); transition: height 1s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 25px #00f2fe; opacity: 0.9; }
    .tank-label-fix { position: absolute; width: 100%; text-align: center; top: 50%; transform: translateY(-50%); font-size: 1.8rem; font-weight: 800; color: white; text-shadow: 0 2px 10px rgba(0,0,0,0.8); z-index: 20; }
    .line-fix { position: absolute; width: 100%; height: 2px; background: rgba(255,255,255,0.2); left: 0; z-index: 5; }

    /* STATISTIK */
    .stat-box { padding: 15px; text-align: center; }
    .stat-label-fix { color: #a8b0c5; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;}
    .stat-value-fix { font-size: 2.2rem; font-weight: 700; color: white; }
    .unit-fix { font-size: 1rem; color: #4facfe; font-weight: 400; }

    /* MODIFIKASI UKURAN TOMBOL (THE BIG SWITCH) */
    /* Target Toggle Switch agar lebih besar */
    div[data-testid="stCheckbox"] label span {
        font-size: 1.2rem !important; /* Label toggle */
    }
    div[data-testid="stCheckbox"] div[role="switch"] {
        transform: scale(1.4); /* Memperbesar ukuran fisik saklar */
        margin-right: 10px;
    }
    
    /* MODIFIKASI RADIO BUTTON (MODE SELECTION) */
    div[role="radiogroup"] {
        background: rgba(0,0,0,0.2);
        padding: 10px;
        border-radius: 15px;
        justify-content: space-evenly;
    }
    div[role="radiogroup"] label {
        font-size: 1.1rem !important;
        font-weight: bold !important;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 10px 20px !important;
        width: 100%;
        text-align: center;
        transition: all 0.3s;
    }
    div[role="radiogroup"] label:hover {
        border-color: #4facfe;
        background: rgba(79, 172, 254, 0.1);
    }

    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 7. DASHBOARD UI
# ==========================================
def show_dashboard():
    if AUTO_REFRESH_INSTALLED:
        st_autorefresh(interval=2000, limit=None, key="fbr")

    sync_data()
    data = st.session_state.dummy_data
    lvl = float(data['sensor']['water_level'])
    pres = float(data['sensor']['pressure'])
    is_pump_on = bool(data['status']['pump'])
    mode = str(data['control']['mode'])

    st.markdown('<div class="main-title">💧 SMART WATER TANK</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">REALTIME MONITORING SYSTEM</div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1.8], gap="large")

    # === KOLOM KIRI: VISUALISASI TANGKI ===
    with col_left:
        tank_html = """
        <div class="glass-card-container" style="height: 100%;">
            <div style='text-align:center; margin-bottom:20px; font-weight:600; color:#4facfe; letter-spacing:1px;'>VISUAL LEVEL</div>
            <div class="tank-wrapper-fix">
                <div class="tank-body-fix">
                    <div class="tank-label-fix">{lvl:.0f}%</div>
                    <div class="line-fix" style="bottom: 25%;"></div>
                    <div class="line-fix" style="bottom: 50%;"></div>
                    <div class="line-fix" style="bottom: 75%;"></div>
                    <div class="water-fix" style="height: {lvl}%;"></div>
                </div>
            </div>
        </div>
        """.format(lvl=lvl)
        st.markdown(tank_html, unsafe_allow_html=True)

    # === KOLOM KANAN: DATA & KONTROL ===
    with col_right:
        # --- BAGIAN 1: STATISTIK (Dua Kotak Berdampingan) ---
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown(f"""
            <div class="glass-card-container stat-box">
                <div class="stat-label-fix">Tekanan Air</div>
                <div class="stat-value-fix">{pres} <span class="unit-fix">MPa</span></div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            status_text = "MENYALA" if is_pump_on else "MATI"
            color_text = "#00f2fe" if is_pump_on else "#ff4b1f"
            st.markdown(f"""
            <div class="glass-card-container stat-box">
                <div class="stat-label-fix">Status Pompa</div>
                <div class="stat-value-fix" style="color: {color_text};">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)

        # --- BAGIAN 2: KONTROL PANEL (Disusun Vertikal) ---
        
        # A. PILIHAN MODE (PALING ATAS & BESAR)
        st.markdown('<div class="glass-card-container">', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:10px; font-weight:600; color:#fff; letter-spacing:1px;'>1. PILIH MODE OPERASI</div>", unsafe_allow_html=True)
        
        # Radio Button Horizontal yang besar
        mode_options = ["🤖 MODE AUTO", "👋 MODE MANUAL"]
        # Logic index
        curr_idx = 0 if mode == "AUTO" else 1
        
        st.radio(
            "Pilih Mode",
            mode_options,
            index=curr_idx,
            key="radio_mode",
            horizontal=True,
            label_visibility="collapsed",
            on_change=update_mode
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # B. SAKLAR POMPA MANUAL (DI BAWAHNYA & BESAR)
        st.markdown('<div class="glass-card-container">', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:10px; font-weight:600; color:#fff; letter-spacing:1px;'>2. KONTROL MANUAL</div>", unsafe_allow_html=True)
        
        col_ctrl_1, col_ctrl_2 = st.columns([2, 1])
        
        with col_ctrl_1:
            is_disabled = (mode == "AUTO")
            # Toggle Switch Besar
            st.write("") # Spacer dikit
            st.toggle(
                "SAKLAR POMPA UTAMA", 
                value=is_pump_on, 
                key="toggle_pump", 
                disabled=is_disabled, 
                on_change=update_pump_toggle
            )
        
        with col_ctrl_2:
            # Status text di sebelah toggle
            if is_disabled:
                st.info("🔒 **Terkunci**\n(Mode Auto Aktif)")
            else:
                st.success("🔓 **Terbuka**\n(Siap Kontrol)")
                
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 8. HALAMAN LANDING PAGE
# ==========================================
def show_home():
    # 1. HERO SECTION
    st.markdown('<div class="hero-title">SMART WATER TANK</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Sistem Monitoring & Kontrol Air Berbasis IoT Firebase</div>', unsafe_allow_html=True)
    
    # 2. HERO IMAGE (Floating & Glowing)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="hero-image-container">', unsafe_allow_html=True)
        try:
            st.image("Smart Water Tank.jpg", use_container_width=True)
        except:
            pass
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. FITUR HIGHLIGHTS
    f1, f2, f3 = st.columns(3, gap="medium")
    with f1:
        st.markdown("""<div class="glass-card-container" style="text-align:center;"><h3>📊</h3><h4>Realtime</h4><p style="font-size:0.8rem; color:#ccc;">Monitor level air presisi.</p></div>""", unsafe_allow_html=True)
    with f2:
        st.markdown("""<div class="glass-card-container" style="text-align:center;"><h3>⚡</h3><h4>Otomatis</h4><p style="font-size:0.8rem; color:#ccc;">Pompa pintar auto ON/OFF.</p></div>""", unsafe_allow_html=True)
    with f3:
        st.markdown("""<div class="glass-card-container" style="text-align:center;"><h3>☁️</h3><h4>Cloud</h4><p style="font-size:0.8rem; color:#ccc;">Akses data dari mana saja.</p></div>""", unsafe_allow_html=True)

    # 4. TOMBOL CTA
    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 1, 1])
    with b2:
        if st.button("🚀 MASUK KE DASHBOARD", use_container_width=True):
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
