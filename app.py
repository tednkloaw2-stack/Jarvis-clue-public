import streamlit as st
import os
import tempfile
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

st.set_page_config(
    page_title="J.A.R.V.I.S. CORE",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# จัดการ State นำทาง
if "view" not in st.session_state:
    st.session_state.view = "landing"

def switch_to(target_view):
    st.session_state.view = target_view
    st.rerun()

# ==========================================
# CSS Overrides: ให้หน้าตาเหมือน Desktop App 100%
# ==========================================
if st.session_state.view == "landing":
    custom_css = """
    <style>
        #MainMenu, header, footer, .stDeployButton { visibility: hidden !important; display: none !important; }
        .stApp {
            background: radial-gradient(circle at 50% 48%, #0d223a 0%, #060a17 65%, #03050c 100%) !important;
            color: #ffffff !important;
            overflow: hidden !important;
        }
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100vw !important;
            height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
        }
        /* ปรับแต่งปุ่มกดกลางจอตามรูป */
        div.stButton {
            display: flex;
            justify-content: center;
        }
        div.stButton > button {
            background: rgba(8, 22, 42, 0.75) !important;
            border: 1.2px solid rgba(0, 242, 254, 0.45) !important;
            color: #ffffff !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.08em !important;
            border-radius: 6px !important;
            padding: 10px 42px !important;
            box-shadow: 0 0 16px rgba(0, 242, 254, 0.15) !important;
            transition: all 0.25s ease !important;
        }
        div.stButton > button:hover {
            border-color: #00f2fe !important;
            background: rgba(0, 242, 254, 0.18) !important;
            box-shadow: 0 0 28px rgba(0, 242, 254, 0.45) !important;
            color: #00f2fe !important;
            transform: scale(1.02) !important;
        }
        div.stButton > button:active {
            transform: scale(0.98) !important;
        }
    </style>
    """
else:
    custom_css = """
    <style>
        #MainMenu, header, footer, .stDeployButton { visibility: hidden !important; display: none !important; }
        .stApp {
            background-color: #060a17 !important;
            background-image: 
                radial-gradient(circle at 50% 15%, rgba(0, 242, 254, 0.08) 0%, transparent 60%),
                linear-gradient(to right, rgba(255, 255, 255, 0.015) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255, 255, 255, 0.015) 1px, transparent 1px) !important;
            background-size: 100% 100%, 48px 48px, 48px 48px !important;
            color: #f8fafc !important;
        }
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1080px !important;
        }
        div.stButton > button {
            background: rgba(14, 23, 44, 0.75) !important;
            border: 1px solid rgba(0, 242, 254, 0.4) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            transition: all 0.25s ease !important;
        }
        div.stButton > button:hover {
            border-color: #00f2fe !important;
            box-shadow: 0 0 20px rgba(0, 242, 254, 0.35) !important;
            color: #00f2fe !important;
        }
    </style>
    """

st.markdown(custom_css, unsafe_allow_html=True)

# โลโก้แปดเหลี่ยมเรืองแสง
STARK_LOGO_SVG = """
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 26px;">
  <svg viewBox="0 0 100 100" style="width: 82px; height: 82px; filter: drop-shadow(0 0 16px rgba(0, 242, 254, 0.8));">
    <polygon points="50,6 88,24 94,62 68,94 32,94 6,62 12,24" stroke="#00f2fe" stroke-width="2.5" fill="none"/>
    <polygon points="50,18 78,32 82,60 62,82 38,82 18,60 22,32" stroke="#38bdf8" stroke-width="2.5" fill="none" opacity="0.85"/>
    <circle cx="50" cy="50" r="7.5" fill="#00f2fe"/>
  </svg>
</div>
"""

# ==========================================
# 1. หน้า Landing: ถอดแบบจากรูปภาพ
# ==========================================
if st.session_state.view == "landing":
    st.markdown(STARK_LOGO_SVG, unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="font-size: 2.1rem; letter-spacing: 0.38em; font-weight: 700; color: #ffffff; margin-bottom: 8px; text-transform: uppercase;">
                J . A . R . V . I . S . &nbsp; C O R E
            </h1>
            <p style="font-size: 0.72rem; letter-spacing: 0.22em; color: #738a9c; margin-bottom: 34px; text-transform: uppercase;">
                SYSTEM READY • DESKTOP EDITION
            </p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("เริ่มต้นเชื่อมต่อระบบ"):
        switch_to("dashboard")

# ==========================================
# 2. หน้า Dashboard: ระบบต่างๆ
# ==========================================
elif st.session_state.view == "dashboard":
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
                <h1 style="font-size: 1.85rem; font-weight: 700; background: linear-gradient(135deg, #ffffff 30%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">
                    ระบบต่างๆ
                </h1>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("ตัดการเชื่อมต่อ"):
            switch_to("landing")

    st.markdown("<hr style='border: none; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 24px;'>", unsafe_allow_html=True)

    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("""
            <div style="background: rgba(11, 19, 38, 0.78); border: 1px solid rgba(168, 85, 247, 0.45); border-radius: 16px; padding: 22px; margin-bottom: 12px;">
                <span style="font-size: 0.72rem; letter-spacing: 0.12em; color: #a855f7; background: rgba(168, 85, 247, 0.15); padding: 4px 10px; border-radius: 20px;">AUDIO EXTRACTOR</span>
                <h3 style="margin-top: 12px; margin-bottom: 6px;">🎬 Video to Text</h3>
                <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5;">แยกแทร็กเสียงจากวิดีโอ (MP4/MOV) แล้วถอดคำพูดออกมาเป็นข้อความจริงด้วย Gemini AI</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("เปิดใช้งาน Video to Text ⚡", use_container_width=True):
            switch_to("v2t")

    with c_right:
        st.markdown("""
            <div style="background: rgba(11, 19, 38, 0.78); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 16px; padding: 22px; margin-bottom: 12px;">
                <span style="font-size: 0.72rem; letter-spacing: 0.12em; color: #00f2fe; background: rgba(0, 242, 254, 0.1); padding: 4px 10px; border-radius: 20px;">CORE BRAIN</span>
                <h3 style="margin-top: 12px; margin-bottom: 6px;">⚡ J.A.R.V.I.S. Chat & Logic</h3>
                <p style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5;">ระบบคุยสั่งการอัตโนมัติ คำนวณโค้ดเบื้องหลัง และจำประวัติการคุยต่อเนื่อง</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("เปิดหน้าต่างแชท J.A.R.V.I.S. 💬", use_container_width=True):
            switch_to("chat")

# ==========================================
# 3. หน้า Video to Text: แปลงไฟล์จริง
# ==========================================
elif st.session_state.view == "v2t":
    if st.button("← ย้อนกลับไปหน้าระบบต่างๆ"):
        switch_to("dashboard")

    st.markdown("<h2 style='color: #a855f7; margin-top: 14px;'>🎬 Video to Text Transcriber</h2>", unsafe_allow_html=True)
    
    col_v1, col_v2 = st.columns([1, 1])
    with col_v1:
        uploaded_video = st.file_uploader("เลือกไฟล์วิดีโอ (MP4, MOV, WEBM)", type=["mp4", "mov", "webm"])
        if uploaded_video:
            st.video(uploaded_video)

    with col_v2:
        if "v2t_result" not in st.session_state:
            st.session_state.v2t_result = ""

        if st.button("⚡ แยกเสียงและแปลงข้อความ", use_container_width=True):
            if not uploaded_video:
                st.error("กรุณาเลือกไฟล์วิดีโอก่อน")
            elif not api_key:
                st.error("ไม่พบคีย์ GEMINI_API_KEY")
            else:
                with st.spinner("J.A.R.V.I.S. กำลังวิเคราะห์คลื่นเสียง..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        suffix = "." + uploaded_video.name.split(".")[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(uploaded_video.getvalue())
                            tmp_path = tmp.name

                        video_file = client.files.upload(file=tmp_path)
                        while video_file.state.name == "PROCESSING":
                            time.sleep(2)
                            video_file = client.files.get(name=video_file.name)

                        res = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[video_file, "กรุณาถอดบทสนทนาจากคลิปนี้ตาม Timestamp และสรุปเนื้อหาสำคัญเป็นภาษาไทย"]
                        )
                        st.session_state.v2t_result = res.text
                        os.remove(tmp_path)
                        st.success("ถอดเสียงสำเร็จ!")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")

        st.text_area("ข้อความที่ได้:", value=st.session_state.v2t_result, height=260)

# ==========================================
# 4. หน้า Chat: สนทนากับ J.A.R.V.I.S.
# ==========================================
elif st.session_state.view == "chat":
    if st.button("← ย้อนกลับไปหน้าระบบต่างๆ"):
        switch_to("dashboard")

    st.markdown("<h2 style='color: #00f2fe; margin-top: 14px;'>💬 J.A.R.V.I.S. Neural Assistant</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if user_input := st.chat_input("สั่งการ J.A.R.V.I.S...."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("กำลังประมวลผล..."):
                try:
                    client = genai.Client(api_key=api_key)
                    res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=user_input,
                        config=types.GenerateContentConfig(
                            system_instruction="You are J.A.R.V.I.S., a witty and elite AI assistant. Always respond concisely in Thai.",
                            temperature=0.6,
                        )
                    )
                    reply = res.text
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {e}")
