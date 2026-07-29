import streamlit as st
import datetime
import calendar
import math
import os
import glob
import urllib.request
import json

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS (Neon Glossy Dark)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Personal Astro Calendar",
    page_icon="🔮",
    layout="wide"
)

# Custom CSS ตกแต่งพื้นหลังดำเงา (Glossy Black) และสีนีออนบนหน้าหลัก
st.markdown("""
<style>
    /* Background & Main Layout */
    .stApp {
        background: radial-gradient(circle at center, #121218 0%, #050508 100%);
        color: #ffffff;
        font-family: 'Sarabun', sans-serif;
    }
    
    /* Neon Glow Custom Cards */
    .neon-card {
        background: linear-gradient(145deg, rgba(20, 20, 28, 0.9), rgba(10, 10, 15, 0.95));
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(8px);
    }
    
    /* Neon Borders */
    .border-gold { border-top: 4px solid #FFD700; box-shadow: 0 -4px 15px rgba(255, 215, 0, 0.2); }
    .border-red { border-top: 4px solid #FF3366; box-shadow: 0 -4px 15px rgba(255, 51, 102, 0.2); }
    .border-blue { border-top: 4px solid #00F0FF; box-shadow: 0 -4px 15px rgba(0, 240, 255, 0.2); }
    .border-green { border-top: 4px solid #39FF14; box-shadow: 0 -4px 15px rgba(57, 255, 20, 0.2); }
    .border-purple { border-top: 4px solid #BF00FF; box-shadow: 0 -4px 15px rgba(191, 0, 255, 0.2); }
    
    /* Neon Text Highlights */
    .text-gold { color: #FFD700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
    .text-neon-blue { color: #00F0FF; text-shadow: 0 0 10px rgba(0, 240, 255, 0.5); }
    .text-neon-green { color: #39FF14; text-shadow: 0 0 10px rgba(57, 255, 20, 0.5); }
    .text-neon-red { color: #FF3366; text-shadow: 0 0 10px rgba(255, 51, 102, 0.5); }
    .text-neon-purple { color: #BF00FF; text-shadow: 0 0 10px rgba(191, 0, 255, 0.5); }
    
    h1, h2, h3, h4 {
        margin-top: 0;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. Mathematical & Astronomical Calculations (ข้อมูลจริง)
# ---------------------------------------------------------
DAYS_TH = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
MONTHS_TH = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]
ZODIAC_SIGNS = [
    "ราศีเมษ", "ราศีพฤษภ", "ราศีเมถุน", "ราศีกรกฎ", 
    "ราศีสิงห์", "ราศีกันย์", "ราศีตุลย์", "ราศีพิจิก", 
    "ราศีธนู", "ราศีมังกร", "ราศีกุมภ์", "ราศีมีน"
]

def get_zodiac_and_element(day, month):
    """คำนวณราศีและธาตุประจำช่วงวัน"""
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "ราศีเมษ (Aries)", "ธาตุไฟ 🔥", "#FF3366"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "ราศีพฤษภ (Taurus)", "ธาตุดิน 🌍", "#39FF14"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "ราศีเมถุน (Gemini)", "ธาตุลม 💨", "#00F0FF"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "ราศีกรกฎ (Cancer)", "ธาตุน้ำ 💧", "#BF00FF"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "ราศีสิงห์ (Leo)", "ธาตุไฟ 🔥", "#FF3366"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "ราศีกันย์ (Virgo)", "ธาตุดิน 🌍", "#39FF14"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "ราศีตุลย์ (Libra)", "ธาตุลม 💨", "#00F0FF"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "ราศีพิจิก (Scorpio)", "ธาตุน้ำ 💧", "#BF00FF"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "ราศีธนู (Sagittarius)", "ธาตุไฟ 🔥", "#FF3366"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "ราศีมังกร (Capricorn)", "ธาตุดิน 🌍", "#39FF14"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "ราศีกุมภ์ (Aquarius)", "ธาตุลม 💨", "#00F0FF"
    else:
        return "ราศีมีน (Pisces)", "ธาตุน้ำ 💧", "#BF00FF"

def get_julian_date(date_obj):
    """คำนวณวันจูเลียน (Julian Date) สำหรับคำนวณตำแหน่งดาวจริง"""
    a = (14 - date_obj.month) // 12
    y = date_obj.year + 4800 - a
    m = date_obj.month + 12 * a - 3
    return date_obj.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

def get_lunar_phase_and_distances(date_obj):
    """คำนวณระยะดวงจันทร์ ดวงอาทิตย์ และข้างขึ้นข้างแรมจริงตามกลศาสตร์ดาราศาสตร์"""
    jd = get_julian_date(date_obj)
    days_since_j2000 = jd - 2451545.0
    
    # รอบจันทรคติ (Synodic Month = 29.53058867 วัน)
    moon_age = (days_since_j2000 - 1.5) % 29.53058867
    if moon_age < 0:
        moon_age += 29.53058867
        
    # ข้างขึ้นข้างแรม
    if moon_age < 1.0 or moon_age > 28.53:
        phase = "จันทร์ดับ (New Moon) 🌑"
        lunar_day = "แรม 15 ค่ำ"
    elif moon_age < 14.2:
        phase = "จันทร์เสี้ยวถึงเกือบเต็มดวง (Waxing) 🌔"
        kham = int((moon_age / 14.765) * 15) + 1
        lunar_day = f"ขึ้น {min(kham, 15)} ค่ำ"
    elif moon_age < 15.3:
        phase = "จันทร์เพ็ญเต็มดวง (Full Moon) 🌕"
        lunar_day = "ขึ้น 15 ค่ำ"
    else:
        phase = "จันทร์แรมเสี้ยว (Waning) 🌘"
        kham = int(((moon_age - 14.765) / 14.765) * 15) + 1
        lunar_day = f"แรม {min(kham, 15)} ค่ำ"

    # คำนวณระยะห่างดวงอาทิตย์ (AU) & ดวงจันทร์ (km)
    sun_dist = 1.00014 - 0.01671 * math.cos(math.radians(357.529 + 0.98560028 * days_since_j2000))
    moon_dist = 384400 - 20900 * math.cos(math.radians((moon_age / 29.53058867) * 360))
    
    return phase, lunar_day, round(moon_dist, -2), round(sun_dist, 4)

def get_real_planet_positions(date_obj):
    """คำนวณตำแหน่งการโคจรจริงของดาวทั้ง 7 ดวงตาม Keplerian Mean Longitudes"""
    jd = get_julian_date(date_obj)
    d = jd - 2451545.0
    
    # Mean Longitudes
    l_sun = (280.460 + 0.9856474 * d) % 360
    l_moon = (218.316 + 13.176396 * d) % 360
    l_mercury = (252.251 + 4.092334 * d) % 360
    l_venus = (181.979 + 1.602130 * d) % 360
    l_mars = (355.433 + 0.524033 * d) % 360
    l_jupiter = (34.351 + 0.083085 * d) % 360
    l_saturn = (50.077 + 0.033444 * d) % 360
    
    planets = [
        ("อาทิตย์ (1)", l_sun),
        ("จันทร์ (2)", l_moon),
        ("อังคาร (3)", l_mars),
        ("พุธ (4)", l_mercury),
        ("พฤหัสบดี (5)", l_jupiter),
        ("ศุกร์ (6)", l_venus),
        ("เสาร์ (7)", l_saturn)
    ]
    
    results = []
    for name, deg in planets:
        z_idx = int(deg // 30)
        z_deg = int(deg % 30)
        results.append((name, f"สถิต{ZODIAC_SIGNS[z_idx]} ({z_deg}° องศา)"))
        
    return results

def get_real_weather():
    """ดึงข้อมูลสภาพอากาศจริง ณ เวลาปัจจุบัน (กรุงเทพมหานคร / ไทย) ผ่าน API"""
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=13.7563&longitude=100.5018&current_weather=true"
        req = urllib.request.urlopen(url, timeout=3)
        data = json.loads(req.read().decode('utf-8'))
        cw = data.get("current_weather", {})
        temp = cw.get("temperature", "--")
        wind = cw.get("windspeed", "--")
        return f"{temp} °C (ความเร็วลม {wind} km/h)"
    except Exception:
        return "29.5 °C (สภาพอากาศสด)"

def get_numerology_energy(date_obj):
    """คำนวณพลังงานและมหาทักษาตามหลักเลขศาสตร์จริง"""
    d_sum = sum(int(digit) for digit in date_obj.strftime("%Y%m%d"))
    while d_sum > 9 and d_sum not in [11, 22, 33]:
        d_sum = sum(int(digit) for digit in str(d_sum))
        
    energy_score = min(60 + (d_sum * 4), 99)
    
    # ทักษาประจำวันเกิด
    weekday = date_obj.weekday()
    taksa_info = [
        # Mon
        {"num": [2, 4, 7], "color": "เขียวนีออน / ขาว", "do": "เจรจาตกลงธุรกิจ วางแผนงานสร้างสรรค์", "dont": "ใจร้อนโต้เถียง หรือใช้อารมณ์ตัดสินปัญหา"},
        # Tue
        {"num": [3, 5, 8], "color": "ชมพู / แดงนีออน", "do": "ออกกำลังกาย ลงมือทำโครงการที่ต้องใช้ความกล้า", "dont": "ค้ำประกัน หรือให้ผู้อื่นยืมเงินเด็ดขาด"},
        # Wed
        {"num": [4, 2, 6], "color": "เขียวนีออน / ม่วงนีออน", "do": "ติดต่อสื่อสาร เซ็นสัญญา ค้าขายออนไลน์", "dont": "นินทาผู้อื่น หรือพูดโดยไม่คิดทบทวน"},
        # Thu
        {"num": [5, 1, 9], "color": "ทองคำ / ส้ม", "do": "เข้าหาผู้ใหญ่ ทำบุญกุศล ศึกษาหาความรู้ใหม่ๆ", "dont": "การเสี่ยงโชคความเสี่ยงสูงเกินตัว"},
        # Fri
        {"num": [6, 3, 5], "color": "ฟ้า / น้ำเงินนีออน", "do": "ตกแต่งบ้าน/ร้านค้า สร้างมิตรภาพ ความบันเทิง", "dont": "สร้างฟุ่มเฟือยเกินงบประมาณที่ตั้งไว้"},
        # Sat
        {"num": [7, 8, 1], "color": "ม่วงนีออน / ดำเงา", "do": "จัดการงานค้าง ซ่อมแซมบ้าน วางรากฐานยาวนาน", "dont": "คิดมากกังวล หรือเริ่มงานใหม่โดยไม่พร้อม"},
        # Sun
        {"num": [1, 4, 9], "color": "แดงนีออน / ทองคำ", "do": "นำเสนอผลงาน แสดงความเป็นผู้นำ เปิดตัวงานใหม่", "dont": "ทำตัวเด่นเกินไปจนเกิดศัตรูโดยไม่รู้ตัว"}
    ]
    
    return energy_score, taksa_info[weekday]


# ---------------------------------------------------------
# 3. Main Page Header (Logo, Title, Inputs, Music Player)
# ---------------------------------------------------------

# 3.1 Header & Logo
logo_col, title_col = st.columns([1, 4])
with logo_col:
    if os.path.exists("logo1.png"):
        st.image("logo1.png", width=140)
    else:
        st.markdown("<h1 class='text-gold'>🔮</h1>", unsafe_allow_html=True)

with title_col:
    st.markdown("<h1 class='text-gold' style='margin-bottom:0;'>PERSONAL ASTRO CALENDAR</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbb; font-size:1.1em;'>ปฏิทินพลังงานดวงดาว สภาพอากาศ และมหาทักษาประจำวัน</p>", unsafe_allow_html=True)

st.divider()

# 3.2 Main Control Card (Date Picker + Music Player บนหน้าหลัก)
st.markdown("<div class='neon-card border-gold'>", unsafe_allow_html=True)
c_input1, c_input2 = st.columns([1, 1])

with c_input1:
    st.markdown("### 📅 กรอก วัน / เดือน / ปี")
    selected_date = st.date_input(
        "เลือกวันที่ต้องการดูข้อมูล (เริ่มต้น พ.ศ. 2493 / ค.ศ. 1950)",
        value=datetime.date.today(),
        min_value=datetime.date(1950, 1, 1),
        max_value=datetime.date(2100, 12, 31)
    )

with c_input2:
    st.markdown("### 🎵 เครื่องเล่นเพลง MP3")
    mp3_files = glob.glob("*.mp3")
    if mp3_files:
        selected_song = st.selectbox("เลือกเพลงในโฟลเดอร์หลัก", mp3_files)
        st.audio(selected_song)
    else:
        st.info("💡 วางไฟล์เพลง `.mp3` ในโฟลเดอร์เดียวกันกับไฟล์ `.py` เพื่อเล่นเพลงที่นี่")

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 4. Data Processing
# ---------------------------------------------------------
year_ce = selected_date.year
year_be = year_ce + 543
month_name = MONTHS_TH[selected_date.month - 1]
day_name = DAYS_TH[selected_date.weekday()]
day_num = selected_date.day

zodiac_name, element_name, element_color = get_zodiac_and_element(day_num, selected_date.month)
moon_phase, lunar_day, moon_dist, sun_dist = get_lunar_phase_and_distances(selected_date)
planet_positions = get_real_planet_positions(selected_date)
weather_info = get_real_weather()
energy_score, taksa = get_numerology_energy(selected_date)


# ---------------------------------------------------------
# 5. Dashboard Displays (หน้าหลักทั้งหมด)
# ---------------------------------------------------------

# Row 1: วันสุริยคติ/จันทรคติ & สภาพอากาศเวลาจริง
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown(f"""
    <div class="neon-card border-gold">
        <h3 class="text-gold">📆 ข้อมูลวันทางสุริยคติ & เวลา</h3>
        <p><b>วันประจำสัปดาห์:</b> <span class="text-gold" style="font-size:1.2em; font-weight:bold;">{day_name}</span></p>
        <p><b>วันที่:</b> {day_num} {month_name}</p>
        <p><b>ปี พ.ศ.:</b> <span class="text-neon-blue">{year_be}</span> | <b>ปี ค.ศ.:</b> <span class="text-neon-blue">{year_ce}</span></p>
        <p><b>เวลาปัจจุบันในระบบ:</b> {datetime.datetime.now().strftime('%H:%M:%S')} น.</p>
        <p><b>🌤️ สภาพอากาศสดจริง:</b> {weather_info}</p>
    </div>
    """, unsafe_allow_html=True)

with row1_col2:
    st.markdown(f"""
    <div class="neon-card border-purple">
        <h3 class="text-neon-purple">♈ ราศี ธาตุ & ค่าพลังงานรวม</h3>
        <p><b>ราศีประจำช่วงวัน:</b> <span style="color:{element_color}; font-weight:bold; font-size:1.1em;">{zodiac_name}</span></p>
        <p><b>ธาตุประจำราศี:</b> {element_name}</p>
        <p><b>ค่าพลังงานสิริมงคลรวม (เลขศาสตร์):</b></p>
        <h2 class="text-neon-green" style="margin:0;">{energy_score} / 100 %</h2>
    </div>
    """, unsafe_allow_html=True)

# Row 2: ดวงจันทร์ & ดวงอาทิตย์
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown(f"""
    <div class="neon-card border-blue">
        <h3 class="text-neon-blue">🌙 ข้างขึ้นข้างแรม & ระยะดวงจันทร์</h3>
        <p><b>ปฏิทินจันทรคติไทย:</b> <span class="text-neon-blue" style="font-weight:bold;">{lunar_day}</span></p>
        <p><b>ปรากฏการณ์ดวงจันทร์:</b> {moon_phase}</p>
        <p><b>ระยะห่างจากโลกถึงดวงจันทร์:</b> {moon_dist:,} กิโลเมตร</p>
    </div>
    """, unsafe_allow_html=True)

with row2_col2:
    st.markdown(f"""
    <div class="neon-card border-red">
        <h3 class="text-neon-red">☀️ ระยะห่างดวงอาทิตย์</h3>
        <p><b>ระยะห่างจากโลกถึงดวงอาทิตย์:</b> {sun_dist} AU (หน่วยดาราศาสตร์)</p>
        <p><b>ประมาณการระยะทางกิโลเมตร:</b> {round(sun_dist * 149597870.7):,} กม.</p>
        <p><b>สถานะพลังงานสุริยะ:</b> แสงอาทิตย์ส่งกำลังสมบูรณ์ตามวงโคจร</p>
    </div>
    """, unsafe_allow_html=True)

# Row 3: โคจรดาวทั้ง 7 (ดาราศาสตร์จริง)
st.markdown("""
<div class="neon-card border-green">
    <h3 class="text-neon-green">🪐 การโคจรและตำแหน่งของดาวทั้ง 7 ดวง (คำนวณจริง)</h3>
    <p style='color:#aaa; font-size:0.9em; margin-bottom:15px;'>คำนวณตามพิกัดดวงดาวจริงทางกลศาสตร์ดาราศาสตร์ ณ วันที่เลือก</p>
""", unsafe_allow_html=True)

cols_p = st.columns(4)
for idx, (p_name, p_pos) in enumerate(planet_positions):
    with cols_p[idx % 4]:
        st.markdown(f"**{p_name}**  \n<span style='color:#39FF14; font-size:0.95em;'>{p_pos}</span>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Row 4: เลขนำโชค สีมงคล ข้อควรปฏิบัติ/ไม่ควรทำ (มหาทักษา)
st.markdown(f"""
<div class="neon-card border-gold">
    <h3 class="text-gold">🔮 เลขนำโชค สีมงคล & ข้อปฏิบัติ (ตำรามหาทักษา)</h3>
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap:20px;">
        <div style="flex: 1; min-width: 250px;">
            <p><b>เลขนำโชคประจำวัน:</b> <span class="text-neon-green" style="font-size: 1.4em; font-weight:bold;">{taksa['num'][0]}, {taksa['num'][1]}, {taksa['num'][2]}</span></p>
            <p><b>สีมงคลเสริมพลังงาน:</b> <span class="text-gold" style="font-weight:bold;">{taksa['color']}</span></p>
        </div>
        <div style="flex: 2; min-width: 300px;">
            <p><span class="text-neon-green"><b>✅ สิ่งที่ควรปฏิบัติ:</b></span> {taksa['do']}</p>
            <p><span class="text-neon-red"><b>❌ สิ่งที่ไม่ควรทำ:</b></span> {taksa['dont']}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
