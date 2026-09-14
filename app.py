import os
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"
os.environ["PYTHONIOENCODING"] = "utf-8"

import sys
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

import streamlit as st
import re
import streamlit.components.v1 as components
from groq import Groq
from duckduckgo_search import DDGS

st.set_page_config(
    page_title="J.A.R.V.I.S. Clue (Stitch UI Engine)",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 J.A.R.V.I.S. Clue + Stitch UI Engine")
st.markdown("ระบบผู้ช่วยอัจฉริยะที่ผสานพลังดีไซน์แบบ Google Stitch: ออกแบบหน้า UI, เขียนโค้ด และพรีวิวผลลัพธ์แบบเรียลไทม์")

raw_api_key = st.secrets.get("GROQ_API_KEY", "")
api_key = str(raw_api_key).strip().encode("ascii", "ignore").decode("ascii")

if not api_key:
    st.error("⚠️ กรุณาตั้งค่า GROQ_API_KEY ใน Streamlit Secrets ก่อนใช้งาน")
    st.stop()

client = Groq(api_key=api_key)

with st.sidebar:
    st.header("⚙️ แผงควบคุม Stitch Engine")
    use_search = st.checkbox("🔍 เปิดใช้งานค้นหาข้อมูลเว็บ", value=True)
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
    except Exception:
        pass
    return ""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "html_preview" in message and message["html_preview"]:
            with st.expander("🔍 ดูพรีวิวหน้า UI (Stitch Live Preview)", expanded=True):
                components.html(message["html_preview"], height=400, scrolling=True)

if prompt := st.chat_input("พิมพ์สั่งออกแบบ UI หรือค้นหาข้อมูล เช่น 'ออกแบบหน้าเว็บ Login สุดล้ำ'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("J.A.R.V.I.S. กำลังประมวลผลและสร้างสรรค์ดีไซน์..."):
            external_context = ""
            query_lower = prompt.lower()
            search_triggers = ["หา", "ค้น", "net", "เน็ต", "เว็บ", "ข้อมูล", "ข่าว", "ราคา", "ล่าสุด", "วันนี้", "ปี 2026", "เหตุการณ์", "ai", "เทคโนโลยี", "คืออะไร"]
            
            if use_search and (any(k in query_lower for k in search_triggers) or len(prompt.strip()) <= 6):
                search_query = prompt
                if len(prompt.strip()) <= 4 and "ai" in query_lower:
                    search_query = "latest breakthrough AI technology trends 2026"
                external_context = secure_web_search(search_query)

            system_content = (
                "You are J.A.R.V.I.S. Clue, powered by Stitch UI engine. "
                "Always respond in fluent, natural Thai. "
                "If the user asks to design a UI, layout, component, or webpage, write complete, modern, and beautiful HTML/CSS inside ```html ... ``` tags so it can be rendered live. "
                "Be proactive, precise, and creative."
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
