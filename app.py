import streamlit as st
import datetime
import calendar
import os
import math

# นำเข้าไลบรารีสำหรับดึง GPS จากอุปกรณ์
try:
    from streamlit_js_eval import get_geolocation
    HAS_GPS_LIB = True
except ImportError:
    HAS_GPS_LIB = False

# 1. ตั้งค่าหน้าเพจ Streamlit
st.set_page_config(
    page_title="Astrology Engine & Cosmic Energy Realtime", 
    page_icon="🔮", 
    layout="wide"
)

# 2. ปรับแต่ง CSS โทนสี ดำเงา (Glossy Dark) + นีออน + ปุ่มลูกศร Sidebar ใหญ่เด่นเรืองแสง
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0d0d11 0%, #050508 50%, #150a21 100%);
        color: #ffffff;
    }
    
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(20, 20, 30, 0.6);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 215, 0, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    h1 {
        color: #FFD700 !important;
        text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00;
        text-align: center;
    }
    
    h2, h3 {
        color: #00F0FF !important;
        text-shadow: 0 0 8px #00F0FF;
    }

    .stButton > button {
        background: linear-gradient(45deg, #FF0055, #7A00FF) !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 0 15px #FF0055, 0 0 20px #7A00FF !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 25px #00FF66, 0 0 30px #00F0FF !important;
    }

    div[data-testid="stMetricValue"] {
        color: #00FF66 !important;
        text-shadow: 0 0 10px #00FF66;
    }
    
    .stAlert {
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 255, 102, 0.3);
    }

    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarExpandButton"] button {
        background: linear-gradient(135deg, #FF0055, #7A00FF) !important;
        border: 2px solid #00F0FF !important;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        box-shadow: 0 0 15px #00F0FF, 0 0 25px #FF0055 !important;
        transition: all 0.3s ease-in-out !important;
    }

    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stSidebarExpandButton"] button svg {
        width: 28px !important;
        height: 28px !important;
        fill: #FFD700 !important;
        filter: drop-shadow(0 0 5px #FFD700) !important;
    }

    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="stSidebarExpandButton"] button:hover {
        transform: scale(1.15) !important;
        background: linear-gradient(135deg, #00FF66, #00F0FF) !important;
        border-color: #FFD700 !important;
        box-shadow: 0 0 25px #00FF66, 0 0 35px #00F0FF !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. จัดการสถานะเปลี่ยนหน้า
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if st.session_state.current_page != "home":
    if st.sidebar.button("🏠 กลับสู่หน้าแรก (Main Menu)", use_container_width=True):
        st.session_state.current_page = "home"
        st.rerun()

# =========================================================================
# 🏠 1. หน้าแรก (HOME)
# =========================================================================
if st.session_state.current_page == "home":
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)

    st.title("🌟 ศูนย์รวมฟีเจอร์ถอดรหัส & พลังงานดวงดาว")
    st.write("<p style='text-align: center; color: #E0E0E0;'>เลือกเมนูความสามารถที่ต้องการใช้งานได้เลยครับ</p>", unsafe_allow_html=True)
    st.markdown("---")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        if st.button("🔮 1. ถอดรหัสดวงชะตา & เพลง", use_container_width=True):
            st.session_state.current_page = "page_astro"
            st.rerun()
            
    with col_m2:
        if st.button("⚡ 2. วิเคราะห์ดาวถอยหลัง & พลังงานชีวิต GPS เรียลไทม์", use_container_width=True):
            st.session_state.current_page = "page_realtime_energy"
            st.rerun()

# =========================================================================
# 🔮 2. หน้าฟีเจอร์ที่ 1: ถอดรหัสดวงชะตา
# =========================================================================
elif st.session_state.current_page == "page_astro":
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)

    st.title("🔮 ถอดรหัสดวงชะตา & เครื่องเล่นเพลง")
    
    st.subheader("🎵 เครื่องเล่นเพลงบรรยากาศ (Music Player)")
    music_files = [f for f in os.listdir('.') if f.endswith('.mp3') or f.endswith('.wav')]

    if music_files:
        selected_song = st.selectbox("🎧 เลือกเพลงที่จะเปิดฟัง:", music_files)
        if selected_song:
            with open(selected_song, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
    else:
        st.caption("📁 ไม่พบไฟล์เพลง (.mp3 / .wav) ในโฟลเดอร์นี้")

    st.markdown("---")

    st.subheader("🗓️ เลือกวัน/เดือน/ปี เพื่อถอดรหัส")
    col1, col2, col3 = st.columns(3)
    with col1:
        day = st.number_input("วัน (Day)", min_value=1, max_value=31, value=datetime.date.today().day)
    with col2:
        month = st.number_input("เดือน (Month)", min_value=1, max_value=12, value=datetime.date.today().month)
    with col3:
        year = st.number_input("ปี ค.ศ. (Year)", min_value=1900, max_value=2100, value=datetime.date.today().year)

    ZODIAC_NAMES = [
        "ราศีเมษ ♈", "ราศีพฤษภ ♉", "ราศีเมถุน ♊", "ราศีกรกฎ ♋",
        "ราศีสิงห์ ♌", "ราศีกันย์ ♍", "ราศีตุลย์ ♎", "ราศีพิจิก ♏", 
        "ราศีธนู ♐", "ราศีมังกร ♑", "ราศีกุมภ์ ♒", "ราศีมีน ♓"
    ]

    zodiac_index = (day + month) % 12
    st.info(f"✨ ราศีคำนวณพื้นฐานของคุณ: **{ZODIAC_NAMES[zodiac_index]}**")

    # ปฏิทินแสดงผล
    st.markdown("### 📅 ปฏิทินดวงชะตาประจำเดือน")
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    st.write(f"#### เดือน: {month_name} {year}")
    
    days_header = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    cols = st.columns(7)
    for idx, day_name in enumerate(days_header):
        cols[idx].write(f"**{day_name}**")
        
    for week in cal:
        cols = st.columns(7)
        for idx, d in enumerate(week):
            if d == 0:
                cols[idx].write(" ")
            elif d == day:
                cols[idx].markdown(f"**[ {d} ]** 🌟")
            else:
                cols[idx].write(str(d))

# =========================================================================
# ⚡ 3. หน้าฟีเจอร์ที่ 2: วิเคราะห์ดาวถอยหลัง & พลังงานชีวิต GPS เรียลไทม์
# =========================================================================
elif st.session_state.current_page == "page_realtime_energy":
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)

    st.title("⚡ วิเคราะห์ดาวถอยหลัง & พลังงานชีวิต GPS เรียลไทม์")
    st.caption("คำนวณค่าสนามพลังงานตามเวลาจริง พิกัดทางภูมิศาสตร์ และวันเดือนปีเกิดของผู้ใช้งาน")

    st.markdown("---")
    
    # ฟีเจอร์: ให้ผู้ใช้งานระบุวัน/เดือน/ปีเกิด
    st.subheader("👤 ข้อมูลส่วนบุคคล (สำหรับคำนวณพลังงานเจาะจงบุคคล)")
    use_user_dob = st.checkbox("📌 ต้องการระบุวัน/เดือน/ปีเกิด เพื่อประมวลผลดวงชะตาเฉพาะบุคคล", value=True)
    
    user_bday, user_bmonth, user_byear = 1, 1, 1995
    if use_user_dob:
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            user_bday = st.number_input("วันเกิด", min_value=1, max_value=31, value=15)
        with col_b2:
            user_bmonth = st.number_input("เดือนเกิด", min_value=1, max_value=12, value=6)
        with col_b3:
            user_byear = st.number_input("ปี ค.ศ. เกิด", min_value=1900, max_value=2100, value=1995)
        
        # คำนวณเลขศาสตร์ชะตาชีวิตพื้นฐาน (Life Path Number)
        dob_sum = sum([int(digit) for digit in f"{user_bday}{user_bmonth}{user_byear}"])
        while dob_sum > 9:
            dob_sum = sum([int(digit) for digit in str(dob_sum)])
        st.success(f"🧬 รหัสพลังงานชะตาชีวิตประจำตัวคุณ (Life Path Energy): **ระดับ {dob_sum}**")
    else:
        st.info("ℹ️ โหมดคำนวณพลังงานสากลรวม (คำนวณจากพิกัดสถานที่และเวลาปัจจุบันเท่านั้น)")
        dob_sum = 5 # ค่ามาตรฐานกลาง

    st.markdown("---")

    # 1. แสดงพิกัด GPS เรียลไทม์
    st.subheader("📍 ดึงพิกัด GPS ปัจจุบันของคุณ")
    lat, lon = 13.7563, 100.5018 # ค่าเริ่มต้น: กรุงเทพฯ
    location_source = "พิกัดเริ่มต้น (Bangkok)"

    if HAS_GPS_LIB:
        loc = get_geolocation()
        if loc and "coords" in loc:
            lat = loc["coords"]["latitude"]
            lon = loc["coords"]["longitude"]
            location_source = "ดึงจาก GPS อุปกรณ์ของคุณเรียลไทม์"
            st.success(f"✅ ดึงตำแหน่งสำเร็จ: ละติจูด {lat:.4f}, ลองจิจูด {lon:.4f} ({location_source})")
        else:
            st.info("📡 กำลังรอรับค่าพิกัด GPS จากเบราว์เซอร์... (หากปฏิเสธระบบจะใช้พิกัดมาตรฐาน)")
    else:
        st.warning("⚠️ ไม่พบไลบรารี `streamlit-js-eval` ใช้พิกัดมาตรฐาน กรุงเทพมหานคร")

    now = datetime.datetime.now()

    # 2. สถานะดาวถอยหลัง (Retrograde Simulation)
    st.markdown("### 🪐 สถานะการโคจรของดาวเคราะห์ (Retrograde Monitor)")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    mercury_retro = (now.day % 3 == 0)
    mars_retro = (now.day % 5 == 0)
    jupiter_retro = (now.month % 2 == 0)

    with col_p1:
        st.metric("ดาวพุธ (Mercury)", "วิกฤต/ถอยหลัง ⚠️" if mercury_retro else "ปกติ (Direct) 🟢")
    with col_p2:
        st.metric("ดาวอังคาร (Mars)", "วิกฤต/ถอยหลัง ⚠️" if mars_retro else "ปกติ (Direct) 🟢")
    with col_p3:
        st.metric("ดาวพฤหัส (Jupiter)", "วิกฤต/ถอยหลัง ⚠️" if jupiter_retro else "ปกติ (Direct) 🟢")

    # 3. คำนวณพลังงานชีวิตเรียลไทม์ (ปรับสูตรตามวันเกิด + พิกัด GPS)
    st.markdown("### ⚡ ดัชนีพลังงานชีวิตตามพิกัด GPS & วันเกิดเรียลไทม์")
    
    base_calc = (lat * lon) + now.second + (dob_sum * 10)
    
    work_energy = int((math.sin(base_calc) + 1) * 50)
    money_energy = int((math.cos(base_calc * 0.5) + 1) * 50)
    mind_energy = int((math.sin(base_calc * 0.8) + 1) * 50)
    love_energy = int((math.cos(base_calc * 1.2) + 1) * 50)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💼 การงาน/ภารกิจ", f"{work_energy}%")
    c2.metric("💰 โชคลาภ/การเงิน", f"{money_energy}%")
    c3.metric("🧠 สมาธิ/ความคิด", f"{mind_energy}%")
    c4.metric("💖 ความสัมพันธ์/เสน่ห์", f"{love_energy}%")

    st.write(f"⏱️ *อัปเดตข้อมูลล่าสุดเมื่อ:* `{now.strftime('%Y-%m-%d %H:%M:%S')}`")
    
    if st.button("🔄 อัปเดตพลังงานเรียลไทม์ (Refresh)"):
        st.rerun()
