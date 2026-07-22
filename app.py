import streamlit as st
import datetime
import calendar
import math
import os
import glob
from PIL import Image

# ---------------------------------------------------------
# 1. ตั้งค่าหน้าเว็บ Streamlit (Theme & Page Config)
# ---------------------------------------------------------
st.set_page_config(
    page_title="AstroTime Matrix & Music Player",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS ตกแต่งสไตล์ นีออน - ดำเงา - ทอง - แดง - เขียว - ม่วง
st.markdown("""
<style>
    /* พื้นหลังหลักดำเงา */
    .stApp {
        background-color: #0a0a0c;
        color: #ffffff;
    }
    
    /* กรอบการ์ดพรีเมียม นีออน */
    .neon-card {
        background-color: #141419;
        border: 1px solid #00f3ff;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .neon-card-purple {
        background-color: #141419;
        border: 1px solid #b000ff;
        box-shadow: 0 0 15px rgba(176, 0, 255, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* ตัวอักษรสีสันต่างๆ */
    .gold-text { color: #ffd700; font-weight: bold; }
    .cyan-text { color: #00f3ff; font-weight: bold; }
    .purple-text { color: #b000ff; font-weight: bold; }
    .red-text { color: #ff3366; font-weight: bold; }
    .green-text { color: #00ff66; font-weight: bold; }
    .blue-text { color: #1a73e8; font-weight: bold; }
    
    /* ปรับแต่งปุ่มกด */
    .stButton>button {
        background: linear-gradient(45deg, #ff3366, #b000ff);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px #00f3ff;
        color: #ffd700;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. ฟังก์ชันคำนวณทางดาราศาสตร์ โหราศาสตร์ และปฏิทิน
# ---------------------------------------------------------

DAYS_TH = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
MONTHS_TH = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]
ZODIAC_TH = [
    ("มังกร", (1, 15), (2, 12)),
    ("กุมภ์", (2, 13), (3, 14)),
    ("มีน", (3, 15), (4, 12)),
    ("เมษ", (4, 13), (5, 14)),
    ("พฤษภ", (5, 15), (6, 14)),
    ("เมถุน", (6, 15), (7, 15)),
    ("กรกฎ", (7, 16), (8, 16)),
    ("สิงห์", (8, 17), (9, 16)),
    ("กันย์", (9, 17), (10, 17)),
    ("ตุลย์", (10, 18), (11, 16)),
    ("พิจิก", (11, 17), (12, 15)),
    ("ธนู", (12, 16), (1, 14))
]
ZODIAC_ANIMALS = ["ชวด (หนู)", "ฉลู (วัว)", "ขาล (เสือ)", "เถาะ (กระต่าย)", 
                  "มะโรง (งูใหญ่)", "มะเส็ง (งูเล็ก)", "มะเมีย (ม้า)", "มะแม (แพะ)", 
                  "วอก (ลิง)", "ระกา (ไก่)", "จอ (สุนัข)", "กุน (หมู)"]

LUCKY_COLORS = ["แดงนีออน", "เขียวมรกต", "น้ำเงินไพลิน", "ม่วงอเมทิสต์", "ทองคำ", "ขาวมุก"]

def get_zodiac(day, month):
    for name, start, end in ZODIAC_TH:
        s_m, s_d = start[0], start[1]
        e_m, e_d = end[0], end[1]
        if s_m <= e_m:
            if (month == s_m and day >= s_d) or (month == e_m and day <= e_d):
                return name
        else:
            if (month == s_m and day >= s_d) or (month == e_m and day <= e_d):
                return name
    return "มังกร"

def get_zodiac_animal(year_ce):
    index = (year_ce - 4) % 12
    return ZODIAC_ANIMALS[index]

def calculate_moon_phase(year, month, day):
    diff_years = year - 2000
    day_count = diff_years * 365.25 + (month - 1) * 30.6 + day
    moon_age = (day_count - 6.5) % 29.530588
    if moon_age < 0:
        moon_age += 29.530588
        
    illumination = (1 - math.cos(math.pi * 2 * moon_age / 29.530588)) / 2 * 100
    
    if moon_age < 14.765:
        phase_name = "ข้างขึ้น (Waxing Moon)"
        kham = int(math.ceil((moon_age / 14.765) * 15))
        kham_str = f"ขึ้น {kham if kham > 0 else 1} ค่ำ"
    else:
        phase_name = "ข้างแรม (Waning Moon)"
        kham = int(math.ceil(((moon_age - 14.765) / 14.765) * 15))
        kham_str = f"แรม {kham if kham > 0 else 1} ค่ำ"
        
    return kham_str, phase_name, round(illumination, 1)

def get_sun_info(day_of_year):
    variation = math.sin((day_of_year - 80) * 2 * math.pi / 365) * 25
    sunrise_m = 375 - variation
    sunset_m = 1095 + variation
    
    sr_h, sr_m = int(sunrise_m // 60), int(sunrise_m % 60)
    ss_h, ss_m = int(sunset_m // 60), int(sunset_m % 60)
    return f"{sr_h:02d}:{sr_m:02d} น.", f"{ss_h:02d}:{ss_m:02d} น."

# ---------------------------------------------------------
# 3. ส่วนหัวของแอป (Header & Logo)
# ---------------------------------------------------------
head_col1, head_col2 = st.columns([1, 6])

with head_col1:
    if os.path.exists("logo1.png"):
        logo_img = Image.open("logo1.png")
        st.image(logo_img, width=80)
    else:
        st.title("🔮")

with head_col2:
    st.markdown("<h1 style='color: #ffd700; margin-bottom: 0;'>ASTROTIME MATRIX</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #00f3ff;'>ระบบคำนวณชะตากาลเวลา ดาราศาสตร์ และโหราศาสตร์</p>", unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 4. ส่วนรับข้อมูล (Inputs - ย้อนหลังได้ตั้งแต่ 1950)
# ---------------------------------------------------------
with st.container():
    st.markdown("### 📅 ระบุวัน เดือน ปี ที่ต้องการคำนวณ")
    col_d, col_m, col_y = st.columns(3)
    
    today_now = datetime.date.today()
    
    with col_d:
        selected_day = st.number_input("วัน (1-31)", min_value=1, max_value=31, value=today_now.day)
        
    with col_m:
        selected_month_str = st.selectbox("เดือน", options=[f"{i} : {MONTHS_TH[i-1]}" for i in range(1, 13)], index=today_now.month-1)
        selected_month = int(selected_month_str.split(":")[0])
        
    with col_y:
        selected_year = st.number_input("ปี (ค.ศ. ตั้งแต่ 1950)", min_value=1950, max_value=2100, value=today_now.year)

# ---------------------------------------------------------
# 5. ประมวลผลข้อมูล
# ---------------------------------------------------------
try:
    target_date = datetime.date(selected_year, selected_month, selected_day)
    date_valid = True
except ValueError:
    st.error("❌ วันที่เลือกไม่ถูกต้อง (เช่น วันที่ 31 ในเดือนที่มีเพียง 30 วัน)")
    date_valid = False

if date_valid:
    weekday_num = target_date.weekday()
    day_name = DAYS_TH[weekday_num]
    month_name = MONTHS_TH[selected_month - 1]
    year_be = selected_year + 543
    
    kham, phase_name, illumination = calculate_moon_phase(selected_year, selected_month, selected_day)
    zodiac_animal = get_zodiac_animal(selected_year)
    zodiac_sign = get_zodiac(selected_day, selected_month)
    
    day_of_year = target_date.timetuple().tm_yday
    sunrise, sunset = get_sun_info(day_of_year)
    
    delta_days = (today_now - target_date).days
    if delta_days > 0:
        time_diff_str = f"ผ่านมาแล้ว {delta_days:,} วัน"
    elif delta_days < 0:
        time_diff_str = f"อีก {abs(delta_days):,} วัน จะถึงวันดังกล่าว"
    else:
        time_diff_str = "คือ วันนี้ปัจจุบัน!"

    lucky_col = LUCKY_COLORS[(selected_day + selected_month) % len(LUCKY_COLORS)]
    lucky_num = (selected_day * selected_month) % 99 + 1

    # ---------------------------------------------------------
    # 6. แสดงผลลัพธ์ (แบ่งเป็น 2 คอลัมน์)
    # ---------------------------------------------------------
    res_col1, res_col2 = st.columns([1.2, 1])

    with res_col1:
        st.markdown(f"""
        <div class="neon-card">
            <h3 class="gold-text">📊 ผลการวิเคราะห์เมทริกซ์กาลเวลา</h3>
            <hr style="border-color: #00f3ff;">
            <p><span class="cyan-text">[1-3] วัน-เดือน-ปี:</span> วัน{day_name} ที่ {selected_day} {month_name} พ.ศ. {year_be} (ค.ศ. {selected_year})</p>
            <p><span class="cyan-text">[4] ข้างขึ้นข้างแรม:</span> <span class="gold-text">{kham}</span> ({phase_name})</p>
            <p><span class="cyan-text">[5] ปีนักษัตร:</span> <span class="purple-text">ปี{zodiac_animal}</span></p>
            <p><span class="cyan-text">[6] ราศี:</span> <span class="red-text">ราศี{zodiac_sign}</span></p>
            <p><span class="cyan-text">[7] ค่าดวงจันทร์:</span> <span class="green-text">ความสว่าง {illumination}%</span></p>
            <p><span class="cyan-text">[8] ค่าดวงอาทิตย์:</span> <span class="gold-text">ขึ้น ~{sunrise} | ตก ~{sunset}</span></p>
            <p><span class="cyan-text">[9] พิกัดอ้างอิง:</span> <span class="blue-text">Lat 13.7563° N | Lon 100.5018° E (กทม.)</span></p>
            <p><span class="cyan-text">[10] การคำนวณวัน:</span> <span class="red-text">{time_diff_str}</span></p>
            <hr style="border-color: #b000ff;">
            <h4 class="purple-text">🔮 พลังชะตาประจำวัน (Special Feature)</h4>
            <p>• สีมงคลเสริมพลัง: <span class="green-text">{lucky_col}</span></p>
            <p>• เลขนำโชคประจำวัน: <span class="gold-text">{lucky_num}</span></p>
        </div>
        """, unsafe_allow_html=True)

    with res_col2:
        # [12] คำนวณหาวันที่ตรงกัน ย้อนหลัง 50 ปี / ล่วงหน้า 50 ปี
        st.markdown("""
        <div class="neon-card-purple">
            <h4 class="gold-text">🔄 ปีที่มีวัน-ราศี-นักษัตร ตรงกัน (+/- 50 ปี)</h4>
        </div>
        """, unsafe_allow_html=True)

        start_y = max(1950, selected_year - 50)
        end_y = selected_year + 50
        matching_years = []

        for y in range(start_y, end_y + 1):
            if y == selected_year:
                continue
            try:
                chk_date = datetime.date(y, selected_month, selected_day)
                chk_animal = get_zodiac_animal(y)
                if chk_date.weekday() == weekday_num and chk_animal == zodiac_animal:
                    matching_years.append(f"พ.ศ. {y+543} (ค.ศ. {y}) - วัน{DAYS_TH[weekday_num]}")
            except ValueError:
                continue

        if matching_years:
            st.success(f"พบ {len(matching_years)} ปีที่ตรงกันเป๊ะ:")
            st.write(matching_years)
        else:
            st.info("ไม่พบปีที่มีเงื่อนไขตรงกันในช่วง +/- 50 ปี")

        # ---------------------------------------------------------
        # 7. เครื่องเล่นเพลง (Music Player Component)
        # ---------------------------------------------------------
        st.markdown("---")
        st.markdown("### 🎵 เครื่องเล่นเพลง (Music Player)")
        
        music_files = glob.glob("*.mp3") + glob.glob("*.wav") + glob.glob("*.ogg")
        
        if music_files:
            selected_song = st.selectbox("เลือกเพลงในโฟลเดอร์:", music_files)
            if selected_song:
                audio_file = open(selected_song, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
                st.caption(f"🎧 กำลังเล่นเพลง: {selected_song}")
        else:
            st.warning("⚠️ ไม่พบไฟล์เพลง (.mp3) ในโฟลเดอร์เดียวกับโค้ด")
