import streamlit as st
import time
import random
import json
import os

# ==========================================
# KONFIGURASI FIREBASE
# ==========================================
try:
    import firebase_admin
    from firebase_admin import credentials, db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

# ==========================================
# IMPORT AUTO REFRESH (Solusi Agar Tidak Gagal)
# ==========================================
try:
    from streamlit_autorefresh import st_autorefresh
    AUTO_REFRESH_INSTALLED = True
except ImportError:
    AUTO_REFRESH_INSTALLED = False

# ==========================================
# KONFIGURASI
# ==========================================
PAKAI_FIREBASE_ASLI = True  # Ubah ke True untuk menggunakan Firebase

# --- SETTING HALAMAN ---
st.set_page_config(page_title="Smart Water Tank", layout="wide")

# Inisialisasi Firebase (setelah set_page_config)
firebase_app = None
if PAKAI_FIREBASE_ASLI and FIREBASE_AVAILABLE:
    try:
        # Cek apakah Firebase sudah diinisialisasi
        if not firebase_admin._apps:
            # Path ke service account key
            cred_path = "serviceAccountKey.json"
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                # Inisialisasi dengan database URL dari konfigurasi
                firebase_app = firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://smart-water-tank-f1b98-default-rtdb.asia-southeast1.firebasedatabase.app'
                })
            else:
                st.error(f"❌ File {cred_path} tidak ditemukan!")
                PAKAI_FIREBASE_ASLI = False
        else:
            firebase_app = firebase_admin.get_app()
    except Exception as e:
        st.error(f"❌ Error inisialisasi Firebase: {str(e)}")
        PAKAI_FIREBASE_ASLI = False
elif PAKAI_FIREBASE_ASLI and not FIREBASE_AVAILABLE:
    st.warning("⚠️ Firebase Admin SDK tidak terinstall. Install dengan: pip install firebase-admin")

# Jika library auto refresh belum diinstall
if not AUTO_REFRESH_INSTALLED:
    st.warning("⚠️ Library 'streamlit-autorefresh' belum terinstall. Install dengan: pip install streamlit-autorefresh")

# ==========================================
# CUSTOM CSS (DESAIN MODERN & MENARIK)
# ==========================================
st.markdown("""
<style>
    /* ========== IMPORT FONTS ========== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ========== GLOBAL STYLES ========== */
    * {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, p, span, div {
        color: #ffffff;
    }
    
    /* ========== BACKGROUND & LAYOUT ========== */
    .stApp {
        background: linear-gradient(135deg, #04152d 0%, #0a2540 50%, #04152d 100%);
        background-attachment: fixed;
        overflow-x: hidden !important;
        overflow-y: hidden !important;
        max-width: 100vw !important;
        width: 100vw !important;
    }
    
    html, body {
        overflow-x: hidden !important;
        overflow-y: hidden !important;
        height: 100vh !important;
        max-width: 100vw !important;
        width: 100vw !important;
    }
    
    div[data-testid="stAppViewContainer"] {
        overflow: hidden !important;
        height: 100vh !important;
    }
    
    .main {
        overflow: hidden !important;
        height: 100vh !important;
    }
    
    .main .block-container {
        max-width: 100% !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100vw !important;
        width: 100vw !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        box-sizing: border-box !important;
    }
    
    /* ========== COLUMN STYLING ========== */
    div[data-testid="column"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    div[data-testid="column"]:nth-of-type(2) {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    div[data-testid="column"]:nth-of-type(2) > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    /* ========== HIDE EMPTY ELEMENTS ========== */
    #homeContainer ~ * {
        overflow: hidden !important;
    }
    
    .main-container ~ div[data-testid="stMarkdownContainer"]:empty,
    .main-container ~ div:empty,
    div[data-testid="column"] > div:first-child:empty,
    div[data-testid="column"] > div:has(.main-container) ~ div:empty,
    div[data-testid="column"]:nth-child(2) > div:first-child:empty,
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div:first-child:empty,
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div:empty,
    div[data-testid="column"]:nth-of-type(2) > div > div:first-child:empty,
    div[data-testid="column"]:nth-of-type(2) > div > div[style*="height"]:empty,
    div:has(.main-container) > *:first-child:empty {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
        max-height: 0 !important;
        visibility: hidden !important;
    }
    
    /* ========== MAIN CONTAINER ========== */
    .main-container {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 15px;
        padding-top: 10px;
        margin-top: 0 !important;
        border: 1px solid rgba(168, 213, 226, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .main-container > *:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    div:has(.main-container) {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    div[data-testid="column"] > div:has(.main-container) > div:first-child:empty {
        display: none !important;
    }
    
    /* ========== TITLE STYLING ========== */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a8d5e2 0%, #4cc9f0 50%, #a8d5e2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0px;
        margin-top: 10px;
        padding-top: 10px;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 0 30px rgba(76, 201, 240, 0.3);
        animation: glow 3s ease-in-out infinite alternate;
    }
    
    .sub-title {
        font-size: 1rem;
        color: #d68c45;
        text-align: center;
        margin-top: -5px;
        margin-bottom: 15px;
        font-weight: 400;
        letter-spacing: 3px;
        text-transform: uppercase;
        opacity: 0.9;
    }
    
    /* ========== CARD STYLING ========== */
    .data-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        border-radius: 15px;
        padding: 12px 18px;
        margin-bottom: 10px;
        border: 1px solid rgba(168, 213, 226, 0.15);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .data-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 201, 240, 0.2);
        border-color: rgba(168, 213, 226, 0.3);
    }
    
    .data-card-no-top-radius {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        border-radius: 0 0 15px 15px;
        padding: 20px 25px;
        margin-bottom: 15px;
        border: 1px solid rgba(168, 213, 226, 0.15);
        border-top: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .data-card-no-top-radius:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 201, 240, 0.2);
        border-color: rgba(168, 213, 226, 0.3);
    }
    
    /* ========== DATA ROW STYLING ========== */
    .data-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
    }
    
    .data-label {
        font-weight: 500;
        color: #e0e0e0;
        font-size: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .data-value {
        font-weight: 700;
        font-size: 1.3rem;
        color: #4cc9f0;
        text-shadow: 0 0 10px rgba(76, 201, 240, 0.5);
    }
    
    /* ========== PROGRESS BAR ========== */
    .progress-container {
        margin-top: 10px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        position: relative;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #4cc9f0 0%, #a8d5e2 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
        box-shadow: 0 0 10px rgba(76, 201, 240, 0.6);
        position: relative;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    /* ========== STATUS BADGES ========== */
    .pump-on {
        color: #2ecc71;
        font-weight: 700;
        background: rgba(46, 204, 113, 0.15);
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid rgba(46, 204, 113, 0.3);
        display: inline-block;
        box-shadow: 0 0 15px rgba(46, 204, 113, 0.3);
    }
    
    .pump-off {
        color: #e74c3c;
        font-weight: 700;
        background: rgba(231, 76, 60, 0.15);
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid rgba(231, 76, 60, 0.3);
        display: inline-block;
        box-shadow: 0 0 15px rgba(231, 76, 60, 0.3);
    }
    
    .mode-badge {
        color: #fca311;
        font-weight: 700;
        background: rgba(252, 163, 17, 0.15);
        padding: 8px 16px;
        border-radius: 20px;
        border: 1px solid rgba(252, 163, 17, 0.3);
        display: inline-block;
        box-shadow: 0 0 15px rgba(252, 163, 17, 0.3);
    }
    
    /* ========== BUTTON STYLING ========== */
    .stButton > button {
        background: linear-gradient(135deg, #4cc9f0 0%, #2a9fd4 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 201, 240, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 201, 240, 0.5);
    }
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    .stButton > button[kind="secondary"]:hover {
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.5);
    }
    
    div[data-testid="stButton"] > button {
        font-size: 1.2rem !important;
    }
    
    /* ========== HOME BUTTON STYLING ========== */
    .home-button-wrapper {
        margin-top: 0px;
        margin-bottom: 0px;
        padding-top: 0px;
        width: 100% !important;
        max-width: 100% !important;
        padding: 0 10px !important;
        box-sizing: border-box !important;
    }
    
    .home-button-wrapper .stButton > button {
        padding: 20px clamp(30px, 8vw, 60px) !important;
        font-size: clamp(1rem, 3vw, 1.5rem) !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #4cc9f0 0%, #2a9fd4 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 30px rgba(76, 201, 240, 0.4) !important;
        text-transform: uppercase !important;
        letter-spacing: clamp(1px, 0.5vw, 2px) !important;
        position: relative !important;
        overflow: hidden !important;
        animation: pulse 2s ease-in-out infinite 2s !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    .home-button-wrapper .stButton > button:hover {
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 0 12px 40px rgba(76, 201, 240, 0.6) !important;
    }
    
    .home-button-wrapper .stButton > button:active {
        transform: translateY(-2px) scale(1.02) !important;
    }
    
    /* ========== SELECTBOX & INFO STYLING ========== */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(168, 213, 226, 0.2);
        border-radius: 10px;
        color: white;
    }
    
    .stInfo {
        background: rgba(76, 201, 240, 0.1);
        border: 1px solid rgba(76, 201, 240, 0.3);
        border-radius: 10px;
    }
    
    /* ========== IMAGE CONTAINER ========== */
    .image-container {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        border: 2px solid rgba(168, 213, 226, 0.2);
    }
    
    .icon {
        font-size: 1.2rem;
        margin-right: 8px;
    }
    
    /* ========== HOME SCREEN STYLING ========== */
    .home-container-wrapper {
        height: 100vh !important;
        max-height: 100vh !important;
        width: 100% !important;
        max-width: 100vw !important;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        overflow: visible !important;
        position: relative;
        margin: 0 !important;
        padding: 0 !important;
        box-sizing: border-box !important;
        gap: 0 !important;
    }
    
    .home-container-wrapper > *:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    .home-container-wrapper div[data-testid="column"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    .home-container-wrapper div[data-testid="column"] > div {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    .home-container-wrapper div[data-testid="stVerticalBlock"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
        gap: 0 !important;
    }
    
    #homeContainer ~ * header,
    #homeContainer ~ * footer {
        display: none !important;
    }
    
    .home-container {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        height: 100vh;
        width: 100%;
        max-width: 100vw;
        text-align: center;
        animation: fadeIn 1s ease-in;
        padding: 0;
        margin: 0;
        box-sizing: border-box;
        overflow: visible;
        margin-top: 0;
        gap: 0;
        padding-top: 15vh;
        will-change: transform, opacity;
        transition: all 0.8s ease-in;
    }
    
    .home-container > * {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    
    .home-container .home-subtitle {
        margin-bottom: 10px !important;
    }
    
    .home-container .home-button-wrapper {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    .home-title {
        font-size: clamp(2rem, 5vw, 3.5rem);
        font-weight: 800;
        background: linear-gradient(135deg, #a8d5e2 0%, #4cc9f0 50%, #a8d5e2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 5px;
        margin-top: 40px;
        padding-top: 40px;
        padding-bottom: 40px;
        padding-left: 10px;
        padding-right: 10px;
        text-transform: uppercase;
        letter-spacing: clamp(2px, 1vw, 5px);
        animation: slideDown 1s ease-out, textGlow 2s ease-in-out infinite alternate;
        position: relative;
        filter: drop-shadow(0 0 10px rgba(76, 201, 240, 0.6));
        word-wrap: break-word;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .home-subtitle {
        font-size: clamp(0.9rem, 2vw, 1.2rem);
        color: #d68c45;
        margin-bottom: 10px;
        margin-top: 0;
        padding-left: 10px;
        padding-right: 10px;
        font-weight: 400;
        letter-spacing: clamp(1px, 0.5vw, 3px);
        opacity: 0.9;
        animation: fadeInUp 1.2s ease-out, subtitleGlow 2.5s ease-in-out infinite alternate;
        position: relative;
        filter: drop-shadow(0 0 8px rgba(214, 140, 69, 0.7));
        text-shadow: 0 0 10px rgba(214, 140, 69, 0.5);
        word-wrap: break-word;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .home-description {
        max-width: 800px;
        margin: 30px auto;
        padding: 0 20px;
        text-align: center;
        animation: fadeInUp 1.4s ease-out;
    }
    
    .home-description-section {
        margin-bottom: 25px;
    }
    
    .home-description-title {
        font-size: clamp(1.2rem, 3vw, 1.8rem);
        font-weight: 700;
        color: #4cc9f0;
        margin-top: 80px;
        margin-bottom: 24px;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 15px rgba(76, 201, 240, 0.5);
    }
    
    .home-description-text {
        font-size: clamp(0.95rem, 2.2vw, 1.15rem);
        color: #e0e0e0;
        line-height: 1.7;
        opacity: 0.95;
        text-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
    }
    
    .start-button-container {
        animation: fadeInUp 1.5s ease-out, pulse 2s ease-in-out infinite 2s;
    }
    
    /* ========== DASHBOARD STYLING ========== */
    .dashboard-container {
        animation: slideInFromRight 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        position: relative;
        will-change: transform, opacity;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    .dashboard-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(76, 201, 240, 0.1) 0%, transparent 100%);
        animation: fadeIn 1s ease-out;
        pointer-events: none;
    }
    
    .dashboard-container > * {
        animation: fadeInUp 0.8s ease-out 0.3s both;
    }
    
    .element-container {
        margin-bottom: 0.5rem !important;
    }
    
    .home-container.transitioning {
        animation: slideOutToLeft 0.8s ease-in forwards !important;
    }
    
    /* ========== HIDE STREAMLIT ELEMENTS ========== */
    /* Hide Sidebar */
    section[data-testid="stSidebar"],
    div[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide Header */
    header[data-testid="stHeader"],
    div[data-testid="stHeader"],
    #stHeader {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Hide Footer */
    footer[data-testid="stFooter"],
    div[data-testid="stFooter"],
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Hide Decoration */
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Hide Menu Button */
    button[data-testid="baseButton-header"],
    button[title="View app source"],
    button[title="Get help"],
    button[title="Report a bug"],
    button[title="About"],
    .stDeployButton,
    #stDeployButton {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu,
    div[data-testid="stToolbar"],
    .stToolbar {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Adjust Main Content Padding */
    .main .block-container {
        padding-top: 0 !important;
    }
    
    /* Hide Streamlit Logo */
    img[alt="Streamlit"],
    a[href*="streamlit.io"] {
        display: none !important;
    }
    
    /* ========== ANIMATIONS ========== */
    @keyframes glow {
        from { filter: brightness(1); }
        to { filter: brightness(1.2); }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideDown {
        from {
            transform: translateY(-50px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes slideOutToLeft {
        0% {
            transform: translateX(0) scale(1);
            opacity: 1;
            filter: blur(0px);
        }
        50% {
            opacity: 0.5;
            filter: blur(5px);
        }
        100% {
            transform: translateX(-100%) scale(0.85);
            opacity: 0;
            filter: blur(10px);
        }
    }
    
    @keyframes slideInFromRight {
        0% {
            transform: translateX(100%) scale(0.95);
            opacity: 0;
            filter: blur(10px);
        }
        50% {
            opacity: 0.5;
            filter: blur(5px);
        }
        100% {
            transform: translateX(0) scale(1);
            opacity: 1;
            filter: blur(0px);
        }
    }
    
    @keyframes textGlow {
        0% {
            filter: drop-shadow(0 0 10px rgba(76, 201, 240, 0.6))
                    drop-shadow(0 0 20px rgba(76, 201, 240, 0.4))
                    drop-shadow(0 0 30px rgba(76, 201, 240, 0.2));
        }
        100% {
            filter: drop-shadow(0 0 20px rgba(76, 201, 240, 0.9))
                    drop-shadow(0 0 40px rgba(76, 201, 240, 0.6))
                    drop-shadow(0 0 60px rgba(76, 201, 240, 0.3));
        }
    }
    
    @keyframes subtitleGlow {
        0% {
            filter: drop-shadow(0 0 8px rgba(214, 140, 69, 0.7))
                    drop-shadow(0 0 16px rgba(214, 140, 69, 0.5))
                    drop-shadow(0 0 24px rgba(214, 140, 69, 0.3));
        }
        100% {
            filter: drop-shadow(0 0 15px rgba(214, 140, 69, 0.9))
                    drop-shadow(0 0 30px rgba(214, 140, 69, 0.6))
                    drop-shadow(0 0 45px rgba(214, 140, 69, 0.4));
        }
    }
    
    @keyframes overlayFade {
        0% { opacity: 0; }
        50% { opacity: 1; }
        100% { opacity: 0; display: none; }
    }
    
    @keyframes wave {
        0%, 100% {
            transform: translateY(0) scaleY(1);
        }
        50% {
            transform: translateY(-20px) scaleY(1.1);
        }
    }
    
    /* ========== TRANSITION OVERLAY ========== */
    .transition-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #04152d 0%, #0a2540 50%, #04152d 100%);
        z-index: 9999;
        animation: overlayFade 1s ease-out forwards;
        pointer-events: none;
    }
    
    .water-wave {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 200px;
        background: linear-gradient(180deg, transparent, rgba(76, 201, 240, 0.1));
        animation: wave 3s ease-in-out infinite;
    }
    
    .main > div {
        transition: opacity 0.5s ease-in-out;
    }
</style>

<script>
    // Function untuk menambahkan animasi transisi saat tombol diklik
    function initTransitionAnimation() {
        const startButton = document.querySelector('button[key="start_button"]') || 
                           document.querySelector('button:has-text("START")') ||
                           Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.includes('START'));
        
        if (startButton) {
            startButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Tambahkan animasi slide out ke home container
                const homeContainer = document.querySelector('.home-container') || document.getElementById('homeContainer');
                if (homeContainer) {
                    homeContainer.style.animation = 'slideOutToLeft 0.8s ease-in forwards';
                    homeContainer.style.transition = 'all 0.8s ease-in';
                }
                
                // Tambahkan overlay transisi
                const overlay = document.createElement('div');
                overlay.id = 'transitionOverlay';
                overlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #04152d 0%, #0a2540 50%, #04152d 100%);
                    z-index: 99999;
                    opacity: 0;
                    transition: opacity 0.5s ease-in-out;
                `;
                document.body.appendChild(overlay);
                
                // Animate overlay
                setTimeout(() => {
                    overlay.style.opacity = '1';
                }, 10);
                
                // Delay sebelum submit form
                setTimeout(() => {
                    const form = startButton.closest('form');
                    if (form) {
                        form.requestSubmit();
                    } else {
                        startButton.click();
                    }
                }, 800);
                
                return false;
            }, true);
        }
    }
    
    // Jalankan saat halaman dimuat
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTransitionAnimation);
    } else {
        initTransitionAnimation();
    }
    
    // Observer untuk memastikan tombol terdeteksi setelah Streamlit render
    const observer = new MutationObserver(function(mutations) {
        initTransitionAnimation();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Fallback: jalankan setiap 500ms untuk memastikan
    setInterval(initTransitionAnimation, 500);
</script>
""", unsafe_allow_html=True)

# ==========================================
# DATA SIMULASI
# ==========================================
if 'dummy_data' not in st.session_state:
    st.session_state.dummy_data = {
        'control': {'mode': 'AUTO', 'manual_pump': False},
        'sensor': {'water_level': 75.0, 'pressure': 0.5},
        'status': {'pump': True}
    }

# ==========================================
# STATE UNTUK HOME SCREEN
# ==========================================
if 'show_dashboard' not in st.session_state:
    st.session_state.show_dashboard = False
if 'transitioning' not in st.session_state:
    st.session_state.transitioning = False
if 'auto_refresh_interval' not in st.session_state:
    st.session_state.auto_refresh_interval = 3  # Default 3 detik
if 'auto_refresh_enabled' not in st.session_state:
    st.session_state.auto_refresh_enabled = True  # Auto-refresh aktif secara default

# ==========================================
# FUNGSI FIREBASE
# ==========================================
def get_firebase_data():
    """Mengambil data dari Firebase Realtime Database"""
    if not PAKAI_FIREBASE_ASLI or not FIREBASE_AVAILABLE:
        return None
    
    try:
        ref = db.reference('/')
        data = ref.get()
        return data
    except Exception as e:
        st.error(f"❌ Error membaca data Firebase: {str(e)}")
        return None

def set_firebase_data(path, value):
    """Menulis data ke Firebase Realtime Database"""
    if not PAKAI_FIREBASE_ASLI or not FIREBASE_AVAILABLE:
        return False
    
    try:
        ref = db.reference(path)
        ref.set(value)
        return True
    except Exception as e:
        st.error(f"❌ Error menulis data Firebase: {str(e)}")
        return False

def sync_firebase_data():
    """Sinkronisasi data dari Firebase ke session state"""
    if not PAKAI_FIREBASE_ASLI or not FIREBASE_AVAILABLE:
        return
    
    firebase_data = get_firebase_data()
    if firebase_data:
        # Update session state dengan data dari Firebase
        if 'control' in firebase_data:
            if 'control' not in st.session_state.dummy_data:
                st.session_state.dummy_data['control'] = {}
            st.session_state.dummy_data['control'].update(firebase_data['control'])
        if 'sensor' in firebase_data:
            if 'sensor' not in st.session_state.dummy_data:
                st.session_state.dummy_data['sensor'] = {}
            st.session_state.dummy_data['sensor'].update(firebase_data['sensor'])
        if 'status' in firebase_data:
            if 'status' not in st.session_state.dummy_data:
                st.session_state.dummy_data['status'] = {}
            st.session_state.dummy_data['status'].update(firebase_data['status'])
    else:
        # Jika Firebase kosong, inisialisasi dengan data default
        default_data = {
            'control': {'mode': 'AUTO', 'manual_pump': False},
            'sensor': {'water_level': 75.0, 'pressure': 0.5},
            'status': {'pump': True}
        }
        set_firebase_data('/', default_data)
        st.session_state.dummy_data = default_data

# ==========================================
# FUNGSI UPDATE DATA
# ==========================================
def update_mode(new_mode):
    """Update mode kontrol (AUTO/MANUAL)"""
    if PAKAI_FIREBASE_ASLI and FIREBASE_AVAILABLE:
        # Update ke Firebase
        success = set_firebase_data('/control/mode', new_mode)
        if success:
            st.session_state.dummy_data['control']['mode'] = new_mode
    else:
        st.session_state.dummy_data['control']['mode'] = new_mode

def update_pump(is_on):
    """Update status pompa"""
    if PAKAI_FIREBASE_ASLI and FIREBASE_AVAILABLE:
        # Update ke Firebase
        set_firebase_data('/control/manual_pump', is_on)
        set_firebase_data('/status/pump', is_on)
        st.session_state.dummy_data['control']['manual_pump'] = is_on
        st.session_state.dummy_data['status']['pump'] = is_on
    else:
        st.session_state.dummy_data['control']['manual_pump'] = is_on
        st.session_state.dummy_data['status']['pump'] = is_on

# ==========================================
# TAMPILAN HOME SCREEN
# ==========================================
def show_home_screen():
    """Menampilkan halaman home screen dengan animasi"""
    transition_placeholder = st.empty()
    
    # Container wrapper untuk memastikan semua muat dalam viewport
    st.markdown("""
    <div class="home-container-wrapper">
        <div class="home-container" id="homeContainer">
            <div class="home-title">💧 SMART WATER TANK</div>
            <div class="home-subtitle">ESP32 + FIREBASE</div>
            <div class="home-description">
                <div class="home-description-section">
                    <div class="home-description-title">Who Are We</div>
                    <div class="home-description-text">We are the IoT Control Initiative. We bridge the gap between hardware and the cloud, engineering precise automation systems to ensure efficiency in every drop.</div>
                </div>
                <div class="home-description-section">
                    <div class="home-description-title">What We Do</div>
                    <div class="home-description-text">We simplify water management. By combining smart sensors with real-time cloud technology, we give you full control over your water supply. Monitor levels, check pressure, and automate your pump all from one beautiful dashboard.</div>
                </div>
            </div>
            <div class="home-button-wrapper">
    """, unsafe_allow_html=True)
    
    # Tombol Start dengan styling khusus
    col1, col2, col3 = st.columns([0.5, 3, 0.5], gap="small")
    with col2:
        if st.button("START", use_container_width=True, key="start_button"):
            # Tampilkan animasi transisi
            transition_placeholder.markdown("""
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #04152d 0%, #0a2540 50%, #04152d 100%);
                z-index: 99999;
                opacity: 0;
                animation: fadeInOverlay 0.6s ease-in forwards;
            "></div>
            <style>
                @keyframes fadeInOverlay {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                #homeContainer {
                    animation: slideOutToLeft 0.8s ease-in forwards !important;
                }
            </style>
            <script>
                (function() {
                    const container = document.getElementById('homeContainer');
                    if (container) {
                        container.style.cssText += 'animation: slideOutToLeft 0.8s ease-in forwards !important;';
                        container.style.cssText += 'transform: translateX(-100%) scale(0.85) !important;';
                        container.style.cssText += 'opacity: 0 !important;';
                        container.style.cssText += 'filter: blur(10px) !important;';
                    }
                })();
            </script>
            """, unsafe_allow_html=True)
            # Beri waktu untuk animasi berjalan
            time.sleep(0.9)
            st.session_state.show_dashboard = True
            st.rerun()
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAMPILAN DASHBOARD
# ==========================================
def show_dashboard():
    """Menampilkan dashboard dengan data dan kontrol"""
    # --- AUTO REFRESH LOGIC (BAGIAN PENTING) ---
    # Ini akan me-refresh data setiap 2000ms (2 detik) tanpa reload halaman penuh
    if AUTO_REFRESH_INSTALLED:
        st_autorefresh(interval=2000, limit=None, key="fbr")
    
    # Sinkronisasi data dari Firebase jika menggunakan Firebase
    # Lakukan sinkronisasi SETIAP KALI dashboard ditampilkan
    if PAKAI_FIREBASE_ASLI and FIREBASE_AVAILABLE:
        try:
            sync_firebase_data()
        except Exception as e:
            st.warning(f"⚠️ Gagal sinkronisasi data: {str(e)}")
    
    # Tambahkan overlay fade out saat dashboard muncul
    st.markdown("""
    <div id="dashboardOverlay" style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #04152d 0%, #0a2540 50%, #04152d 100%);
        z-index: 99998;
        opacity: 1;
        animation: fadeOutOverlay 0.8s ease-out forwards;
        pointer-events: none;
    "></div>
    <style>
        @keyframes fadeOutOverlay {
            from { opacity: 1; }
            to { opacity: 0; display: none; }
        }
    </style>
    <script>
        setTimeout(function() {
            const overlay = document.getElementById('dashboardOverlay');
            if (overlay) overlay.remove();
        }, 800);
    </script>
    """, unsafe_allow_html=True)
    
    # Header dengan Class CSS khusus
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
    st.markdown('<div class="main-title">💧 SMART WATER TANK</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">ESP32 + FIREBASE</div>', unsafe_allow_html=True)
    
    # Status Firebase
    if PAKAI_FIREBASE_ASLI:
        if FIREBASE_AVAILABLE and firebase_app:
            st.success("🟢 Terhubung ke Firebase")
        else:
            st.error("🔴 Firebase tidak tersedia")
    
    # Ambil Data
    data = st.session_state.dummy_data
    lvl = data.get('sensor', {}).get('water_level', 0)
    pres = data.get('sensor', {}).get('pressure', 0)
    pump = data.get('status', {}).get('pump', False)
    mode = data.get('control', {}).get('mode', 'AUTO')

    # Layout Dashboard - 3 Bagian: Gambar, Statistik, Kontrol
    # Bagian 1: Gambar dan Visualisasi
    st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    col_img, col_stats = st.columns([1.3, 1], gap="large")
    
    with col_img:
        # Container untuk gambar dengan efek modern
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        try:
            st.image("Smart Water Tank.jpg", use_container_width=True)
        except:
            st.warning("Gambar tidak ditemukan.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tombol Test dengan styling modern
        if not PAKAI_FIREBASE_ASLI:
            st.markdown('<div style="margin-top: 15px;">', unsafe_allow_html=True)
            if st.button("Acak Nilai (Test Simulasi)", use_container_width=True):
                st.session_state.dummy_data['sensor']['water_level'] = round(random.uniform(20, 95), 1)
                st.session_state.dummy_data['sensor']['pressure'] = round(random.uniform(0.1, 0.9), 2)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Tombol refresh manual (opsional, karena sudah ada auto-refresh)
            st.markdown('<div style="margin-top: 15px;">', unsafe_allow_html=True)
            if st.button("🔄 Refresh Manual", use_container_width=True):
                sync_firebase_data()
                st.rerun()
            
            # Indikator auto-refresh aktif
            if AUTO_REFRESH_INSTALLED:
                st.info("🔄 Auto-refresh aktif setiap 2 detik")
            else:
                st.warning("⚠️ Auto-refresh tidak aktif. Install: pip install streamlit-autorefresh")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col_stats:
        # Container utama untuk statistik cards
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        
        # 1. Level Air dengan Progress Bar - Card Besar
        level_color = "#2ecc71" if lvl > 50 else "#f39c12" if lvl > 20 else "#e74c3c"
        st.markdown(f"""
        <div class="data-card" style="background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, rgba(46, 204, 113, 0.05) 100%); border-color: {level_color}40;">
            <div class="data-row" style="margin-bottom: 12px;">
                <span class="data-label" style="font-size: 1.1rem;">
                    Persentase Level Air
                </span>
                <span class="data-value" style="font-size: 2rem; color: {level_color};">{lvl}%</span>
            </div>
            <div class="progress-container" style="height: 20px; border-radius: 10px;">
                <div class="progress-bar" style="width: {lvl}%; background: linear-gradient(90deg, {level_color} 0%, {level_color}cc 100%); box-shadow: 0 0 20px {level_color}80;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.85rem; color: #a0a0a0;">
                <span>0%</span>
                <span>50%</span>
                <span>100%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Tekanan Air - Card Modern
        st.markdown(f"""
        <div class="data-card" style="background: linear-gradient(135deg, rgba(76, 201, 240, 0.1) 0%, rgba(76, 201, 240, 0.05) 100%);">
            <div class="data-row">
                <span class="data-label">
                    Tekanan Air
                </span>
                <span class="data-value" style="font-size: 1.5rem;">{pres} <span style="font-size: 1rem;">MPa</span></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 3. Status Pompa - Card dengan Animasi
        status_text = "ON" if pump else "OFF"
        status_class = "pump-on" if pump else "pump-off"
        pump_color = "#2ecc71" if pump else "#e74c3c"
        st.markdown(f"""
        <div class="data-card" style="background: linear-gradient(135deg, {pump_color}15 0%, {pump_color}05 100%); border-color: {pump_color}40;">
            <div class="data-row">
                <span class="data-label">
                    <span class="icon" style="font-size: 1.5rem;"></span>
                    Status Pompa
                </span>
                <span class="{status_class}" style="font-size: 1.1rem; padding: 10px 20px;">{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 4. Mode Aktif - Card Modern
        mode_color = "#fca311" if mode == "AUTO" else "#9b59b6"
        st.markdown(f"""
        <div class="data-card" style="background: linear-gradient(135deg, {mode_color}15 0%, {mode_color}05 100%); border-color: {mode_color}40;">
            <div class="data-row">
                <span class="data-label">
                    <span class="icon" style="font-size: 1.5rem;"></span>
                    Mode Aktif
                </span>
                <span class="mode-badge" style="font-size: 1.1rem; padding: 10px 20px;">{mode}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close main-container
    st.markdown('</div>', unsafe_allow_html=True)  # Close image/stats section
    
    # Bagian 2: Kontrol Panel
    st.markdown('<div style="margin-top: 25px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.3rem; font-weight: 600; color: #4cc9f0; margin-bottom: 15px; text-align: center;">KONTROL PANEL</div>', unsafe_allow_html=True)
    
    control_col1, control_col2 = st.columns([1, 1], gap="large")
    
    with control_col1:
        # Container untuk Mode Control
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 1.1rem; font-weight: 600; color: #e0e0e0; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">Ubah Mode Kontrol</div>', unsafe_allow_html=True)
        
        modes = ["AUTO", "MANUAL"]
        idx = 0 if mode == "AUTO" else 1
        new_mode = st.selectbox("Pilih Mode", modes, index=idx, label_visibility="collapsed", key="mode_select")
        
        if new_mode != mode:
            update_mode(new_mode)
            time.sleep(0.3)
            st.rerun()
        
        # Info box untuk mode
        if mode == "AUTO":
            st.info("**Mode AUTO**: Pompa akan otomatis menyala/mati berdasarkan level air.")
        else:
            st.info("**Mode MANUAL**: Kontrol pompa secara manual menggunakan tombol di bawah.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with control_col2:
        # Container untuk Manual Control
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 1.1rem; font-weight: 600; color: #e0e0e0; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">Kontrol Manual Pompa</div>', unsafe_allow_html=True)
        
        if mode == "MANUAL":
            # Tombol kontrol dengan styling lebih menarik
            btn_col1, btn_col2 = st.columns(2, gap="medium")
            with btn_col1:
                if st.button("START POMPA", type="primary", use_container_width=True, key="start_pump"):
                    update_pump(True)
                    st.rerun()
            with btn_col2:
                if st.button("STOP POMPA", type="secondary", use_container_width=True, key="stop_pump"):
                    update_pump(False)
                    st.rerun()
            
            # Status indicator
            if pump:
                st.success("Pompa sedang **AKTIF**")
            else:
                st.error("Pompa sedang **NONAKTIF**")
        else:
            st.warning("Mode AUTO aktif. Kontrol manual tidak tersedia.")
            st.markdown('<div style="padding: 20px; text-align: center; color: #a0a0a0; font-size: 0.9rem;">Ubah ke mode MANUAL untuk mengaktifkan kontrol manual.</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close control section
    st.markdown('</div>', unsafe_allow_html=True)  # Close dashboard-container
    

# ==========================================
# FUNGSI MAIN
# ==========================================
def main():
    """Fungsi utama untuk mengatur tampilan"""
    if not st.session_state.show_dashboard:
        show_home_screen()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
