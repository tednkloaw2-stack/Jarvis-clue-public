import streamlit as st
import os
from groq import Groq

st.set_page_config(
    page_title="J.A.R.V.I.S. Clue Online",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 J.A.R.V.I.S. Clue (Public Edition)")
st.markdown("ระบบผู้ช่วยอัจฉริยะเวอร์ชันออนไลน์สาธารณะ เข้าถึงได้ทุกที่ทุกเวลา")

# ดึง API Key จาก Streamlit Secrets ความปลอดภัยสูงสุด
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ กรุณาตั้งค่า GROQ_API_KEY ใน Streamlit Secrets ของระบบก่อนใช้งาน")
    st.stop()

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำสั่งถึง J.A.R.V.I.S. ออนไลน์..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("J.A.R.V.I.S. กำลังประมวลผลบนคลาวด์..."):
            try:
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are J.A.R.V.I.S. Clue, an elite AI assistant. Always respond in fluent, natural Thai. Be proactive and direct."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )
                reply = chat_completion.choices[0].message.content
            except Exception as e:
                reply = f"เกิดข้อผิดพลาดในการเชื่อมต่อคลาวด์: {str(e)}"
            
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})