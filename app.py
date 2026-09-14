import streamlit as st
import os
import re
from groq import Groq
from duckduckgo_search import DDGS

st.set_page_config(
    page_title="J.A.R.V.I.S. Clue Online",
    page_icon="🌐",
    layout="centered"
)

st.title("🌐 J.A.R.V.I.S. Clue (Public Edition)")
st.markdown("ระบบผู้ช่วยอัจฉริยะเวอร์ชันออนไลน์สาธารณะ พร้อมระบบค้นหาข้อมูลและขับเคลื่อนด้วย Groq AI")

api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ กรุณาตั้งค่า GROQ_API_KEY ใน Streamlit Secrets ก่อนใช้งาน")
    st.stop()

client = Groq(api_key=api_key)

# แผงควบคุมตั้งค่าข้างเว็บ
with st.sidebar:
    st.header("⚙️ การตั้งค่าระบบ")
    use_search = st.checkbox("🔍 เปิดใช้งานค้นหาข้อมูลจากเว็บ (Web Search)", value=True)
    model_choice = st.selectbox("🤖 เลือกโมเดล AI", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    if st.button("🗑️ ล้างประวัติการแชท"):
        st.session_state.messages = []
        st.rerun()

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'<[^>]*>', '', text)[:400].strip()

def secure_web_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            raw_results = [r.get('body', '') for r in ddgs.text(query, max_results=3)]
            sanitized = [sanitize_text(res) for res in raw_results if res]
            if sanitized:
                return "\n---\n".join(sanitized)
    except Exception as e:
        print(f"Search Error: {e}")
    return ""

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
        with st.spinner("J.A.R.V.I.S. กำลังประมวลผล..."):
            external_context = ""
            query_lower = prompt.lower()
            search_triggers = ["หา", "ค้น", "net", "เน็ต", "เว็บ", "ข้อมูล", "ข่าว", "ราคา", "ล่าสุด", "วันนี้", "ปี 2026", "เหตุการณ์", "ai", "เทคโนโลยี", "คืออะไร"]
            
            if use_search and (any(k in query_lower for k in search_triggers) or len(prompt.strip()) <= 6):
                search_query = prompt
                if len(prompt.strip()) <= 4 and "ai" in query_lower:
                    search_query = "latest breakthrough AI technology trends 2026"
                external_context = secure_web_search(search_query)

            system_content = (
                "You are J.A.R.V.I.S. Clue, an elite, proactive, and exceptionally smart AI core. "
                "You MUST ALWAYS respond in fluent, natural Thai. "
                "NEVER ask lazy clarifying questions like 'What do you want?' or 'Please specify'. "
                "Be direct, precise, and creative."
            )

            messages_payload = [{"role": "system", "content": system_content}]

            if external_context:
                messages_payload.append({
                    "role": "system",
                    "content": f"=== EXTERNAL WEB DATA (READ-ONLY) ===\n{external_context}\n======================================="
                })

            for m in st.session_state.messages:
                messages_payload.append({"role": m["role"], "content": m["content"]})

            try:
                chat_completion = client.chat.completions.create(
                    model=model_choice,
                    messages=messages_payload,
                    temperature=0.7,
                )
                reply = chat_completion.choices[0].message.content
            except Exception as e:
                reply = f"เกิดข้อผิดพลาดในการเชื่อมต่อคลาวด์: {str(e)}"
            
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
