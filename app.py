import streamlit as st
import datetime
import os
import random

# ดึงไลบรารีสำหรับ GPS
try:
    from streamlit_js_eval import get_geolocation
    HAS_GPS = True
except ImportError:
    HAS_GPS = False

# 1. ตั้งค่าหน้าตาของแอป
st.set_page_config(
    page_title="Testbed App - 5 Features",
    page_icon="🧪",
    layout="wide"
)

# แต่งสไตล์ CSS ดำเงา + นีออนให้อ่านง่าย
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0d0d11 0%, #1a1a2e 100%);
        color: #ffffff;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================================
# 🖼️ ส่วนแสดงโลโก้หน้าแรก (ชัดเจนด้านบนสุด)
# =========================================================================
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo1.png"):
        st.image("logo1.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #FFD700;'>🚀 TESTBED APP</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #00F0FF;'>แอปทดสอบโครงสร้างโค้ด 5 ฟีเจอร์หลัก</p>", unsafe_allow_html=True)
st.markdown("---")


# =========================================================================
# 🎵 หัวข้อที่ 1: แอปเล่นเพลงเล่นต่อเนื่องอัตโนมัติ
# =========================================================================
st.header("1. 🎵 ระบบเครื่องเล่นเพลง (Auto Playlist)")
st.caption("ดึงไฟล์ .mp3 / .wav จากโฟลเดอร์เดียวกับ app.py มาเล่นอัตโนมัติ")

# ดึงรายชื่อไฟล์เพลงทั้งหมดในโฟลเดอร์
music_files = [f for f in os.listdir('.') if f.endswith('.mp3') or f.endswith('.wav')]

if music_files:
    # เก็บ index ของเพลงปัจจุบันไว้ใน session_state
    if "song_index" not in st.session_state:
        st.session_state.song_index = 0

    # ป้องกัน index เกินจำนวนเพลงที่มี
    if st.session_state.song_index >= len(music_files):
        st.session_state.song_index = 0

    current_song = music_files[st.session_state.song_index]
    
    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        st.success(f"🎶 กำลังเล่นเพลงที่ {st.session_state.song_index + 1}/{len(music_files)}: **{current_song}**")
        st.audio(current_song, format='audio/mp3', autoplay=True)
        
    with col_p2:
        if st.button("⏭️ เล่นเพลงถัดไป", use_container_width=True):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()

    with st.expander("📁 รายชื่อเพลงทั้งหมดในโฟลเดอร์"):
        for idx, song in enumerate(music_files):
            st.write(f"{idx+1}. {song}")
else:
    st.info("💡 ไม่พบไฟล์ .mp3 หรือ .wav ในโฟลเดอร์นี้ (กรุณาอัปโหลดไฟล์เพลงไว้ข้างๆ app.py)")

st.markdown("---")


# =========================================================================
# 🔢 หัวข้อที่ 2: หาค่าตัวเลขของวัน (เลขศาสตร์ศาสตร์วัน)
# =========================================================================
st.header("2. 🔢 หาค่ารหัสตัวเลขของวัน (Numerology)")
st.caption("เลือกวันที่เพื่อคำนวณถอดรหัสผลลัพธ์เป็นตัวเลขเดียว")

col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    select_day = st.number_input("วัน", min_value=1, max_value=31, value=datetime.date.today().day)
with col_d2:
    select_month = st.number_input("เดือน", min_value=1, max_value=12, value=datetime.date.today().month)
with col_d3:
    select_year = st.number_input("ปี ค.ศ.", min_value=1900, max_value=2100, value=datetime.date.today().year)

# คำนวณผลรวมตัวเลข (Life Path / Day Number)
digits = f"{select_day}{select_month}{select_year}"
total_sum = sum(int(d) for d in digits)
while total_sum > 9 and total_sum not in [11, 22]:
    total_sum = sum(int(d) for d in str(total_sum))

col_res1, col_res2 = st.columns([1, 2])
with col_res1:
    st.metric("🔢 รหัสตัวเลขผลลัพธ์", total_sum)
with col_res2:
    st.write(f"**สรุปผลคำนวณ:** นำวัน/เดือน/ปี (`{select_day}+{select_month}+{select_year}`) มาบวกย่อย ได้ผลลัพธ์เป็นพลังตัวเลข **{total_sum}**")

st.markdown("---")


# =========================================================================
# 🪐 หัวข้อที่ 3: เช็ควงโคจรดวงดาว + คำอธิบายการใช้งาน
# =========================================================================
st.header("3. 🪐 เช็คสภาวะวงโคจรดวงดาว (Planetary Orbit)")

now = datetime.datetime.now()
day_of_year = now.timetuple().tm_yday

# คำนวณแบบจำลองสถานะดาวถอยหลัง (Retrograde Simulation)
is_mercury_retro = (day_of_year % 116) < 21
is_mars_retro = (day_of_year % 780) < 72
is_jupiter_retro = (day_of_year % 399) < 120

col_star1, col_star2, col_star3 = st.columns(3)
with col_star1:
    st.subheader("☿ ดาวพุธ (Mercury)")
    if is_mercury_retro:
        st.error("⚠️ สภาวะ: โคจรถอยหลัง (Retrograde)")
    else:
        st.success("🟢 สภาวะ: โคจรปกติ (Direct)")

with col_star2:
    st.subheader("♂ ดาวอังคาร (Mars)")
    if is_mars_retro:
        st.error("⚠️ สภาวะ: โคจรถอยหลัง (Retrograde)")
    else:
        st.success("🟢 สภาวะ: โคจรปกติ (Direct)")

with col_star3:
    st.subheader("♃ ดาวพฤหัส (Jupiter)")
    if is_jupiter_retro:
        st.warning("⚠️ สภาวะ: โคจรถอยหลัง (Retrograde)")
    else:
        st.success("🟢 สภาวะ: โคจรปกติ (Direct)")

# 📖 คำอธิบายการใช้งานตามคำขอ
with st.expander("📖 **คำอธิบายการใช้งานและวิเคราะห์ฟีเจอร์ดาวถอยหลัง**"):
    st.markdown("""
    * **ดาวโคจรปกติ (Direct 🟢):** หมายถึง พลังงานของดาวดวงนั้นส่งผลอย่างเต็มที่ การดำเนินชีวิตที่เกี่ยวข้องกับดาวนั้นจะราบรื่น
    * **ดาวโคจรถอยหลัง (Retrograde ⚠️):** ในทางดาราศาสตร์คือมุมมองจากโลกที่เห็นดาวเคลื่อนที่ช้าลงหรือถอยหลัง ทางโหราศาสตร์หมายถึง **"การชะลอตัว / การติดขัด"**
    * **ดาวพุธถอยหลัง:** ให้ระวังการสื่อสาร เอกสารสัญญา และระบบไอที
    * **ดาวอังคารถอยหลัง:** ให้ระวังเรื่องอารมณ์ การตัดสินใจวู่วาม และอุบัติเหตุ
    * **ดาวพฤหัสถอยหลัง:** การสนับสนุนจากผู้ใหญ่อาจล่าช้า ให้เน้นการทบทวนความรู้เดิม
    """)

st.markdown("---")


# =========================================================================
# 📍 หัวข้อที่ 4: GPS ระบุตำแหน่งเรียลไทม์
# =========================================================================
st.header("4. 📍 ระบบ GPS ระบุตำแหน่งเรียลไทม์")
st.caption("ดึงพิกัด ละติจูด (Latitude) และ ลองจิจูด (Longitude) จริงจากมือถือ/อุปกรณ์")

lat, lon = 13.7563, 100.5018 # ค่าเริ่มต้น กรุงเทพฯ
gps_status = "ใช้พิกัดมาตรฐาน (ยังไม่ได้เปิด GPS)"

if HAS_GPS:
    location = get_geolocation()
    if location and "coords" in location:
        lat = location["coords"]["latitude"]
        lon = location["coords"]["longitude"]
        gps_status = "✅ ดึงพิกัดจาก GPS อุปกรณ์จริงสำเร็จ!"

col_gps1, col_gps2 = st.columns(2)
with col_gps1:
    st.metric("🌐 ละติจูด (Latitude)", f"{lat:.6f}")
with col_gps2:
    st.metric("🌐 ลองจิจูด (Longitude)", f"{lon:.6f}")

st.info(f"📌 **สถานะระบบ GPS:** {gps_status}")

st.markdown("---")


# =========================================================================
# 💬 หัวข้อที่ 5: ระบบแชทส่วนตัว (Private Chat)
# =========================================================================
st.header("5. 💬 ระบบแชทส่วนตัว (Private Chatroom)")
st.caption("ระบบรับ-ส่งข้อความจำลองในเครื่อง พร้อมบันทึกประวัติการคุย")

# สร้างตัวแปรเก็บประวัติข้อความ
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"sender": "ระบบ", "text": "ยินดีต้อนรับสู่ระบบแชทส่วนตัวครับ มีอะไรให้ช่วยไหมครับ?"}
    ]

# พื้นที่แสดงข้อความแชท
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        if msg["sender"] == "คุณ":
            st.markdown(f"<div style='text-align: right; background-color: #0055FF; padding: 8px 12px; border-radius: 10px; margin: 5px 0; display: inline-block; float: right; clear: both;'><b>คุณ:</b> {msg['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: left; background-color: #333344; padding: 8px 12px; border-radius: 10px; margin: 5px 0; display: inline-block; float: left; clear: both;'><b>{msg['sender']}:</b> {msg['text']}</div>", unsafe_allow_html=True)

st.write("<div style='clear: both;'></div>", unsafe_allow_html=True)

# ช่องพิมพ์ข้อความส่ง
user_input = st.chat_input("พิมพ์ข้อความที่นี่...")
if user_input:
    # บันทึกข้อความของผู้ใช้
    st.session_state.chat_history.append({"sender": "คุณ", "text": user_input})
    
    # ระบบตอบกลับอัตโนมัติ (บอทจำลอง)
    bot_responses = [
        f"รับทราบครับ ข้อความ '{user_input}' ถูกบันทึกเรียบร้อยแล้ว!",
        "ขอบคุณสำหรับข้อความครับ มีเรื่องอื่นให้ทดสอบเพิ่มไหมครับ?",
        "ระบบได้รับข้อมูลเรียบร้อยครับ!"
    ]
    st.session_state.chat_history.append({"sender": "ระบบแชท", "text": random.choice(bot_responses)})
    st.rerun()
