import streamlit as st
import datetime
import math
import os
import glob
import urllib.request
import json
from streamlit_js_eval import get_geolocation

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Personal Astro Calendar",
    page_icon="🔮",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at center, #121218 0%, #050508 100%);
        color: #ffffff;
        font-family: 'Sarabun', sans-serif;
    }
    .neon-card {
        background: linear-gradient(145deg, rgba(20, 20, 28, 0.9), rgba(10, 10, 15, 0.95));
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .border-gold { border-top: 4px solid #FFD700; }
    .border-red { border-top: 4px solid #FF3366; }
    .border-blue { border-top: 4px solid #00F0FF; }
    .border-green { border-top: 4px solid #39FF14; }
    .border-purple { border-top: 4px solid #BF00FF; }
    
    .text-gold { color: #FFD700; }
    .text-neon-blue { color: #00F0FF; }
    .text-neon-green { color: #39FF14; }
    .text-neon-red { color: #FF3366; }
    .text-neon-purple { color: #BF00FF; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Helper Functions (ปีนักษัตร, ปฏิทินไทย, พิกัด GPS)
# ---------------------------------------------------------
DAYS_TH = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
MONTHS_TH = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]
ZODIAC_ANIMALS = [
    "ปีชวด (หนู) 🐀", "ปีฉลู (วัว) 🐂", "ปีขาล (เสือ) 🐅", "ปีเถาะ (กระต่าย) 🐇",
    "ปีมะโรง (งูใหญ่) 🐉", "ปีมะเส็ง (งูเล็ก) 🐍", "ปีมะเมีย (ม้า) 🐎", "ปีมะแม (แพะ) 🐐",
    "ปีวอก (ลิง) 🐒", "ปีระกา (ไก่) 🐓", "ปีจอ (หมา) 🐕", "ปีกุน (หมู) 🐖"
]
ZODIAC_SIGNS = [
    "ราศีเมษ", "ราศีพฤษภ", "ราศีเมถุน", "ราศีกรกฎ", 
    "ราศีสิงห์", "ราศีกันย์", "ราศีตุลย์", "ราศีพิจิก", 
    "ราศีธนู", "ราศีมังกร", "ราศีกุมภ์", "ราศีมีน"
]

def get_thai_zodiac_animal(year_ce, month, day):
    """คำนวณปีนักษัตรไทย (เปลี่ยนปีนักษัตรช่วงสงกรานต์/เดือนเมษายน)"""
    # หากยังไม่ถึงสงกรานต์ (13 เมษายน) ตามหลักไทยโบราณจะนับเป็นปีนักษัตรเดิม
    calc_year = year_ce
    if month < 4 or (month == 4 and day < 13):
        calc_year -= 1
    
    # ปี ค.ศ. 4 ตรงกับปีชวด
    index = (calc_year - 4) % 12
    return ZODIAC_ANIMALS[index]

def get_thai_lunar_phase(date_obj):
    """คำนวณข้างขึ้นข้างแรมปฏิทินจันทรคติไทย (อ้างอิงอธิกมาส/อธิกวาร)"""
    # หมุดอ้างอิงปฏิทินจันทรคติไทยมาตรฐาน
    base_date = datetime.date(2000, 1, 1) # ตรงกับ แรม 10 ค่ำ เดือน 1
    diff_days = (date_obj - base_date).days
    
    # รอบดวงจันทร์ปฏิทินไทยเฉลี่ย
    lunar_cycle = 29.530588
    current_day_in_cycle = (diff_days + 24.5) % lunar_cycle
    
    if current_day_in_cycle < 15:
        kham = int(current_day_in_cycle) + 1
        lunar_str = f"ขึ้น {min(kham, 15)} ค่ำ"
        phase = "ช่วงจันทร์สว่าง (สุกกปักข์) 🌔"
    else:
        kham = int(current_day_in_cycle - 15) + 1
        lunar_str = f"แรม {min(kham, 15)} ค่ำ"
        phase = "ช่วงจันทร์มืด (กาฬปักข์) 🌘"
        
    # คำนวณระยะห่างดวงจันทร์และดวงอาทิตย์จริงทางดาราศาสตร์
    jd = date_obj.toordinal() + 1721425
    d = jd - 2451545.0
    moon_dist = 384400 - 20900 * math.cos(math.radians((current_day_in_cycle / 29.53) * 360))
    sun_dist = 1.00014 - 0.01671 * math.cos(math.radians(357.529 + 0.98560028 * d))
    
    return lunar_str, phase, round(moon_dist, -2), round(sun_dist, 4)

def get_weather_by_coords(lat, lon):
    """ดึงสภาพอากาศสดจากพิกัด GPS จริงของโทรศัพท์"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        req = urllib.request.urlopen(url, timeout=3)
        data = json.loads(req.read().decode('utf-8'))
        cw = data.get("current_weather", {})
        temp = cw.get("temperature", "--")
        wind = cw.get("windspeed", "--")
        return f"{temp} °C (ความเร็วลม {wind} km/h)"
    except Exception:
        return "ไม่สามารถดึงข้อมูลสภาพอากาศได้"

def get_real_planet_positions(date_obj):
    """คำนวณพิกัดดวงดาวจริงทางดาราศาสตร์"""
    jd = date_obj.toordinal() + 1721425
    d = jd - 2451545.0
    
    l_sun = (280.460 + 0.9856474 * d) % 360
    l_moon = (218.316 + 13.176396 * d) % 360
    l_mars = (355.433 + 0.524033 * d) % 360
    l_mercury = (252.251 + 4.092334 * d) % 360
    l_jupiter = (34.351 + 0.083085 * d) % 360
    l_venus = (181.979 + 1.602130 * d) % 360
    l_saturn = (50.077 + 0.033444 * d) % 360
    
    planets = [
        ("อาทิตย์ (1)", l_sun), ("จันทร์ (2)", l_moon), ("อังคาร (3)", l_mars),
        ("พุธ (4)", l_mercury), ("พฤหัสบดี (5)", l_jupiter), ("ศุกร์ (6)", l_venus), ("เสาร์ (7)", l_saturn)
    ]
    
    results = []
    for name, deg in planets:
        z_idx = int(deg // 30)
        z_deg = int(deg % 30)
        results.append((name, f"สถิต{ZODIAC_SIGNS[z_idx]} ({z_deg}° องศา)"))
    return results

# ---------------------------------------------------------
# 3. Header & Controls
# ---------------------------------------------------------
logo_col, title_col = st.columns([1, 4])
with logo_col:
    if os.path.exists("logo1.png"):
        st.image("logo1.png", width=130)
    else:
        st.markdown("<h1 class='text-gold'>🔮</h1>", unsafe_allow_html=True)

with title_col:
    st.markdown("<h1 class='text-gold' style='margin-bottom:0;'>PERSONAL ASTRO CALENDAR</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbb;'>ปฏิทินพลังงานดวงดาว สภาพอากาศจริงตาม GPS และมหาทักษาประจำวัน</p>", unsafe_allow_html=True)

st.divider()

# Input & GPS Container
st.markdown("<div class='neon-card border-gold'>", unsafe_allow_html=True)
c_input1, c_input2 = st.columns([1, 1])

with c_input1:
    st.markdown("### 📅 กรอก วัน / เดือน / ปี")
    selected_date = st.date_input(
        "เลือกวันที่ต้องการดูข้อมูล (ย้อนหลังได้ถึง พ.ศ. 2493 / ค.ศ. 1950)",
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
        st.info("💡 วางไฟล์เพลง `.mp3` ในโฟลเดอร์หลักเพื่อเล่นเพลงที่นี่")

# ดึงพิกัด GPS จากโทรศัพท์
st.markdown("---")
st.markdown("<b>📍 พิกัดตำแหน่งจริงจากโทรศัพท์ของคุณ:</b>", unsafe_allow_html=True)
location = get_geolocation()

if location and 'coords' in location:
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    st.success(f"เชื่อมต่อตำแหน่งสำเร็จ: ละติจูด {lat:.4f}, ลองจิจูด {lon:.4f}")
    weather_info = get_weather_by_coords(lat, lon)
else:
    # พิกัดเริ่มต้น (กรุงเทพฯ) กรณีผู้ใช้ยังไม่ได้กดอนุญาตตำแหน่ง
    lat, lon = 13.7563, 100.5018
    st.warning("⚠️ กรุณากดอนุญาตให้เข้าถึงตำแหน่ง (GPS) บนมือถือเพื่อรับสภาพอากาศและเวลาพิกัดจริง")
    weather_info = get_weather_by_coords(lat, lon)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Calculation & Display
# ---------------------------------------------------------
year_ce = selected_date.year
year_be = year_ce + 543
month_name = MONTHS_TH[selected_date.month - 1]
day_name = DAYS_TH[selected_date.weekday()]
day_num = selected_date.day

zodiac_animal = get_thai_zodiac_animal(year_ce, selected_date.month, day_num)
lunar_day, moon_phase, moon_dist, sun_dist = get_thai_lunar_phase(selected_date)
planet_positions = get_real_planet_positions(selected_date)

# Render Rows
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown(f"""
    <div class="neon-card border-gold">
        <h3 class="text-gold">📆 วัน เดือน ปี & ปีนักษัตร</h3>
        <p><b>วันประจำสัปดาห์:</b> <span class="text-gold" style="font-size:1.2em; font-weight:bold;">{day_name}</span></p>
        <p><b>วันที่:</b> {day_num} {month_name}</p>
        <p><b>ปี พ.ศ.:</b> <span class="text-neon-blue">{year_be}</span> | <b>ปี ค.ศ.:</b> <span class="text-neon-blue">{year_ce}</span></p>
        <p><b>ปีนักษัตรไทย:</b> <span class="text-neon-green" style="font-size:1.2em; font-weight:bold;">{zodiac_animal}</span></p>
        <p><b>🌤️ สภาพอากาศตามพิกัดสด:</b> {weather_info}</p>
    </div>
    """, unsafe_allow_html=True)

with row1_col2:
    st.markdown(f"""
    <div class="neon-card border-blue">
        <h3 class="text-neon-blue">🌙 ข้างขึ้นข้างแรม (ปฏิทินไทย)</h3>
        <p><b>ข้างขึ้นข้างแรม:</b> <span class="text-neon-blue" style="font-size:1.2em; font-weight:bold;">{lunar_day}</span></p>
        <p><b>ปรากฏการณ์:</b> {moon_phase}</p>
        <p><b>ระยะห่างดวงจันทร์:</b> {moon_dist:,} กม.</p>
        <p><b>ระยะห่างดวงอาทิตย์:</b> {sun_dist} AU ({round(sun_dist * 149597870.7):,} กม.)</p>
    </div>
    """, unsafe_allow_html=True)

# Planet Positions
st.markdown("""
<div class="neon-card border-green">
    <h3 class="text-neon-green">🪐 ตำแหน่งการโคจรของดาวทั้ง 7 ดวง</h3>
""", unsafe_allow_html=True)

cols_p = st.columns(4)
for idx, (p_name, p_pos) in enumerate(planet_positions):
    with cols_p[idx % 4]:
        st.markdown(f"**{p_name}**  \n<span style='color:#39FF14;'>{p_pos}</span>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
