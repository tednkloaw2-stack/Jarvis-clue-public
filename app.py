import streamlit as st
import re
import streamlit.components.v1 as components
import google.generativeai as genai

st.set_page_config(
    page_title="J.A.R.V.I.S. Clue (Stitch UI Engine)",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ J.A.R.V.I.S. Clue + Stitch UI Engine")
st.markdown("ระบบผู้ช่วยดีไซน์ UI อัจฉริยะ (Ultra-Fast Realtime Stream)")

api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ กรุณาใส่ GEMINI_API_KEY ใน Streamlit Secrets ก่อนใช้งาน")
    st.stop()

genai.configure(api_key=api_key)

with st.sidebar:
    st.header("⚙️ ตั้งค่าความเร็วและโมเดล")
    model_choice = st.selectbox(
        "🤖 เลือกสมอง AI", 
        ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
    )
    if st.button("🗑️ ล้างประวัติการแชท"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงประวัติการสนทนาย้อนหลัง
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("html_preview"):
            with st.expander("🔍 ดูพรีวิวหน้า UI (Stitch Live Preview)", expanded=True):
                components.html(message["html_preview"], height=420, scrolling=True)

if prompt := st.chat_input("พิมพ์สั่งออกแบบ UI ด่วนพิเศษ เช่น 'การ์ดสินค้า 3D Hover Effect'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_content = (
            "You are J.A.R.V.I.S. Clue, an elite UI/UX engineer and code architect. "
            "Write clean, highly aesthetic, modern HTML/CSS directly. "
            "Put all UI code inside a single ```html ... ``` block with embedded CSS in <style>. "
            "Respond concisely in natural Thai."
        )

        # เก็บประวัติเฉพาะรอบล่าสุดเพื่อความเร็วสูงสุด
        recent_messages = st.session_state.messages[-3:]
        chat_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in recent_messages])
        full_prompt = f"{system_content}\n\n{chat_history}"

        try:
            current_model = genai.GenerativeModel(
                model_choice,
                generation_config={"temperature": 0.3} # ปรับให้ออกโค้ดแม่นยำ ไม่เวิ่นเว้อ
            )
            
            # ยิง Streaming ทันที ให้ข้อความวิ่งแบบ Realtime
            response_stream = current_model.generate_content(full_prompt, stream=True)
            
            def stream_generator():
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text

            reply = st.write_stream(stream_generator)

            # ดึงโค้ด HTML มารัน Preview ทันทีที่ข้อความวิ่งจบ
            html_match = re.search(r'```html\s*(.*?)\s*```', reply, re.DOTALL)
            html_preview_code = html_match.group(1) if html_match else None

            if html_preview_code:
                with st.expander("🔍 ดูพรีวิวหน้า UI (Stitch Live Preview)", expanded=True):
                    components.html(html_preview_code, height=420, scrolling=True)

            st.session_state.messages.append({
                "role": "assistant", 
                "content": reply,
                "html_preview": html_preview_code
            })

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")
