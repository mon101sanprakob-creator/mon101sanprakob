import streamlit as st
import datetime
import calendar
import os

# 1. ตั้งค่าหน้าเพจ (มีแค่จุดเดียวบรรทัดแรกสุด)
st.set_page_config(
    page_title="Astrology & Multi-Feature App", 
    page_icon="🔮", 
    layout="centered"
)

# 2. ปรับแต่ง CSS โทนสี ดำเงา (Glossy Dark) + นีออน (แดง, น้ำเงิน, เขียว, ม่วง, ขาว, ทอง)
st.markdown("""
    <style>
    /* พื้นหลังหลักดำเงา Glossy Dark */
    .stApp {
        background: linear-gradient(135deg, #0d0d11 0%, #050508 50%, #150a21 100%);
        color: #ffffff;
    }
    
    /* กล่องการ์ดมีเงา Glossy Glassmorphism */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(20, 20, 30, 0.6);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 215, 0, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* หัวข้อสีทองนีออน (Neon Gold) */
    h1 {
        color: #FFD700 !important;
        text-shadow: 0 0 10px #FFD700, 0 0 20px #FF8C00;
        text-align: center;
    }
    
    h2, h3 {
        color: #00F0FF !important;
        text-shadow: 0 0 8px #00F0FF;
    }

    /* ปุ่มกดสีม่วง-แดง นีออน */
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

    /* ตารางและ Metric */
    div[data-testid="stMetricValue"] {
        color: #00FF66 !important;
        text-shadow: 0 0 10px #00FF66;
    }
    
    .stAlert {
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 255, 102, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- 3. ระบบจัดการสถานะหน้า (Session State) ----------------- #
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# แสดงปุ่มกลับหน้าหลักใน Sidebar เมื่ออยู่นอกหน้าแรก
if st.session_state.current_page != "home":
    if st.sidebar.button("🏠 กลับสู่หน้าแรก (Main Menu)", use_container_width=True):
        st.session_state.current_page = "home"
        st.rerun()

# =========================================================================
# 🏠 1. หน้าแรก (HOME / LANDING PAGE)
# =========================================================================
if st.session_state.current_page == "home":
    
    # แสดงโลโก้หน้าแรก
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            st.info("💡 (ใส่ไฟล์ logo1.png ในโฟลเดอร์เพื่อแสดงโลโก้)")

    st.title("🌟 ศูนย์รวมฟีเจอร์ถอดรหัส & ความสามารถพิเศษ")
    st.write("<p style='text-align: center; color: #E0E0E0;'>กรุณาเลือกหัวข้อ/ฟีเจอร์ที่คุณต้องการใช้งานด้านล่างนี้ได้เลยครับ</p>", unsafe_allow_html=True)
    st.markdown("---")

    # ปุ่มเลือกหัวข้อฟีเจอร์ต่างๆ
    st.subheader("📌 เมนูความสามารถทั้งหมด:")
    
    col_m1, col_m2 = st.columns(2)
    
    with col_m1:
        if st.button("🔮 1. ถอดรหัสดวงชะตา & เพลง", use_container_width=True):
            st.session_state.current_page = "page_astro"
            st.rerun()
            
        if st.button("📊 2. ความสามารถที่สอง (ใหม่)", use_container_width=True):
            st.session_state.current_page = "page_feature_2"
            st.rerun()

    with col_m2:
        if st.button("🎴 3. ความสามารถที่สาม (ใหม่)", use_container_width=True):
            st.session_state.current_page = "page_feature_3"
            st.rerun()
            
        if st.button("⚙️ 4. ติดต่อ / เกี่ยวกับแอป", use_container_width=True):
            st.session_state.current_page = "page_about"
            st.rerun()

# =========================================================================
# 🔮 2. หน้าฟีเจอร์ที่ 1: ถอดรหัสดวงชะตา & เครื่องเล่นเพลง (โค้ดเดิม)
# =========================================================================
elif st.session_state.current_page == "page_astro":
    
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)

    st.title("🔮 ถอดรหัสดวงชะตา & เครื่องเล่นเพลง")
    
    # ----------------- เครื่องเล่นเพลง ----------------- #
    st.subheader("🎵 เครื่องเล่นเพลงบรรยากาศ (Music Player)")
    music_files = [f for f in os.listdir('.') if f.endswith('.mp3') or f.endswith('.wav')]

    if music_files:
        selected_song = st.selectbox("🎧 เลือกเพลงที่จะเปิดฟัง:", music_files)
        if selected_song:
            audio_file = open(selected_song, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
    else:
        st.caption("📁 ไม่พบไฟล์เพลง (.mp3 / .wav) ในโฟลเดอร์นี้")

    st.markdown("---")

    # ----------------- รับอินพุตวันเดือนปี ----------------- #
    st.subheader("🗓️ เลือกวัน/เดือน/ปี เพื่อถอดรหัส")
    col1, col2, col3 = st.columns(3)
    with col1:
        day = st.number_input("วัน (Day)", min_value=1, max_value=31, value=datetime.date.today().day)
    with col2:
        month = st.number_input("เดือน (Month)", min_value=1, max_value=12, value=datetime.date.today().month)
    with col3:
        year = st.number_input("ปี ค.ศ. (Year)", min_value=1900, max_value=2100, value=datetime.date.today().year)

    # ----------------- ฟังก์ชันคำนวณและโหราศาสตร์ ----------------- #
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

    # ----------------- ปุ่มเริ่มคำนวณ ----------------- #
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
# 📊 3. หน้าฟีเจอร์ที่ 2 (พื้นที่สำหรับโค้ดความสามารถใหม่)
# =========================================================================
elif st.session_state.current_page == "page_feature_2":
    st.title("📊 หัวข้อความสามารถที่ 2")
    st.write("พื้นที่สำหรับใส่โค้ดฟังก์ชันใหม่ๆ ของคุณในอนาคตครับ")

# =========================================================================
# 🎴 4. หน้าฟีเจอร์ที่ 3 (พื้นที่สำหรับโค้ดความสามารถใหม่)
# =========================================================================
elif st.session_state.current_page == "page_feature_3":
    st.title("🎴 หัวข้อความสามารถที่ 3")
    st.write("พื้นที่สำหรับใส่โค้ดฟังก์ชันใหม่ๆ ของคุณในอนาคตครับ")

# =========================================================================
# ⚙️ 5. หน้าติดต่อ / เกี่ยวกับแอป
# =========================================================================
elif st.session_state.current_page == "page_about":
    st.title("⚙️ เกี่ยวกับแอปพลิเคชัน")
    st.write("แอปพลิเคชันนี้ถูกพัฒนาขึ้นเพื่อวิเคราะห์ตัวเลข จันทรคติ และผูกดวงชะตาทางโหราศาสตร์")
