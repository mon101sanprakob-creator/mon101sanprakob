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

    st.title("🌟 อยู่นิ้งๆไม่เจ็บตัว.ฟีเจอร์ถอดรหัส & พลังงานดวงดาว")
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

    def get_exact_day_name(target_date):
        day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
        day_powers = [15, 8, 17, 19, 21, 12, 6]
        idx = target_date.weekday()
        return day_names[idx], day_powers[idx]

    def get_zodiac(d, m):
        zodiacs = [
            (1, 20, "มังกร ♑"), (2, 19, "กุมภ์ ♒"), (3, 21, "มีน ♓"),
            (4, 20, "เมษ ♈"), (5, 21, "พฤษภ ♉"), (6, 21, "เมถุน ♊"),
            (7, 23, "กรกฎ ♋"), (8, 23, "สิงห์ ♌"), (9, 23, "กันย์ ♍"),
            (10, 23, "ตุลย์ ♎"), (11, 22, "พิจิก ♏"), (12, 22, "ธนู ♐"),
            (12, 31, "มังกร ♑")
        ]
        for month_end, day_end, name in zodiacs:
            if m < month_end or (m == month_end and d <= day_end):
                return name
        return "มังกร ♑"

    def get_zodiac_animal(y):
        animals = ["วอก (ลิง)", "ระกา (ไก่)", "จอ (หมา)", "กุน (หมู)", "ชวด (หนู)", "ฉลู (วัว)",
                   "ขาล (เสือ)", "เถาะ (กระต่าย)", "มะโรง (งูใหญ่)", "มะเส็ง (งูเล็ก)", "มะเมีย (ม้า)", "มะเมีย (แพะ)"]
        return animals[y % 12]

    def get_exact_moon_phase(target_date):
        ref_date = datetime.datetime(1980, 4, 15, 12, 0)
        target_datetime = datetime.datetime(target_date.year, target_date.month, target_date.day, 12, 0)
        diff_days = (target_datetime - ref_date).total_seconds() / 86400.0
        synodic_month = 29.53058867
        cycle_pos = (diff_days % synodic_month)
        age_in_days = int(cycle_pos)
        illumination = int((1 - abs((cycle_pos / synodic_month) - 0.5) * 2) * 100)
        
        if age_in_days < 15:
            kham = age_in_days + 1
            return f"ขึ้น {kham} ค่ำ 🌓 (ดวงจันทร์สว่างประมาณ {illumination}%)"
        else:
            kham = age_in_days - 14
            if kham > 15:
                kham = 15
            return f"แรม {kham} ค่ำ 🌗 (ดวงจันทร์สว่างประมาณ {illumination}%)"

    def calculate_planetary_positions(target_date):
        days_since_2000 = (target_date - datetime.date(2000, 1, 1)).days
        sun_pos = int(((days_since_2000 % 365.25) / 365.25) * 12)
        moon_pos = int(((days_since_2000 % 27.32) / 27.32) * 12)
        mercury_pos = int(((days_since_2000 % 87.97) / 87.97) * 12)
        venus_pos = int(((days_since_2000 % 224.7) / 224.7) * 12)
        mars_pos = int(((days_since_2000 % 686.98) / 686.98) * 12)
        jupiter_pos = int(((days_since_2000 % 4332.59) / 4332.59) * 12)
        saturn_pos = int(((days_since_2000 % 10759.22) / 10759.22) * 12)
        
        elements = ["🔥 ธาตุไฟ", "🌍 ธาตุดิน", "🌬️ ธาตุลม", "💧 ธาตุน้ำ"] * 3
        houses = ["ตนุ (ตัวตน)", "กุมภะ (ทรัพย์สิน)", "สหัชชะ (เพื่อนฝูง)", "พันธุ (ครอบครัว)", 
                  "ปุตตะ (บริวาร/โชค)", "อริ (อุปสรรค)", "ปัตนิ (คู่ครอง)", "มรณะ (การเปลี่ยนแปลง)", 
                  "ศุภะ (ความเจริญ)", "กัมมะ (การงาน)", "ลาภะ (โชคลาภ)", "วินาศ (เรื่องเร้นลับ)"]

        planets = [
            {"ดวงดาว": "☀️ ดาวอาทิตย์ (1)", "สถิตราศี": ZODIAC_NAMES[sun_pos], "ธาตุประจำราศี": elements[sun_pos], "ส่งผลต่อเรื่อง": houses[sun_pos], "อัญมณีเสริมดวง": "ทับทิม / แดง", "คำทำนายเชิงลึก": "ส่งผลต่อวาสนา ความเป็นผู้นำ และศักดิ์ศรีในสังคม"},
            {"ดวงดาว": "🌙 ดาวจันทร์ (2)", "สถิตราศี": ZODIAC_NAMES[moon_pos], "ธาตุประจำราศี": elements[moon_pos], "ส่งผลต่อเรื่อง": houses[moon_pos], "อัญมณีเสริมดวง": "ไข่มุก / ขาว, เหลืองนวล", "คำทำนายเชิงลึก": "ส่งผลต่อจิตใจ เสน่ห์ ความอ่อนโยน และจินตนาการ"},
            {"ดวงดาว": "☿ ดาวพุธ (4)", "สถิตราศี": ZODIAC_NAMES[mercury_pos], "ธาตุประจำราศี": elements[mercury_pos], "ส่งผลต่อเรื่อง": houses[mercury_pos], "อัญมณีเสริมดวง": "มรกต / เขียว", "คำทำนายเชิงลึก": "ส่งผลต่อวาทศิลป์ การเจรจาค้าขาย และสติปัญญา"},
            {"ดวงดาว": "♀ ดาวศุกร์ (6)", "สถิตราศี": ZODIAC_NAMES[venus_pos], "ธาตุประจำราศี": elements[venus_pos], "ส่งผลต่อเรื่อง": houses[venus_pos], "อัญมณีเสริมดวง": "ไพลิน / ฟ้า, น้ำเงิน", "คำทำนายเชิงลึก": "ส่งผลต่อความรัก ศิลปะ ความสุข และโชคด้านการเงิน"},
            {"ดวงดาว": "♂ ดาวอังคาร (3)", "สถิตราศี": ZODIAC_NAMES[mars_pos], "ธาตุประจำราศี": elements[mars_pos], "ส่งผลต่อเรื่อง": houses[mars_pos], "อัญมณีเสริมดวง": "โกเมน / ชมพู, แดงเข้ม", "คำทำนายเชิงลึก": "ส่งผลต่อความกล้าหาญ ขยันอดทน การต่อสู้และกำลังกาย"},
            {"ดวงดาว": "♃ ดาวพฤหัสบดี (5)", "สถิตราศี": ZODIAC_NAMES[jupiter_pos], "ธาตุประจำราศี": elements[jupiter_pos], "ส่งผลต่อเรื่อง": houses[jupiter_pos], "อัญมณีเสริมดวง": "บุษราคัม / ส้ม, ทอง", "คำทำนายเชิงลึก": "ส่งผลต่อผู้ใหญ่เมตตา ความรู้ คุณธรรม และโชคใหญ่"},
            {"ดวงดาว": "♄ ดาวเสาร์ (7)", "สถิตราศี": ZODIAC_NAMES[saturn_pos], "ธาตุประจำราศี": elements[saturn_pos], "ส่งผลต่อเรื่อง": houses[saturn_pos], "อัญมณีเสริมดวง": "นิลดำ / ดำ, ม่วง", "คำทำนายเชิงลึก": "ส่งผลต่อความอุตสาหะ การวางแผนระยะยาว และความมั่นคง"}
        ]
        return planets

    def calculate_life_path(d, m, y):
        digits = f"{d}{m}{y}"
        total = sum(int(digit) for digit in digits)
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(digit) for digit in str(total))
        return total

    if st.button("🚀 ถอดรหัสผูกดวง & คำนวณตำแหน่งดวงดาว"):
        try:
            target_date = datetime.date(year, month, day)
            day_name, day_power = get_exact_day_name(target_date)
            year_th = year + 543
            zodiac = get_zodiac(day, month)
            zodiac_animal = get_zodiac_animal(year)
            moon_phase = get_exact_moon_phase(target_date)
            life_path = calculate_life_path(day, month, year)
            planet_data = calculate_planetary_positions(target_date)

            st.markdown("---")
            st.header(f"✨ แผ่นผูกดวงชะตา: {day} / {month} / {year} (พ.ศ. {year_th})")
            st.subheader(f"🗓️ เจ้าชะตากำเนิด: **วัน{day_name}** | ปี{zodiac_animal}")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("ราศีประจำตัว", zodiac)
            with c2:
                st.metric("เลขกำลังวัน", day_power)
            with c3:
                st.metric("เลขชะตาลิขิต", life_path)

            st.info(f"🌙 **สภาวะดวงจันทร์ (ข้างขึ้น/ข้างแรม):** {moon_phase}")

            st.markdown("---")
            st.subheader("🪐 ตารางตำแหน่งดวงดาวประทับราศี & มิติความหมาย")
            st.dataframe(planet_data, use_container_width=True)

            st.markdown("---")
            st.subheader("🎯 ค้นหาวันที่มีโครงสร้างดวงชะตาตรงกันเป๊ะ (ย้อนหลัง 50 ปี - ล่วงหน้า 50 ปี)")
            
            start_year = year - 50
            end_year = year + 50
            matching_dates = []
            
            for y in range(start_year, end_year + 1):
                if y == year:
                    continue
                try:
                    check_date = datetime.date(y, month, day)
                    if check_date.weekday() == target_date.weekday():
                        diff_years = y - year
                        status = f"ล่วงหน้า +{diff_years} ปี" if diff_years > 0 else f"ย้อนหลัง {diff_years} ปี"
                        matching_dates.append({
                            "ปี ค.ศ.": y,
                            "ปี พ.ศ.": y + 543,
                            "วันที่ตรงกัน": check_date.strftime("%d/%m/%Y"),
                            "ปีนักษัตร": get_zodiac_animal(y),
                            "ระยะเวลา": status,
                            "เลขกำลังวัน": day_power
                        })
                except ValueError:
                    continue
                    
            st.write(f"พบวันที่มีค่าคุณสมบัติปฏิทินและพลังดาวตรงกันทั้งหมด **{len(matching_dates)} วัน** ในรอบ 100 ปี:")
            st.dataframe(matching_dates, use_container_width=True)

        except ValueError:
            st.error("❌ วันที่ที่คุณกรอกไม่ถูกต้อง กรุณาตรวจสอบวันที่ใหม่อีกครั้งครับ")

# =========================================================================
# ⚡ 3. หน้าฟีเจอร์ที่ 2: ระบบวิเคราะห์ดาวถอยหลัง & GPS พิกัดเวลาท้องถิ่นจริง
# =========================================================================
elif st.session_state.current_page == "page_realtime_energy":
    st.title("⚡ วิเคราะห์สภาวะดาวถอยหลัง & GPS พิกัดเวลาท้องถิ่นเรียลไทม์")
    st.write("ระบบคำนวณตำแหน่งพิกัด GPS อัตโนมัติจากอุปกรณ์ของคุณ เพื่อความแม่นยำทางดาราศาสตร์รายบุคคล")
    
    st.markdown("---")
    
    # 📌 1. ระบบดึง GPS จากโทรศัพท์/คอมพิวเตอร์
    st.subheader("📍 พิกัดตำแหน่ง GPS ปัจจุบันของคุณ")
    
    default_lat, default_lon = 13.7563, 100.5018  # ค่าเริ่มต้น กทม.
    
    if HAS_GPS_LIB:
        location = get_geolocation()
        if location and "coords" in location:
            default_lat = location["coords"]["latitude"]
            default_lon = location["coords"]["longitude"]
            st.success("✅ ดึงพิกัด GPS จากอุปกรณ์ของคุณสำเร็จแล้ว!")
        else:
            st.info("💡 กดยินยอมเปิด Location บนเบราว์เซอร์เพื่อดึงตำแหน่ง GPS จริง หรือเลือกลิสต์ด้านล่างได้ครับ")
    else:
        st.warning("⚠️ กรุณาใส่ `streamlit-js-eval` ในไฟล์ requirements.txt เพื่อเปิดใช้งานระบบดึง GPS อัตโนมัติ")

    col_gps1, col_gps2, col_gps3 = st.columns([2, 2, 2])
    with col_gps1:
        province_preset = st.selectbox(
            "🏙️ เลือกจังหวัด (หากไม่เปิด GPS):",
            ["📍 ใช้ค่าจาก GPS อุปกรณ์", "กรุงเทพมหานคร (Bangkok)", "เชียงใหม่ (Chiang Mai)", "ภูเก็ต (Phuket)", "ขอนแก่น (Khon Kaen)", "ชลบุรี (Chonburi)"]
        )
    
    if province_preset == "เชียงใหม่ (Chiang Mai)":
        default_lat, default_lon = 18.7883, 98.9853
    elif province_preset == "ภูเก็ต (Phuket)":
        default_lat, default_lon = 7.8804, 98.3923
    elif province_preset == "ขอนแก่น (Khon Kaen)":
        default_lat, default_lon = 16.4419, 102.8360
    elif province_preset == "ชลบุรี (Chonburi)":
        default_lat, default_lon = 13.3611, 100.9847
    elif province_preset == "กรุงเทพมหานคร (Bangkok)":
        default_lat, default_lon = 13.7563, 100.5018

    with col_gps2:
        lat = st.number_input("🌐 ละติจูด (Latitude):", value=float(default_lat), format="%.4f")
    with col_gps3:
        lon = st.number_input("🌐 ลองจิจูด (Longitude):", value=float(default_lon), format="%.4f")

    # เวลาประเทศไทย (GMT+7)
    utc_now = datetime.datetime.utcnow()
    th_now = utc_now + datetime.timedelta(hours=7)

    # คำนวณ Local Mean Time (LMT) จากลองจิจูดจริง (1° = 4 นาที)
    lon_offset_minutes = (lon - 105.0) * 4
    lmt_now = th_now + datetime.timedelta(minutes=lon_offset_minutes)

    st.markdown("---")
    st.subheader("⏱️ รายงานเวลาเรียลไทม์เปรียบเทียบเชิงพิกัด")
    c_t1, c_t2, c_t3 = st.columns(3)
    with c_t1:
        st.metric("🇹🇭 เวลามาตรฐานไทย (GMT+7)", th_now.strftime("%H:%M:%S น."))
    with c_t2:
        st.metric("🧭 เวลาท้องถิ่นจริงตาม GPS (LMT)", lmt_now.strftime("%H:%M:%S น."))
    with c_t3:
        st.metric("📍 พิกัดอ้างอิง GPS", f"{lat:.4f}°N, {lon:.4f}°E")

    st.markdown("---")

    # 🔮 2. คำนวณสถานะดาวถอยหลัง (Retrograde Status)
    day_of_year = th_now.timetuple().tm_yday
    
    is_mercury_retro = (day_of_year % 116) < 21
    is_mars_retro = (day_of_year % 780) < 72
    is_jupiter_retro = (day_of_year % 399) < 120
    is_saturn_retro = (day_of_year % 378) < 140

    st.subheader("🔮 1. รายงานสภาวะดวงดาวโคจรวิปริต (ดาวถอยหลัง - Retrograde Monitor)")
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        if is_mercury_retro:
            st.error("🚨 **ดาวพุธ (☿) กำลังโคจรถอยหลัง (Retrograde):**\n"
                     "⚠️ **ข้อควรระวัง:** ระวังเรื่องเอกสารสัญญาผิดพลาด การสื่อสารเข้าใจผิด ระบบการสื่อสาร/อุปกรณ์ไอทีมีปัญหา ไม่ควรเซ็นสัญญาสัมพันธ์ใหญ่ในช่วงนี้")
        else:
            st.success("✅ **ดาวพุธ (☿) โคจรปกติ (Direct):**\n"
                       "🟢 การเจรจา ค้าขาย สื่อสาร ตกลงสัญญา และระบบไอทีลื่นไหลเป็นปกติ")

        if is_mars_retro:
            st.error("🚨 **ดาวอังคาร (♂) กำลังโคจรถอยหลัง (Retrograde):**\n"
                     "⚠️ **ข้อควรระวัง:** ความอดทนต่ำ อารมณ์ร้อน ระวังอุบัติเหตุ ความขัดแย้ง และการตัดสินใจวู่วาม")
        else:
            st.success("✅ **ดาวอังคาร (♂) โคจรปกติ (Direct):**\n"
                       "🟢 พลังงานขับเคลื่อนสูง มีความกล้าหาญ ขยัน และการตัดสินใจเฉียบขาด")

    with col_r2:
        if is_jupiter_retro:
            st.warning("⚠️ **ดาวพฤหัสบดี (♃) กำลังโคจรถอยหลัง (Retrograde):**\n"
                       "⚠️ **ข้อควรระวัง:** โชคลาภและการสนับสนุนจากผู้ใหญ่ล่าช้า ควรทบทวนความรู้และแผนงานก่อนลุยจริง")
        else:
            st.success("✅ **ดาวพฤหัสบดี (♃) โคจรปกติ (Direct):**\n"
                       "🟢 โชคลาภเด่น ผู้ใหญ่ให้การสนับสนุน ความคิดและปัญญาสว่างไสว")

        if is_saturn_retro:
            st.warning("⚠️ **ดาวเสาร์ (♄) กำลังโคจรถอยหลัง (Retrograde):**\n"
                       "⚠️ **ข้อควรระวัง:** งานโปรเจกต์ใหญ่ล่าช้า เจอแรงกดดันสูง ให้เน้นเคลียร์งานเก่าอย่าเพิ่งขยายงานใหม่")
        else:
            st.success("✅ **ดาวเสาร์ (♄) โคจรปกติ (Direct):**\n"
                       "🟢 รากฐานมั่นคง งานระยะยาวมีความก้าวหน้า ความอุตสาหะส่งผลสำเร็จ")

    st.markdown("---")

    # 📊 3. คำนวณดัชนีพลังงานชีวิต 4 ด้านประจำวันตามพิกัด
    st.subheader("📊 2. ดัชนีพลังงานชีวิตประจำวันอ้างอิงพิกัด GPS (Cosmic Energy Index)")
    
    base_val = (th_now.day * 7 + th_now.month * 13 + th_now.hour + int(lon * 100)) % 40
    
    work_energy = min(98, max(45, 60 + base_val - (15 if is_mars_retro else 0)))
    money_energy = min(98, max(40, 55 + ((base_val * 3) % 35) + (10 if not is_jupiter_retro else -10)))
    brain_energy = min(98, max(35, 50 + ((base_val * 2) % 40) - (20 if is_mercury_retro else 0)))
    love_energy = min(98, max(50, 65 + ((base_val * 5) % 30)))

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("💼 ด้านการงาน & การตัดสินใจ", f"{work_energy}%")
        st.progress(work_energy / 100)
    with m2:
        st.metric("💰 ด้านการเงิน & โชคลาภ", f"{money_energy}%")
        st.progress(money_energy / 100)
    with m3:
        st.metric("🧠 ด้านความคิด & การเจรจา", f"{brain_energy}%")
        st.progress(brain_energy / 100)
    with m4:
        st.metric("❤️ ด้านเสน่ห์ & อารมณ์", f"{love_energy}%")
        st.progress(love_energy / 100)

    st.markdown("---")

    # 🎯 4. คำแนะนำชีวิตประจำวัน
    st.subheader("🎯 3. คำแนะนำในการดำเนินชีวิตประจำวันนี้")
    
    if brain_energy < 50:
        st.info("💡 **กลยุทธ์วันนี้:** การเจรจายังมีอุปสรรค ควรเน้นฟังมากกว่าพูด และตรวจสอบข้อความก่อนส่งทุกครั้ง")
    elif work_energy > 80:
        st.info("💡 **กลยุทธ์วันนี้:** พลังการงานและพลังขับเคลื่อนสูงมาก เหมาะแก่การลุยโปรเจกต์ใหม่และตัดสินใจเรื่องสำคัญ")
    else:
        st.info("💡 **กลยุทธ์วันนี้:** พลังงานอยู่ในระดับสมดุล เหมาะแก่การสะสางงานคงค้างและดูแลความสัมพันธ์กับคนรอบข้าง")

    if st.button("🔄 อัปเดตพิกัด GPS และเวลาปัจจุบัน"):
        st.rerun()
