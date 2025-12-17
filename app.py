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
    new_mode = st.session_state['radio_mode']
    db_val = "AUTO" if "AUTO" in new_mode else "MANUAL"
    if PAKAI_FIREBASE_ASLI:
        set_data('/control/mode', db_val)
    st.session_state.dummy_data['control']['mode'] = db_val

# ==========================================
# 6. STYLING CSS
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
        padding: 25px; /* Padding sedikit lebih besar */
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }

    /* JUDUL */
    .main-title {
        font-size: 2.5rem; font-weight: 700; text-align: center;
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .sub-title {
        text-align: center; color: #a8b0c5; letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 40px;
    }
    
    /* PANEL HEADER */
    .panel-header {
        background: rgba(255, 255, 255, 0.1);
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 600;
        color: #fff;
        letter-spacing: 1px;
        margin-bottom: 20px;
        text-transform: uppercase;
        font-size: 0.9rem;
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

    /* MODIFIKASI TOMBOL */
    div[data-testid="stCheckbox"] label span { font-size: 1.1rem !important; }
    div[data-testid="stCheckbox"] div[role="switch"] { transform: scale(1.3); margin-right: 10px; }
    
    /* RADIO BUTTON GAYA PILL/CAPSULE */
    div[role="radiogroup"] { flex-direction: row; gap: 10px; }
    div[role="radiogroup"] label {
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 50px !important; /* Membuatnya bulat lonjong */
        padding: 5px 15px !important;
        transition: all 0.3s ease;
    }
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: rgba(79, 172, 254, 0.2) !important;
        border-color: #4facfe !important;
        color: #4facfe !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    
    /* LANDING PAGE */
    .hero-title { font-size: clamp(2.5rem, 5vw, 4rem); font-weight: 800; text-align: center; background: linear-gradient(to right, #00c6ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 20px; text-shadow: 0 0 40px rgba(0, 198, 255, 0.3); animation: fadeInDown 1s ease-out; }
    .hero-subtitle { text-align: center; font-size: 1.2rem; color: #e0e0e0; margin-bottom: 40px; font-weight: 300; letter-spacing: 1px; animation: fadeInUp 1s ease-out; }
    .hero-image-container { display: flex; justify-content: center; margin-bottom: 40px; animation: zoomIn 1.2s ease-out; }
    .hero-image-container img { border-radius: 20px; box-shadow: 0 0 30px rgba(0, 198, 255, 0.5); border: 2px solid rgba(255, 255, 255, 0.1); transition: transform 0.3s; }
    .hero-image-container img:hover { transform: scale(1.02); box-shadow: 0 0 50px rgba(0, 198, 255, 0.8); }
    .feature-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 20px; border-radius: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.1); transition: transform 0.3s, background 0.3s; height: 100%; }
    .feature-card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.1); border-color: #00c6ff; }
    .feature-icon { font-size: 2.5rem; margin-bottom: 10px; }
    .feature-title { font-weight: 700; color: #fff; margin-bottom: 5px; }
    .feature-desc { font-size: 0.85rem; color: #ccc; }
    div.stButton > button { background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%); color: white; border: none; padding: 15px 40px; font-size: 1.2rem; font-weight: bold; border-radius: 50px; box-shadow: 0 10px 20px rgba(0, 114, 255, 0.3); transition: all 0.3s; width: 100%; }
    div.stButton > button:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 15px 30px rgba(0, 114, 255, 0.5); }
    @keyframes fadeInDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes zoomIn { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
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

    # Tombol Back to Home (Kecil di pojok)
    if st.button("⬅️ Kembali ke Home"):
        st.session_state.show_dashboard = False
        st.rerun()

    st.markdown('<div class="main-title">DASHBOARD MONITORING</div>', unsafe_allow_html=True)
    st.write("") # Spacer

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
        # --- BAGIAN 1: STATISTIK ---
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


        # Grid layout di dalam panel kontrol (2 Kolom)
        ctrl_c1, ctrl_c2 = st.columns(2, gap="large")
        
        with ctrl_c1:
            st.markdown("📡 **Mode Operasi**")
            st.write("") # Spacer kecil
            # Radio Button
            st.radio(
                "Pilih Mode",
                ["🤖 AUTO", "👋 MANUAL"],
                index=0 if mode == "AUTO" else 1,
                key="radio_mode",
                horizontal=True,
                label_visibility="collapsed",
                on_change=update_mode
            )

        with ctrl_c2:
            st.markdown("🔌 **Saklar Pompa**")
            # Logic Disable
            is_disabled = (mode == "AUTO")
            st.toggle(
                "Power Pompa", 
                value=is_pump_on, 
                key="toggle_pump", 
                disabled=is_disabled, 
                label_visibility="collapsed",
                on_change=update_pump_toggle
            )
            # Caption di bawah toggle
            caption_text = "🔒 *Terkunci (Mode Auto)*" if is_disabled else "👆 *Geser untuk ON/OFF*"
            st.caption(caption_text)
                
        st.markdown('</div>', unsafe_allow_html=True) # End glass-card-container

# ==========================================
# 8. HALAMAN LANDING PAGE
# ==========================================
def show_home():
    st.markdown('<div class="hero-title">SMART WATER TANK</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Sistem Monitoring & Kontrol Air Berbasis IoT Firebase</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="hero-image-container">', unsafe_allow_html=True)
        try: st.image("Smart Water Tank.jpg", use_container_width=True)
        except: pass
        st.markdown('</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3, gap="medium")
    with f1: st.markdown("""<div class="feature-card"><div class="feature-icon">📊</div><div class="feature-title">Realtime Monitor</div><div class="feature-desc">Pantau ketinggian air dan tekanan secara presisi setiap detik.</div></div>""", unsafe_allow_html=True)
    with f2: st.markdown("""<div class="feature-card"><div class="feature-icon">⚡</div><div class="feature-title">Otomatisasi</div><div class="feature-desc">Pompa menyala otomatis saat air habis dan mati saat penuh.</div></div>""", unsafe_allow_html=True)
    with f3: st.markdown("""<div class="feature-card"><div class="feature-icon">☁️</div><div class="feature-title">Cloud Firebase</div><div class="feature-desc">Data tersimpan aman di cloud dan dapat diakses dari mana saja.</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 1, 1])
    with b2:
        if st.button("🚀 MASUK KE DASHBOARD", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()
            
    st.markdown("<div style='text-align:center; margin-top:50px; color:#aaa; font-size:0.8rem;'>© 2025 Smart Water Project • IoT Division</div>", unsafe_allow_html=True)

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    if st.session_state.show_dashboard:
        show_dashboard()
    else:
        show_home()

