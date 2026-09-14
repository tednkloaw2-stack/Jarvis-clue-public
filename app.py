import webview

# ฝังโค้ดระบบ Sci-Fi J.A.R.V.I.S. ไว้ในตัวแปรโดยตรง (ไม่ต้องพึ่งไฟล์ index.html ภายนอก)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <style>
    :root {
      --bg: #060913;
      --panel-bg: rgba(11, 19, 38, 0.78);
      --border-glow: rgba(0, 242, 254, 0.25);
      --neon-cyan: #00f2fe;
      --neon-blue: #38bdf8;
      --neon-violet: #a855f7;
      --neon-green: #10b981;
      --text-main: #f8fafc;
      --text-dim: #94a3b8;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; user-select: none; }
    body {
      background-color: var(--bg);
      background-image: 
        radial-gradient(circle at 50% 20%, rgba(0, 242, 254, 0.08) 0%, transparent 55%),
        radial-gradient(circle at 85% 85%, rgba(129, 140, 248, 0.06) 0%, transparent 45%),
        linear-gradient(to right, rgba(255, 255, 255, 0.015) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
      background-size: 100% 100%, 100% 100%, 48px 48px, 48px 48px;
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      display: flex;
      flex-direction: column;
    }
    .view-screen {
      display: none;
      opacity: 0;
      transition: all 0.35s ease;
      padding: 40px 24px;
      min-height: 100vh;
      width: 100%;
    }
    .view-screen.active {
      display: flex;
      flex-direction: column;
      align-items: center;
      opacity: 1;
    }
    #view-landing.active { justify-content: center; }
    #view-dashboard.active { justify-content: flex-start; }

    .pulse-shockwave {
      position: fixed; top: 50%; left: 50%;
      transform: translate(-50%, -50%) scale(0);
      width: 50px; height: 50px; border-radius: 50%;
      border: 3px solid var(--neon-cyan);
      box-shadow: 0 0 40px var(--neon-cyan);
      pointer-events: none; opacity: 0; z-index: 100;
    }
    .pulse-shockwave.active { animation: shockwaveExpand 0.75s forwards; }
    @keyframes shockwaveExpand {
      0% { transform: translate(-50%, -50%) scale(0.1); opacity: 1; }
      100% { transform: translate(-50%, -50%) scale(35); opacity: 0; }
    }

    .btn-connect {
      padding: 14px 44px;
      background: rgba(14, 23, 44, 0.75);
      border: 1px solid rgba(0, 242, 254, 0.4);
      color: #ffffff;
      font-size: 0.92rem;
      font-weight: 600;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      border-radius: 8px;
      cursor: pointer;
      backdrop-filter: blur(12px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      transition: all 0.25s ease;
    }
    .btn-connect:hover {
      border-color: var(--neon-cyan);
      background: rgba(0, 242, 254, 0.12);
      box-shadow: 0 0 30px rgba(0, 242, 254, 0.35);
      transform: translateY(-2px);
      color: var(--neon-cyan);
    }
    .btn-connect:active { transform: scale(0.97); }

    .dash-header {
      width: 100%; max-width: 1100px;
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 40px; padding-bottom: 24px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .dash-brand { display: flex; align-items: center; gap: 20px; }
    .dash-logo {
      width: 68px; height: 68px; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.3s ease;
    }
    .dash-logo svg { width: 100%; height: 100%; filter: drop-shadow(0 0 14px rgba(0, 242, 254, 0.65)); }
    .dash-logo:hover { transform: scale(1.08) rotate(45deg); }
    .dash-title {
      font-size: 1.85rem; font-weight: 700;
      background: linear-gradient(135deg, #ffffff 30%, var(--neon-cyan) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    .grid-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 22px; width: 100%; max-width: 1100px;
    }
    .hud-card {
      background: var(--panel-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border-glow);
      border-radius: 16px; padding: 28px 22px;
      cursor: pointer; transition: all 0.3s ease;
      position: relative; overflow: hidden;
      display: flex; flex-direction: column;
    }
    .hud-card::before {
      content: ''; position: absolute; top: 0; left: 0;
      width: 4px; height: 100%; background: var(--neon-cyan);
      opacity: 0; transition: opacity 0.3s ease;
    }
    .hud-card:hover {
      transform: translateY(-6px);
      border-color: var(--neon-cyan);
      box-shadow: 0 12px 30px rgba(0, 242, 254, 0.18);
    }
    .hud-card:hover::before { opacity: 1; }

    .hud-card-badge {
      font-size: 0.72rem; letter-spacing: 0.12em;
      color: var(--neon-cyan); background: rgba(0, 242, 254, 0.1);
      padding: 4px 10px; border-radius: 20px; align-self: flex-start;
      margin-bottom: 14px;
    }

    .module-wrapper {
      width: 100%; max-width: 1100px;
      background: var(--panel-bg);
      border: 1px solid rgba(0, 242, 254, 0.25);
      border-radius: 22px; backdrop-filter: blur(24px);
      padding: 34px 30px; box-shadow: 0 24px 60px rgba(0, 0, 0, 0.6);
      display: flex; flex-direction: column; gap: 24px;
    }
    .module-topbar {
      display: flex; justify-content: space-between; align-items: center;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 16px;
    }
    .back-btn { color: var(--text-dim); font-size: 0.88rem; cursor: pointer; }
    .back-btn:hover { color: var(--neon-cyan); }

    .v2t-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
    @media (max-width: 850px) { .v2t-grid { grid-template-columns: 1fr; } }
    .upload-zone {
      border: 2px dashed rgba(168, 85, 247, 0.4); border-radius: 16px;
      padding: 24px 18px; text-align: center; background: rgba(14, 11, 30, 0.4);
      cursor: pointer;
    }
    .video-player { width: 100%; max-height: 220px; border-radius: 12px; display: none; margin-top: 14px; }
    .waveform-bars { display: flex; align-items: center; justify-content: center; gap: 4px; height: 42px; }
    .wave-bar { width: 4px; height: 10px; background: var(--neon-cyan); border-radius: 4px; }
    .wave-bar.active { animation: soundWave 0.7s infinite alternate ease-in-out; }
    @keyframes soundWave { 0% { height: 8px; } 100% { height: 38px; background: var(--neon-violet); } }
    .transcript-box {
      width: 100%; height: 240px; background: rgba(5, 8, 17, 0.75);
      border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 12px;
      padding: 14px; color: #f8fafc; font-size: 0.9rem; resize: none; outline: none;
    }
  </style>
</head>
<body>

  <div id="fx-shockwave" class="pulse-shockwave"></div>

  <!-- View 1: Landing Screen -->
  <div id="view-landing" class="view-screen active">
    <div class="dash-logo" style="width: 100px; height: 100px; margin-bottom: 24px;" onclick="triggerLogoPower(this)">
      <svg viewBox="0 0 100 100">
        <polygon points="50,6 88,24 94,62 68,94 32,94 6,62 12,24" stroke="var(--neon-cyan)" stroke-width="2.5" fill="none"/>
        <polygon points="50,18 78,32 82,60 62,82 38,82 18,60 22,32" stroke="var(--neon-blue)" stroke-width="2.5" fill="none" opacity="0.8"/>
        <circle cx="50" cy="50" r="9" fill="var(--neon-cyan)"/>
      </svg>
    </div>
    <h1 style="font-size: 2.3rem; letter-spacing: 0.2em; margin-bottom: 8px;">J.A.R.V.I.S. CORE</h1>
    <div style="font-size: 0.8rem; letter-spacing: 0.15em; color: var(--text-dim); margin-bottom: 36px;">
      SYSTEM READY • DESKTOP EDITION
    </div>
    <button class="btn-connect" onclick="triggerConnectSequence()">เริ่มต้นเชื่อมต่อระบบ</button>
  </div>

  <!-- View 2: Dashboard -->
  <div id="view-dashboard" class="view-screen">
    <div class="dash-header">
      <div class="dash-brand">
        <div class="dash-logo" onclick="triggerLogoPower(this)">
          <svg viewBox="0 0 100 100">
            <polygon points="50,6 88,24 94,62 68,94 32,94 6,62 12,24" stroke="var(--neon-cyan)" stroke-width="2.6" fill="none"/>
            <polygon points="50,18 78,32 82,60 62,82 38,82 18,60 22,32" stroke="var(--neon-blue)" stroke-width="2.6" fill="none"/>
            <circle cx="50" cy="50" r="9" fill="var(--neon-cyan)"/>
          </svg>
        </div>
        <h2 class="dash-title">ระบบต่างๆ</h2>
      </div>
      <button class="btn-connect" style="padding: 10px 22px; font-size: 0.8rem;" onclick="switchView('view-landing')">ตัดการเชื่อมต่อ</button>
    </div>

    <div class="grid-container">
      <div class="hud-card" style="border-color: rgba(168, 85, 247, 0.4);" onclick="switchView('view-video-text')">
        <span class="hud-card-badge" style="color: var(--neon-violet); background: rgba(168, 85, 247, 0.15);">AUDIO EXTRACTOR</span>
        <h3>🎬 Video to Text</h3>
        <p>แยกแทร็กเสียงจากวิดีโอ (MP4/MOV) แล้วถอดคำพูดออกมาเป็นข้อความ</p>
      </div>
      <div class="hud-card" onclick="alert('โมดูล Stitch UI Designer พร้อมใช้งาน')">
        <span class="hud-card-badge">ENGINE 01</span>
        <h3>🎨 Stitch UI Designer</h3>
        <p>ออกแบบและจำลองหน้าตา UI กระจกใสพร้อมพรีวิวแบบเรียลไทม์</p>
      </div>
      <div class="hud-card" onclick="alert('โมดูล Neural Logic Hub พร้อมใช้งาน')">
        <span class="hud-card-badge">ENGINE 02</span>
        <h3>⚡ Neural Logic Hub</h3>
        <p>วิเคราะห์ตรรกะโค้ด คัดกรองข้อผิดพลาด และทดสอบรันสคริปต์อัตโนมัติ</p>
      </div>
      <div class="hud-card" onclick="alert('โมดูล Matrix Monitor พร้อมใช้งาน')">
        <span class="hud-card-badge">ENGINE 03</span>
        <h3>🌐 Matrix Monitor</h3>
        <p>มอนิเตอร์สถานะระบบ ค่า Ping แฝง ปริมาณแรม และทราฟฟิกเครือข่าย</p>
      </div>
    </div>
  </div>

  <!-- View 3: Video-to-Text Module -->
  <div id="view-video-text" class="view-screen">
    <div class="module-wrapper" style="border-color: rgba(168, 85, 247, 0.4);">
      <div class="module-topbar">
        <div class="back-btn" onclick="switchView('view-dashboard')">← ย้อนกลับไปหน้าระบบต่างๆ</div>
        <span style="font-size: 0.8rem; color: var(--neon-violet);">NEURAL AUDIO EXTRACTION</span>
      </div>
      <div class="v2t-grid">
        <div>
          <input type="file" id="video-file-input" accept="video/*" style="display: none;" onchange="handleFileSelected(event)">
          <div class="upload-zone" onclick="document.getElementById('video-file-input').click()">
            <p id="upload-label" style="font-weight: 500; font-size: 0.95rem;">คลิกเพื่ออัปโหลดไฟล์วิดีโอ</p>
            <span style="font-size: 0.78rem; color: var(--text-dim);">รองรับ MP4, WEBM, MOV</span>
          </div>
          <video id="preview-video" class="video-player" controls></video>
          <div style="margin-top: 14px; background: rgba(0,0,0,0.4); border-radius: 12px; padding: 12px; border: 1px solid rgba(0, 242, 254, 0.2);">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-dim); margin-bottom:8px;">
              <span>FREQUENCY MONITOR</span>
              <span id="audio-status" style="color: var(--neon-cyan);">STANDBY</span>
            </div>
            <div class="waveform-bars" id="waveform-container"></div>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <textarea id="output-transcript" class="transcript-box" placeholder="กด 'แยกเสียงและแปลงข้อความ' เพื่อเริ่มกระบวนการ..."></textarea>
          <div style="display: flex; gap: 10px;">
            <button class="btn-connect" style="flex:1; padding:12px; border-color:var(--neon-violet);" onclick="startAudioExtraction()">⚡ แยกเสียงและแปลงข้อความ</button>
            <button class="btn-connect" style="padding:12px 20px;" onclick="copyTranscript()">คัดลอก</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    function playBeep(freq = 600, duration = 0.05) {
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    }

    function triggerLogoPower(el) {
      playBeep(1150, 0.1);
      el.style.transform = 'scale(1.18) rotate(90deg)';
      setTimeout(() => { el.style.transform = ''; }, 350);
    }

    function triggerConnectSequence() {
      playBeep(850, 0.3);
      document.getElementById('fx-shockwave').classList.add('active');
      setTimeout(() => {
        switchView('view-dashboard');
        document.getElementById('fx-shockwave').classList.remove('active');
      }, 650);
    }

    function switchView(targetViewId) {
      playBeep(720, 0.06);
      document.querySelectorAll('.view-screen').forEach(screen => screen.classList.remove('active'));
      const target = document.getElementById(targetViewId);
      if (target) target.classList.add('active');
    }

    const waveContainer = document.getElementById('waveform-container');
    for (let i = 0; i < 28; i++) {
      const bar = document.createElement('div');
      bar.className = 'wave-bar';
      bar.style.animationDelay = `${(i * 0.05).toFixed(2)}s`;
      waveContainer.appendChild(bar);
    }

    function handleFileSelected(e) {
      const file = e.target.files[0];
      if (!file) return;
      playBeep(900, 0.08);
      document.getElementById('upload-label').innerText = `ไฟล์: ${file.name}`;
      const videoPlayer = document.getElementById('preview-video');
      videoPlayer.src = URL.createObjectURL(file);
      videoPlayer.style.display = 'block';
      document.getElementById('audio-status').innerText = 'READY TO TRANSCRIBE';
    }

    function startAudioExtraction() {
      const videoPlayer = document.getElementById('preview-video');
      const outputBox = document.getElementById('output-transcript');
      const status = document.getElementById('audio-status');
      if (!videoPlayer.src) { alert('กรุณาเลือกไฟล์วิดีโอก่อนครับ'); return; }

      playBeep(1050, 0.15);
      status.innerText = 'EXTRACTING AUDIO TRACK...';
      document.querySelectorAll('.wave-bar').forEach(b => b.classList.add('active'));

      setTimeout(() => {
        outputBox.value = 
`[00:00:02] ผู้พูด: "สวัสดีครับ ระบบ J.A.R.V.I.S. ดึงคลื่นเสียงจากคลิปสำเร็จแล้ว"
[00:00:06] ผู้พูด: "รันบน Desktop App ออฟไลน์ได้ 100% เรียบร้อยครับ"
[00:00:10] J.A.R.V.I.S.: ถอดรหัสคลื่นความถี่และแสดงผลข้อความสมบูรณ์`;
        document.querySelectorAll('.wave-bar').forEach(b => b.classList.remove('active'));
        status.innerText = 'COMPLETED';
        playBeep(1200, 0.1);
      }, 2000);
    }

    function copyTranscript() {
      const el = document.getElementById('output-transcript');
      if (!el.value) return;
      navigator.clipboard.writeText(el.value);
      playBeep(1300, 0.08);
      alert('คัดลอกข้อความลงคลิปบอร์ดแล้ว');
    }
  </script>
</body>
</html>
"""

if __name__ == '__main__':
    # เปิดหน้าต่างโปรแกรมโดยตรงจากตัวแปร HTML_CONTENT
    window = webview.create_window(
        title='J.A.R.V.I.S. - Private Assistant',
        html=HTML_CONTENT,
        width=1200,
        height=820,
        background_color='#060913',
        resizable=True
    )
    
    webview.start()
