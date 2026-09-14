import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="J.A.R.V.I.S. CORE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ล้าง Padding และขอบขาวของ Streamlit ออกให้หมด 100%
st.markdown("""
<style>
    #MainMenu, header, footer, .stDeployButton { display: none !important; }
    div[data-testid="stAppViewBlockContainer"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        overflow: hidden !important;
    }
    iframe {
        border: none !important;
        width: 100vw !important;
        height: 100vh !important;
    }
</style>
""", unsafe_allow_html=True)

# ดึงโครงสร้าง HTML/CSS ตัวดั้งเดิมที่จัดตำแหน่งตรงเป๊ะ
ORIGINAL_JARVIS_UI = """
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <style>
    :root {
      --bg: #060a17;
      --neon-cyan: #00f2fe;
      --neon-blue: #38bdf8;
      --neon-violet: #a855f7;
      --text-dim: #738a9c;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; user-select: none; }
    html, body {
      width: 100%;
      height: 100%;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: radial-gradient(circle at 50% 48%, #0d223a 0%, #060a17 65%, #03050c 100%);
      color: #ffffff;
    }

    /* จัดทุกอย่างให้อยู่กึ่งกลางหน้าจอเป๊ะ */
    .view-screen {
      display: none;
      width: 100vw;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
    }

    /* เอฟเฟกต์คลื่นกระแทกเวลาเชื่อมต่อ */
    .pulse-shockwave {
      position: fixed; top: 50%; left: 50%;
      transform: translate(-50%, -50%) scale(0);
      width: 60px; height: 60px; border-radius: 50%;
      border: 3px solid var(--neon-cyan);
      box-shadow: 0 0 50px var(--neon-cyan);
      pointer-events: none; opacity: 0; z-index: 999;
    }
    .pulse-shockwave.active { animation: shockwaveExpand 0.7s forwards; }
    @keyframes shockwaveExpand {
      0% { transform: translate(-50%, -50%) scale(0.1); opacity: 1; }
      100% { transform: translate(-50%, -50%) scale(40); opacity: 0; }
    }

    .stark-logo {
      width: 84px; height: 84px; margin-bottom: 26px; cursor: pointer;
      filter: drop-shadow(0 0 16px rgba(0, 242, 254, 0.8));
      transition: transform 0.35s ease;
    }
    .stark-logo:hover { transform: scale(1.1) rotate(45deg); }

    .brand-title {
      font-size: 2.1rem;
      letter-spacing: 0.38em;
      font-weight: 700;
      color: #ffffff;
      margin-bottom: 8px;
      text-transform: uppercase;
    }

    .brand-sub {
      font-size: 0.72rem;
      letter-spacing: 0.22em;
      color: var(--text-dim);
      margin-bottom: 34px;
      text-transform: uppercase;
    }

    /* ปุ่มกดตรงกลาง สไตล์แบบเดิมเป๊ะ */
    .btn-connect {
      background: rgba(8, 22, 42, 0.75);
      border: 1.2px solid rgba(0, 242, 254, 0.45);
      color: #ffffff;
      font-size: 0.92rem;
      font-weight: 500;
      letter-spacing: 0.08em;
      border-radius: 6px;
      padding: 10px 42px;
      box-shadow: 0 0 16px rgba(0, 242, 254, 0.15);
      cursor: pointer;
      transition: all 0.25s ease;
      outline: none;
    }
    .btn-connect:hover {
      border-color: var(--neon-cyan);
      background: rgba(0, 242, 254, 0.18);
      box-shadow: 0 0 28px rgba(0, 242, 254, 0.45);
      color: var(--neon-cyan);
      transform: scale(1.02);
    }
  </style>
</head>
<body>

  <div id="shockwave" class="pulse-shockwave"></div>

  <div class="view-screen">
    <!-- โลโก้แปดเหลี่ยม -->
    <div class="stark-logo" onclick="playBeep(1100)">
      <svg viewBox="0 0 100 100">
        <polygon points="50,6 88,24 94,62 68,94 32,94 6,62 12,24" stroke="var(--neon-cyan)" stroke-width="2.5" fill="none"/>
        <polygon points="50,18 78,32 82,60 62,82 38,82 18,60 22,32" stroke="var(--neon-blue)" stroke-width="2.5" fill="none" opacity="0.85"/>
        <circle cx="50" cy="50" r="7.5" fill="var(--neon-cyan)"/>
      </svg>
    </div>

    <!-- ข้อความกลางจอ -->
    <h1 class="brand-title">J . A . R . V . I . S . &nbsp; C O R E</h1>
    <p class="brand-sub">SYSTEM READY • DESKTOP EDITION</p>

    <!-- ปุ่มเริ่มระบบ -->
    <button class="btn-connect" onclick="connectCore()">เริ่มต้นเชื่อมต่อระบบ</button>
  </div>

  <script>
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    function playBeep(freq = 750, dur = 0.08) {
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + dur);
    }

    function connectCore() {
      playBeep(900, 0.25);
      const wave = document.getElementById('shockwave');
      wave.classList.add('active');
      setTimeout(() => {
        alert('เชื่อมต่อระบบ J.A.R.V.I.S. Core สมบูรณ์');
        wave.classList.remove('active');
      }, 650);
    }
  </script>
</body>
</html>
"""

components.html(ORIGINAL_JARVIS_UI, height=850, scrolling=False)
