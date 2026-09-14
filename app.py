import streamlit as st
import re
import streamlit.components.v1 as components
import google.generativeai as genai

st.set_page_config(
    page_title="J.A.R.V.I.S. Clue (Stitch UI Engine)",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 J.A.R.V.I.S. Clue + Stitch UI Engine")
st.markdown("ระบบผู้ช่วยอัจฉริยะที่ผสานพลังดีไซน์แบบ Google Stitch")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ กรุณาใส่ GEMINI_API_KEY ใน Streamlit Secrets ก่อนใช้งาน")
    st.stop()

genai.configure(api_key=api_key)

with st.sidebar:
    st.header("⚙️ ตั้งค่าระบบ")
    model_choice = st.selectbox("🤖 เลือกโมเดล AI", ["gemini-2.0-flash", "gemini-1.5-flash"])
    if st.button("🗑️ ล้างประวัติการแชท"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "html_preview" in message and message["html_preview"]:
            with st.expander("🔍 ดูพรีวิวหน้า UI (Stitch Live Preview)", expanded=True):
                components.html(message["html_preview"], height=400, scrolling=True)

if prompt := st.chat_input("พิมพ์สั่งออกแบบ UI เช่น 'ออกแบบหน้าเว็บ Login สุดล้ำ'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("J.A.R.V.I.S. กำลังคิดและสร้างสรรค์ดีไซน์..."):
            system_content = (
                "You are J.A.R.V.I.S. Clue, powered by Stitch UI engine. "
                "Always respond in fluent, natural Thai. "
                "If the user asks to design a UI, layout, component, or webpage, write complete, modern, and beautiful HTML/CSS inside ```html ... ``` tags so it can be rendered live. "
                "Be proactive, precise, and creative."
            )

            full_prompt = system_content + "\n\n"
            for m in st.session_state.messages:
                role_prefix = "User: " if m["role"] == "user" else "Assistant: "
                full_prompt += f"{role_prefix}{m['content']}\n"

            try:
                current_model = genai.GenerativeModel(model_choice)
                response = current_model.generate_content(full_prompt)
                reply = response.text
            except Exception as e:
                reply = f"เกิดข้อผิดพลาด: {str(e)}"

            html_match = re.search(r'```html\s*(.*?)\s*```', reply, re.DOTALL)
            html_preview_code = html_match.group(1) if html_match else None

            st.markdown(reply)
            if html_preview_code:
                with st.expander("🔍 ดูพรีวิวหน้า UI (Stitch Live Preview)", expanded=True):
                    components.html(html_preview_code, height=400, scrolling=True)

            st.session_state.messages.append({
                "role": "assistant", 
                "content": reply,
                "html_preview": html_preview_code
            })
