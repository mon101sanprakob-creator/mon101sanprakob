import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้าจอ Streamlit ให้กว้างเต็มจอ
st.set_page_config(
    page_title="CyberBeat DJ Studio & Voice AI",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🎧 CyberBeat DJ Studio & AI Music Video")
st.markdown("ระบบมิกซ์เพลง DJ ไฮเทค พร้อมสตูดิโอแปลงเสียงร้องเป็นเพลงและมิวสิกวิดีโอ 4K")

# URL ของแอปพลิเคชันของคุณที่พร้อมรัน
APP_URL = "https://ais-pre-y2bu2bf23olnwut4lytksh-163890626857.asia-southeast1.run.app"

# ฝังหน้าจอ Web App เข้าไปใน Streamlit
components.iframe(APP_URL, height=920, scrolling=True)

st.info("💡 เคล็ดลับ: สามารถกดเปิดเพลง, มิกซ์เสียง DJ, หรืออัดเสียงร้องเพื่อสร้างเพลงในหน้าต่างด้านบนได้ทันที")
