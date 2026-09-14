import os
import re
import tempfile
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st

try:
  from moviepy.editor import VideoFileClip
except Exception:
  try:
    from moviepy import VideoFileClip
  except Exception:
    VideoFileClip = None

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key and "GEMINI_API_KEY" in st.secrets:
  api_key = st.secrets["GEMINI_API_KEY"]

st.set_page_config(
    page_title="J.A.R.V.I.S. CORE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    header, [data-testid="stHeader"], footer, #MainMenu, .stDeployButton { display: none !important; }
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #060a17 !important;
        background: radial-gradient(circle at 50% 40%, #0d1e36 0%, #060a17 70%, #02040a 100%) !important;
        color: #ffffff !important;
    }
    .block-container {
        padding-top: 2rem !important;
        max-width: 1100px !important;
    }
    div.stButton > button {
        background: rgba(14, 23, 44, 0.85) !important;
        border: 1px solid rgba(0, 242, 254, 0.45) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        transition: all 0.25s ease !important;
    }
    div.stButton > button:hover {
        border-color: #00f2fe !important;
        background: rgba(0, 242, 254, 0.18) !important;
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.35) !important;
        color: #00f2fe !important;
    }
    .stTextArea textarea {
        background: rgba(5, 10, 22, 0.95) !important;
        border: 1px solid rgba(0, 242, 254, 0.35) !important;
        color: #f8fafc !important;
        border-radius: 8px !important;
        font-family: monospace !important;
        line-height: 1.6 !important;
    }
    [data-testid="stFileUploader"] {
        border: 1px dashed rgba(0, 242, 254, 0.4) !important;
        border-radius: 10px !important;
        padding: 8px !important;
        background: rgba(10, 18, 36, 0.3) !important;
    }
    .stream-box {
        background: rgba(5, 10, 22, 0.95);
        border: 1px solid #00f2fe;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
        border-radius: 8px;
        padding: 16px;
        color: #e2e8f0;
        font-family: monospace;
        line-height: 1.6;
        min-height: 240px;
        white-space: pre-wrap;
    }
    .jarvis-popup {
        position: fixed;
        top: 24px;
        right: 24px;
        z-index: 999999;
        background: rgba(10, 20, 42, 0.94);
        border: 1px solid #00f2fe;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.45);
        border-radius: 10px;
        padding: 14px 22px;
        color: #00f2fe;
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.92rem;
        display: flex;
        align-items: center;
        gap: 12px;
        backdrop-filter: blur(8px);
    }
    .pulse-dot {
        width: 10px;
        height: 10px;
        background-color: #00f2fe;
        border-radius: 50%;
        box-shadow: 0 0 10px #00f2fe;
        animation: blink 1.2s infinite ease-in-out;
    }
    @keyframes blink {
        0%, 100% { opacity: 0.3; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1.2); }
    }
</style>
""",
    unsafe_allow_html=True,
)


def sanitize_for_speech(text):
  substitutions = {
      "J.A.R.V.I.S.": "จาร์วิส",
      "JARVIS": "จาร์วิส",
      "Dashboard": "แดชบอร์ด",
      "Video to Text": "วิดีโอ ทู เท็กซ์",
      "Stitch UI Designer": "สติทช์ ยูไอ ดีไซเนอร์",
      "Matrix Monitor": "เมทริกซ์ มอนิเตอร์",
      "Streaming": "สตรีมมิ่ง",
      "Standard": "สแตนดาร์ด",
      "Online": "ออนไลน์",
      "AI": "เอไอ",
  }
  cleaned = str(text)
  for eng, th in substitutions.items():
    cleaned = re.sub(re.escape(eng), th, cleaned, flags=re.IGNORECASE)
  return cleaned.replace('"', "").replace("'", "")


def trigger_jarvis_action(message, voice_text=None):
  if voice_text is None:
    voice_text = message

  st.markdown(
      f"""
    <div class="jarvis-popup">
        <div class="pulse-dot"></div>
        <div>
            <div style="font-size: 0.7rem; color: #94a3b8; letter-spacing: 1.5px;">J.A.R.V.I.S. PROTOCOL</div>
            <div style="font-weight: 600;">{message}</div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  phonetic_text = (
      sanitize_for_speech(voice_text).replace("\\", "\\\\").replace('"', '\\"')
  )

  js_template = """
        <script>
            (function() {
                if (!window.speechSynthesis) return;
                window.speechSynthesis.cancel();

                function executeSpeech() {
                    const utter = new SpeechSynthesisUtterance("__PHONETIC_TEXT__");
                    utter.lang = "th-TH";
                    utter.rate = 1.02;
                    utter.pitch = 0.92;

                    const voices = window.speechSynthesis.getVoices();
                    let bestVoice = voices.find(v => v.lang.includes("th") && (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Online")));
                    if (!bestVoice) {
                        bestVoice = voices.find(v => v.lang.includes("th"));
                    }
                    if (bestVoice) utter.voice = bestVoice;

                    window.speechSynthesis.speak(utter);
                }

                if (window.speechSynthesis.getVoices().length > 0) {
                    executeSpeech();
                } else {
                    window.speechSynthesis.onvoiceschanged = executeSpeech;
                }
            })();
        </script>
    """
  js_code = js_template.replace("__PHONETIC_TEXT__", phonetic_text)
  st.components.v1.html(js_code, height=0, width=0)


if "view" not in st.session_state:
  st.session_state.view = "landing"
if "welcomed" not in st.session_state:
  st.session_state.welcomed = False


def switch_to(v):
  st.session_state.view = v
  st.rerun()


STARK_LOGO_SVG = """
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 24px;">
  <svg viewBox="0 0 100 100" style="width: 82px; height: 82px; filter: drop-shadow(0 0 16px rgba(0, 242, 254, 0.8));">
    <polygon points="50,6 88,24 94,62 68,94 32,94 6,62 12,24" stroke="#00f2fe" stroke-width="2.5" fill="none"/>
    <polygon points="50,18 78,32 82,60 62,82 38,82 18,60 22,32" stroke="#38bdf8" stroke-width="2.5" fill="none" opacity="0.85"/>
    <circle cx="50" cy="50" r="7.5" fill="#00f2fe"/>
  </svg>
</div>
"""

# ========================================================
# 1. หน้า Landing
# ========================================================
if st.session_state.view == "landing":
  if not st.session_state.welcomed:
    trigger_jarvis_action(
        "SYSTEM READY: ยินดีต้อนรับเข้าสู่ระบบ จาร์วิส",
        "ยินดีต้อนรับเข้าสู่ระบบ จาร์วิส ระบบพร้อมปฏิบัติการแล้วครับ",
    )
    st.session_state.welcomed = True

  st.markdown("<div style='height: 22vh;'></div>", unsafe_allow_html=True)
  st.markdown(STARK_LOGO_SVG, unsafe_allow_html=True)
  st.markdown(
      """
        <div style="text-align: center;">
            <h1 style="font-size: 2.1rem; letter-spacing: 0.38em; font-weight: 700; color: #ffffff; margin-bottom: 8px; text-transform: uppercase;">
                J . A . R . V . I . S . &nbsp; C O R E
            </h1>
            <p style="font-size: 0.72rem; letter-spacing: 0.22em; color: #738a9c; margin-bottom: 34px; text-transform: uppercase;">
                HIGH VELOCITY INTERFACE • FLUID AUDIO CORE
            </p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  col_btn = st.columns([2, 1, 2])
  with col_btn[1]:
    if st.button("เริ่มต้นเชื่อมต่อระบบ", use_container_width=True):
      switch_to("dashboard")

# ========================================================
# 2. หน้า Dashboard
# ========================================================
elif st.session_state.view == "dashboard":
  st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)
  c1, c2 = st.columns([5, 1])
  with c1:
    st.markdown(
        "<h1 style='font-size: 1.85rem; font-weight: 700; color: #00f2fe; margin:"
        " 0;'>ระบบสั่งการหลัก</h1>",
        unsafe_allow_html=True,
    )
  with c2:
    if st.button("ตัดการเชื่อมต่อ"):
      st.session_state.welcomed = False
      switch_to("landing")

  st.markdown(
      "<hr style='border:none; border-bottom:1px solid"
      " rgba(255,255,255,0.08); margin: 20px 0;'>",
      unsafe_allow_html=True,
  )

  col_l, col_r = st.columns(2)
  with col_l:
    st.markdown(
        """
            <div style="background: rgba(11, 19, 38, 0.75); border: 1px solid rgba(168, 85, 247, 0.45); border-radius: 14px; padding: 22px; margin-bottom: 12px;">
                <span style="font-size: 0.72rem; color: #a855f7; background: rgba(168, 85, 247, 0.15); padding: 4px 10px; border-radius: 20px;">ACOUSTIC ENGINE</span>
                <h3 style="margin-top: 12px; margin-bottom: 6px;">🎬 Video to Text</h3>
                <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5;">สกัดคลื่นเสียงบริสุทธิ์ ถอดคำพูดและเนื้อเพลงตามเวลาจริง</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "เปิดใช้งาน Video to Text ⚡", key="btn_v2t", use_container_width=True
    ):
      switch_to("v2t")

    st.markdown(
        """
            <div style="background: rgba(11, 19, 38, 0.75); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 14px; padding: 22px; margin-top: 16px; margin-bottom: 12px;">
                <span style="font-size: 0.72rem; color: #00f2fe; background: rgba(0, 242, 254, 0.1); padding: 4px 10px; border-radius: 20px;">ENGINE 01</span>
                <h3 style="margin-top: 12px; margin-bottom: 6px;">🎨 Stitch UI Designer</h3>
                <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5;">ออกแบบหน้าจอแสดงผลกระจกไซไฟแบบเรียลไทม์</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "เปิด Stitch UI Designer 🎨", key="btn_stitch", use_container_width=True
    ):
      switch_to("stitch")

  with col_r:
    st.markdown(
        """
            <div style="background: rgba(11, 19, 38, 0.75); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 14px; padding: 22px; margin-bottom: 12px;">
                <span style="font-size: 0.72rem; color: #00f2fe; background: rgba(0, 242, 254, 0.1); padding: 4px 10px; border-radius: 20px;">CORE BRAIN</span>
                <h3 style="margin-top: 12px; margin-bottom: 6px;">⚡ J.A.R.V.I.S. Chat</h3>
                <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5;">สนทนาโต้ตอบ ปัญญาประดิษฐ์ระดับสูงแบบเรียลไทม์</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "เปิดหน้าต่างแชท J.A.R.V.I.S. 💬", key="btn_chat", use_container_width=True
    ):
      switch_to("chat")

    st.markdown(
        """
            <div style="background: rgba(11, 19, 38, 0.75); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 14px; padding: 22px; margin-top: 16px; margin-bottom: 12px;">
                <span style="font-size: 0.72rem; color: #00f2fe; background: rgba(0, 242, 254, 0.1); padding: 4px 10px; border-radius: 20px;">ENGINE 03</span>
                <h3 style="margin-top: 12px; margin-bottom: 6px;">🌐 Matrix Monitor</h3>
                <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5;">มอนิเตอร์สถานะเซิร์ฟเวอร์และการเชื่อมต่อเครือข่าย</p>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "เปิด Matrix Monitor 🌐", key="btn_matrix", use_container_width=True
    ):
      switch_to("matrix")

# ========================================================
# 3. หน้า Video to Text
# ========================================================
elif st.session_state.view == "v2t":
  col_t1, col_t2 = st.columns([4, 1])
  with col_t1:
    if st.button("← ย้อนกลับไปหน้าระบบต่างๆ"):
      switch_to("dashboard")
  with col_t2:
    st.markdown(
        "<p style='text-align: right; color: #a855f7; font-size:"
        " 0.82rem;'>NEURAL AUDIO EXTRACTION</p>",
        unsafe_allow_html=True,
    )

  st.markdown(
      "<hr style='border: none; border-bottom: 1px solid"
      " rgba(255,255,255,0.06); margin-bottom: 20px;'>",
      unsafe_allow_html=True,
  )

  col1, col2 = st.columns([1, 1], gap="medium")

  with col1:
    uploaded_video = st.file_uploader(
        "รองรับ MP4, WEBM, MOV", type=["mp4", "webm", "mov"]
    )
    if uploaded_video:
      st.video(uploaded_video)
      st.caption(f"ไฟล์: {uploaded_video.name}")

  with col2:
    if "transcribed_text" not in st.session_state:
      st.session_state.transcribed_text = "รอการประมวลผล..."

    display_placeholder = st.empty()
    display_placeholder.text_area(
        "ข้อความที่ถอดได้:",
        value=st.session_state.transcribed_text,
        height=240,
        label_visibility="collapsed",
    )

    st.markdown(
        "<p style='font-size: 0.78rem; color: #738a9c; margin-bottom:"
        " 4px;'>เลือกระบบประมวลผล:</p>",
        unsafe_allow_html=True,
    )

    btn_c1, btn_c2, btn_c3 = st.columns([1.5, 1.8, 1])
    with btn_c1:
      run_standard = st.button("⚡ 1. ถอดละเอียด", use_container_width=True)
    with btn_c2:
      run_upgrade = st.button("🚀 2. สตรีมสด", use_container_width=True)
    with btn_c3:
      download_data = (
          st.session_state.transcribed_text
          if st.session_state.transcribed_text != "รอการประมวลผล..."
          else ""
      )
      st.download_button(
          "📥 ดาวน์โหลด",
          data=download_data,
          file_name="transcript.txt",
          disabled=(download_data == ""),
          use_container_width=True,
      )

    PURE_AUDIO_INSTRUCTION = """You are a dedicated acoustic speech-to-text engine.
Transcribe all vocalized speech and sung lyrics sequentially from 00:00 to EOF.
1. End-of-file completion: Never truncate early.
2. Thai Verbatim: Keep colloquial particles 'วะ', 'เนี่ย', 'ว่ะ', 'นะ', 'หรอ'. Do not sanitize or summarize.
3. If muffled, output [ฟังไม่ชัด]. Format: [MM:SS] [ผู้พูด/เสียงร้อง]: ข้อความ"""

    USER_AUDIO_PROMPT = (
        "Transcribe all dialogue and vocal lyrics in this file from start to"
        " finish line-by-line."
    )

    def process_and_upload_audio(client, file_obj):
      ext = "." + file_obj.name.split(".")[-1]
      with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_vid:
        tmp_vid.write(file_obj.getvalue())
        vid_path = tmp_vid.name

      target_path = vid_path
      if VideoFileClip is not None:
        try:
          audio_path = vid_path + ".mp3"
          video_clip = VideoFileClip(vid_path)
          if video_clip.audio is not None:
            video_clip.audio.write_audiofile(audio_path, logger=None)
            video_clip.close()
            target_path = audio_path
          else:
            video_clip.close()
        except Exception:
          pass

      uploaded_file = client.files.upload(file=target_path)
      while uploaded_file.state.name == "PROCESSING":
        time.sleep(1)
        uploaded_file = client.files.get(name=uploaded_file.name)

      return uploaded_file, vid_path, target_path

    def call_gemini_engine(client, contents, stream=False):
      config = types.GenerateContentConfig(
          system_instruction=PURE_AUDIO_INSTRUCTION,
          temperature=0.0,
          max_output_tokens=8192,
      )
      max_retries = 3
      for attempt in range(max_retries):
        try:
          if stream:
            return client.models.generate_content_stream(
                model="gemini-3.6-flash", contents=contents, config=config
            )
          else:
            return client.models.generate_content(
                model="gemini-3.6-flash", contents=contents, config=config
            )
        except Exception as err:
          if "503" in str(err) and attempt < max_retries - 1:
            time.sleep(3)
            continue
          raise err

    if run_standard:
      if not uploaded_video:
        trigger_jarvis_action(
            "คำเตือน: ไม่พบไฟล์", "กรุณาเลือกไฟล์วิดีโอก่อนทำการประมวลผลครับ"
        )
      elif not api_key:
        st.error("ไม่พบคีย์ API ในระบบ")
      else:
        trigger_jarvis_action(
            "กำลังประมวลผล: ถอดเสียงละเอียด",
            "ระบบกำลังเริ่มประมวลผล กรุณารอสักครู่ครับ",
        )
        with st.spinner("J.A.R.V.I.S. กำลังวิเคราะห์คลื่นเสียง..."):
          v_path, a_path = None, None
          try:
            client = genai.Client(api_key=api_key)
            audio_file, v_path, a_path = process_and_upload_audio(
                client, uploaded_video
            )
            response = call_gemini_engine(
                client, [audio_file, USER_AUDIO_PROMPT], stream=False
            )
            st.session_state.transcribed_text = response.text
            trigger_jarvis_action(
                "สถานะ: ถอดเสียงสมบูรณ์",
                "การแปลงข้อความเสร็จสมบูรณ์เรียบร้อยแล้วครับ",
            )
            st.rerun()
          except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
          finally:
            if v_path and os.path.exists(v_path):
              os.remove(v_path)
            if a_path and a_path != v_path and os.path.exists(a_path):
              os.remove(a_path)

    if run_upgrade:
      if not uploaded_video:
        trigger_jarvis_action(
            "คำเตือน: ไม่พบไฟล์", "กรุณาเลือกไฟล์วิดีโอก่อนทำการประมวลผลครับ"
        )
      elif not api_key:
        st.error("ไม่พบคีย์ API ในระบบ")
      else:
        trigger_jarvis_action(
            "กำลังเปิดช่องสัญญาณสตรีมสด",
            "กำลังเริ่มต้นระบบสตรีมสด กรุณารอสักครู่ครับ",
        )
        with st.spinner("J.A.R.V.I.S. กำลังสตรีมข้อความ..."):
          v_path, a_path = None, None
          try:
            client = genai.Client(api_key=api_key)
            audio_file, v_path, a_path = process_and_upload_audio(
                client, uploaded_video
            )
            stream_response = call_gemini_engine(
                client, [audio_file, USER_AUDIO_PROMPT], stream=True
            )

            accumulated_text = ""
            for chunk in stream_response:
              if chunk.text:
                accumulated_text += chunk.text
                display_placeholder.markdown(
                    f"<div class='stream-box'>{accumulated_text}▌</div>",
                    unsafe_allow_html=True,
                )

            st.session_state.transcribed_text = accumulated_text
            trigger_jarvis_action(
                "สถานะ: สตรีมสดสำเร็จ",
                "ระบบทำการสตรีมข้อความเสร็จสิ้นเรียบร้อยครับ",
            )
            st.rerun()
          except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
          finally:
            if v_path and os.path.exists(v_path):
              os.remove(v_path)
            if a_path and a_path != v_path and os.path.exists(a_path):
              os.remove(a_path)

  status_tag = (
      "COMPLETED"
      if st.session_state.transcribed_text != "รอการประมวลผล..."
      else "READY"
  )
  st.markdown(
      f"""
<div style='margin-top: 24px; padding: 14px 18px; border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 8px; background: rgba(5, 10, 22, 0.6);'>
    <div style='display: flex; justify-content: space-between; font-size: 0.78rem; color: #738a9c; margin-bottom: 8px;'>
        <span>FREQUENCY MONITOR</span>
        <span style='color: #00f2fe;'>{status_tag}</span>
    </div>
    <div style='color: #00f2fe; letter-spacing: 3px; font-size: 0.9rem;'>
        ❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚❚
    </div>
</div>
""",
      unsafe_allow_html=True,
  )

# ========================================================
# 4. หน้า Chat
# ========================================================
elif st.session_state.view == "chat":
  if st.button("← ย้อนกลับไปหน้าระบบต่างๆ"):
    switch_to("dashboard")

  st.markdown(
      "<h2 style='color: #00f2fe; margin-top: 10px;'>💬 J.A.R.V.I.S. Neural"
      " Assistant</h2>",
      unsafe_allow_html=True,
  )

  if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

  for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

  if prompt := st.chat_input("สั่งการ J.A.R.V.I.S...."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      trigger_jarvis_action(
          "กำลังประมวลผลข้อมูล", "กำลังประมวลผลคำตอบ กรุณารอสักครู่ครับ"
      )
      with st.spinner("J.A.R.V.I.S. กำลังคิด..."):
        try:
          client = genai.Client(api_key=api_key)
          res = client.models.generate_content(
              model="gemini-3.6-flash",
              contents=prompt,
              config=types.GenerateContentConfig(
                  system_instruction=(
                      "You are J.A.R.V.I.S., a witty and elite AI assistant. Always"
                      " respond concisely in Thai."
                  ),
                  temperature=0.5,
              ),
          )
          reply = res.text
          st.markdown(reply)
          st.session_state.chat_history.append(
              {"role": "assistant", "content": reply}
          )
          trigger_jarvis_action("คำตอบพร้อมใช้งาน", reply[:90])
        except Exception as e:
          st.error(f"เกิดข้อผิดพลาด: {e}")

# ========================================================
# 5. หน้า Stitch UI Designer
# ========================================================
elif st.session_state.view == "stitch":
  if st.button("← ย้อนกลับไปหน้าระบบต่างๆ"):
    switch_to("dashboard")

  st.markdown(
      "<h2 style='color: #00f2fe; margin-top: 10px;'>🎨 Stitch UI Designer"
      " Sandbox</h2>",
      unsafe_allow_html=True,
  )
  st.caption("ระบบจำลองและพรีวิวอินเทอร์เฟซกระจกไซไฟแบบเรียลไทม์")

  col_s1, col_s2 = st.columns(2)
  with col_s1:
    st.subheader("ตัวควบคุมการจัดรูปแบบ")
    neon_color = st.color_picker("เลือกสีนีออน HUD", "#00f2fe")
    glow_intensity = st.slider("ระดับแสงสะท้อน (Glow Intensity)", 5, 40, 20)
    border_radius = st.slider("ความโค้งของขอบกระจก (Border Radius)", 0, 30, 12)

  with col_s2:
    st.subheader("ตัวอย่างพรีวิว HUD กระจก")
    st.markdown(
        f"""
    <div style="background: rgba(10, 20, 42, 0.75); border: 2px solid {neon_color}; border-radius: {border_radius}px; padding: 24px; box-shadow: 0 0 {glow_intensity}px {neon_color}; backdrop-filter: blur(10px);">
        <h4 style="color: {neon_color}; margin-top: 0;">J.A.R.V.I.S. QUANTUM PANEL</h4>
        <p style="color: #cbd5e1; font-size: 0.9rem;">สถานะระบบ: ACTIVE<br>การเข้ารหัส: 512-BIT QUANTUM</p>
        <div style="height: 6px; width: 100%; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;">
            <div style="height: 100%; width: 75%; background: {neon_color};"></div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# ========================================================
# 6. หน้า Matrix Monitor
# ========================================================
elif st.session_state.view == "matrix":
  if st.button("← ย้อนกลับไปหน้าระบบต่างๆ"):
    switch_to("dashboard")

  st.markdown(
      "<h2 style='color: #00f2fe; margin-top: 10px;'>🌐 Matrix Telemetry &"
      " Network Monitor</h2>",
      unsafe_allow_html=True,
  )
  st.caption("ตรวจสอบสถานะคลัสเตอร์เซิร์ฟเวอร์ และทราฟฟิกข้อมูล")

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("CPU UTILIZATION", "14%", "-2%")
  m2.metric("MEMORY ALLOCATED", "4.2 GB", "+0.1 GB")
  m3.metric("API LATENCY", "128 ms", "-15 ms")
  m4.metric("SYSTEM INTEGRITY", "100%", "SECURE")

  st.markdown(
      "<hr style='border:none; border-bottom:1px solid"
      " rgba(255,255,255,0.08); margin: 20px 0;'>",
      unsafe_allow_html=True,
  )

  st.subheader("📡 Live Server Diagnostics")
  st.markdown(
      """
    <div style="background: rgba(5, 10, 22, 0.9); border: 1px solid rgba(0,242,254,0.3); border-radius: 8px; padding: 15px; font-family: monospace; color: #38bdf8; font-size: 0.85rem; line-height: 1.6;">
        [OK] Core Engine online: models/gemini-3.6-flash<br>
        [OK] Pure Acoustic Spectrogram Parser: ENABLED<br>
        [OK] Cloud Connection: TLS 1.3 / Encrypted Pipe<br>
        [OK] Fluid Voice Driver: READY
    </div>
    """,
      unsafe_allow_html=True,
  )