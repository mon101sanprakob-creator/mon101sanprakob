import streamlit as st
import datetime
import math
import os
import glob
import urllib.request
import json
import random
from streamlit_js_eval import get_geolocation

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS (Neon Glossy Dark Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Personal Astro Calendar",
    page_icon="🔮",
    layout="wide"
)

# Custom CSS ตกแต่งพื้นหลังดำเงา (Glossy Black) และโทนสีนีออนตามระบุ
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
        border: 1px solid rgba(255, 255, 255, 0.08);
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
# 2. Master Calculations & Helper Functions
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
    """คำนวณปีนักษัตรไทย (เปลี่ยนปีนักษัตรช่วงวันสงกรานต์ 13 เมษายน)"""
    calc_year = year_ce
    if month < 4 or (month == 4 and day < 13):
        calc_year -= 1
    index = (calc_year - 4) % 12
    return ZODIAC_ANIMALS[index]

def get_zodiac_and_element(day, month):
    """คำนวณราศีสุริยคติและธาตุประจำช่วงวันเกิด/วันที่เลือก"""
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

def get_thai_lunar_phase(date_obj):
    """คำนวณข้างขึ้นข้างแรมปฏิทินจันทรคติไทยพร้อมระยะห่างทางดาราศาสตร์จริง"""
    base_date = datetime.date(2000, 1, 1)  # แรม 10 ค่ำ เดือน 1
    diff_days = (date_obj - base_date).days
    
    lunar_cycle = 29.53058882
    current_day_in_cycle = (diff_days + 24.5) % lunar_cycle
    
    if current_day_in_cycle < 14.765:
        kham = int(current_day_in_cycle) + 1
        lunar_str = f"ขึ้น {min(kham, 15)} ค่ำ"
        phase = "ช่วงจันทร์สว่าง (สุกกปักข์) 🌔"
    else:
        kham = int(current_day_in_cycle - 14.765) + 1
        lunar_str = f"แรม {min(kham, 15)} ค่ำ"
        phase = "ช่วงจันทร์มืด (กาฬปักข์) 🌘"
        
    jd = date_obj.toordinal() + 1721425
    d = jd - 2451545.0
    moon_dist = 384400 - 20900 * math.cos(math.radians((current_day_in_cycle / lunar_cycle) * 360))
    sun_dist = 1.00014 - 0.01671 * math.cos(math.radians(357.529 + 0.98560028 * d))
    
    return lunar_str, phase, round(moon_dist, -2), round(sun_dist, 4)

def get_real_planet_positions(date_obj):
    """คำนวณตำแหน่งการโคจรจริงของดาวทั้ง 7 ดวงตามหลักดาราศาสตร์"""
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

def get_weather_by_coords(lat, lon):
    """ดึงข้อมูลสภาพอากาศสดจริงจากตำแหน่งละติจูดและลองจิจูดของโทรศัพท์"""
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

def get_numerology_and_taksa(date_obj):
    """คำนวณพลังงานรวม เลขมงคล สีมงคล ข้อปฏิบัติและข้อห้ามตามหลักตำราทักษาไทย"""
    d_sum = sum(int(digit) for digit in date_obj.strftime("%Y%m%d"))
    while d_sum > 9 and d_sum not in [11, 22, 33]:
        d_sum = sum(int(digit) for digit in str(d_sum))
        
    energy_score = min(62 + (d_sum * 4), 99)
    weekday = date_obj.weekday()
    
    taksa_info = [
        # Monday
        {"num": [2, 4, 7], "color": "เขียวนีออน / ขาว / เหลืองทอง", "do": "เจรจาติดต่อธุรกิจ งานขาย งานสร้างสรรค์ และการเข้าหาผู้ใหญ่", "dont": "การใช้อารมณ์ตัดสินปัญหา หรือโต้เถียงในเรื่องไร้สาระ"},
        # Tuesday
        {"num": [3, 5, 8], "color": "ชมพู / แดงนีออน / ดำเงา", "do": "ออกกำลังกาย ลงมือทำโครงการใหม่ที่ต้องใช้ความเด็ดขาด", "dont": "การค้ำประกัน ให้ผู้อื่นยืมเงิน หรือเสี่ยงโชคเกินตัว"},
        # Wednesday
        {"num": [4, 2, 6], "color": "เขียวนีออน / ม่วงนีออน / ฟ้า", "do": "การทำสัญญา ค้าขายออนไลน์ ประสานงาน และการเรียนรู้สิ่งใหม่", "dont": "การพูดโดยไม่คิด หรือการนินทาที่อาจนำภัยมาสู่ตน"},
        # Thursday
        {"num": [5, 1, 9], "color": "ทองคำ / ส้ม / แดง", "do": "ทำบุญ สวดมนต์ ปรึกษาผู้เชี่ยวชาญ และการวางแผนระยะยาว", "dont": "การลงทุนที่มีความเสี่ยงสูงโดยไร้การศึกษารายละเอียด"},
        # Friday
        {"num": [6, 3, 5], "color": "ฟ้า / น้ำเงินนีออน / ชมพู", "do": "งานศิลปะ การตกแต่งสถานที่ สร้างมิตรภาพ และการสังสรรค์", "dont": "การจับจ่ายใช้สอยฟุ่มเฟือยเกินงบประมาณที่วางไว้"},
        # Saturday
        {"num": [7, 8, 1], "color": "ม่วงนีออน / ดำเงา / น้ำเงิน", "do": "สะสางงานค้าง ซ่อมแซมบ้านเรือน และการจัดระเบียบชีวิต", "dont": "การวิตกกังวลมากเกินไป หรือการเริ่มงานใหญ่โดยไม่พร้อม"},
        # Sunday
        {"num": [1, 4, 9], "color": "แดงนีออน / ทองคำ / เขียว", "do": "การเสนอผลงาน เปิดตัวสินค้า แสดงความเป็นผู้นำ", "dont": "การทำตัวเด่นเกินไปจนก่อให้เกิดศัตรูโดยไม่รู้ตัว"}
    ]
    return energy_score, taksa_info[weekday]


# ---------------------------------------------------------
# 3. Main Header (Logo, Controls, Music Player)
# ---------------------------------------------------------
logo_col, title_col = st.columns([1, 4])
with logo_col:
    if os.path.exists("logo1.png"):
        st.image("logo1.png", width=130)
    else:
        st.markdown("<h1 class='text-gold'>🔮</h1>", unsafe_allow_html=True)

with title_col:
    st.markdown("<h1 class='text-gold' style='margin-bottom:0;'>PERSONAL ASTRO CALENDAR</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#bbb;'>ปฏิทินพลังงานดวงดาว สภาพอากาศสดตามพิกัด GPS และมหาทักษาประจำวัน</p>", unsafe_allow_html=True)

st.divider()

# Main Controls Card
st.markdown("<div class='neon-card border-gold'>", unsafe_allow_html=True)
c_input1, c_input2 = st.columns([1, 1])

with c_input1:
    st.markdown("### 📅 เลือกวัน / เดือน / ปี")
    selected_date = st.date_input(
        "เลือกวันที่ต้องการดูข้อมูล (ย้อนหลังได้ตั้งแต่ พ.ศ. 2493 / ค.ศ. 1950)",
        value=datetime.date.today(),
        min_value=datetime.date(1950, 1, 1),
        max_value=datetime.date(2100, 12, 31)
    )

with c_input2:
    st.markdown("### 🎵 เครื่องเล่นเพลง MP3")
    mp3_files = glob.glob("*.mp3")
    if mp3_files:
        selected_song = st.selectbox("เลือกเพลง MP3 ในโฟลเดอร์หลัก", mp3_files)
        st.audio(selected_song)
    else:
        st.info("💡 นำไฟล์เพลง `.mp3` วางในโฟลเดอร์หลักโฟลเดอร์เดียวกับไฟล์ `.py` เพื่อเล่นเพลงได้ทันที")

# ดึงพิกัด GPS จริงจากมือถือผู้ใช้
st.markdown("---")
st.markdown("<b>📍 พิกัดตำแหน่งจริงจากโทรศัพท์มือถือของคุณ:</b>", unsafe_allow_html=True)
location = get_geolocation()

if location and 'coords' in location:
    lat = location['coords']['latitude']
    lon = location['coords']['longitude']
    st.success(f"เชื่อมต่อพิกัดโทรศัพท์สำเร็จ: ละติจูด {lat:.4f}, ลองจิจูด {lon:.4f}")
    weather_info = get_weather_by_coords(lat, lon)
else:
    lat, lon = 13.7563, 100.5018  # Default พิกัดกรุงเทพฯ
    st.warning("⚠️ หากต้องการรับข้อมูลสภาพอากาศสดตามตำแหน่งของคุณ กรุณากดอนุญาตการเข้าถึง GPS บนโทรศัพท์มือถือ")
    weather_info = get_weather_by_coords(lat, lon)

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 4. Processing Output Data
# ---------------------------------------------------------
year_ce = selected_date.year
year_be = year_ce + 543
month_name = MONTHS_TH[selected_date.month - 1]
day_name = DAYS_TH[selected_date.weekday()]
day_num = selected_date.day

zodiac_animal = get_thai_zodiac_animal(year_ce, selected_date.month, day_num)
zodiac_name, element_name, element_color = get_zodiac_and_element(day_num, selected_date.month)
lunar_day, moon_phase, moon_dist, sun_dist = get_thai_lunar_phase(selected_date)
planet_positions = get_real_planet_positions(selected_date)
energy_score, taksa = get_numerology_and_taksa(selected_date)


# ---------------------------------------------------------
# 5. Full Dashboard Layout Display (หน้าหลักทั้งหมด)
# ---------------------------------------------------------

# Row 1: วันสุริยคติ, ปีนักษัตร, สภาพอากาศ & ราศี, ธาตุ, ค่าพลังงาน
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown(f"""
    <div class="neon-card border-gold">
        <h3 class="text-gold">📆 ข้อมูลวันทางสุริยคติ & ปีนักษัตร</h3>
        <p><b>วันประจำสัปดาห์:</b> <span class="text-gold" style="font-size:1.2em; font-weight:bold;">{day_name}</span></p>
        <p><b>วันที่:</b> {day_num} {month_name}</p>
        <p><b>ปี พ.ศ.:</b> <span class="text-neon-blue">{year_be}</span> | <b>ปี ค.ศ.:</b> <span class="text-neon-blue">{year_ce}</span></p>
        <p><b>ปีนักษัตรไทย:</b> <span class="text-neon-green" style="font-size:1.2em; font-weight:bold;">{zodiac_animal}</span></p>
        <p><b>🌤️ สภาพอากาศสดจริงตามพิกัด:</b> {weather_info}</p>
        <p><b>เวลาอัปเดตระบบปัจจุบัน:</b> {datetime.datetime.now().strftime('%H:%M:%S')} น.</p>
    </div>
    """, unsafe_allow_html=True)

with row1_col2:
    st.markdown(f"""
    <div class="neon-card border-purple">
        <h3 class="text-neon-purple">♈ ราศี ธาตุ & ค่าพลังงานสิริมงคล</h3>
        <p><b>ราศีประจำช่วงวัน:</b> <span style="color:{element_color}; font-weight:bold; font-size:1.18em;">{zodiac_name}</span></p>
        <p><b>ธาตุประจำราศี:</b> {element_name}</p>
        <p><b>ค่าพลังงานสิริมงคลรวมประจำวัน (เลขศาสตร์):</b></p>
        <h2 class="text-neon-green" style="margin:0;">{energy_score} / 100 %</h2>
    </div>
    """, unsafe_allow_html=True)

# Row 2: ดวงจันทร์ (จันทรคติไทย) & ดวงอาทิตย์
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown(f"""
    <div class="neon-card border-blue">
        <h3 class="text-neon-blue">🌙 ข้างขึ้นข้างแรม (ปฏิทินไทย)</h3>
        <p><b>ปฏิทินจันทรคติไทย:</b> <span class="text-neon-blue" style="font-size:1.2em; font-weight:bold;">{lunar_day}</span></p>
        <p><b>ปรากฏการณ์ดวงจันทร์:</b> {moon_phase}</p>
        <p><b>ระยะห่างจากโลกถึงดวงจันทร์:</b> {moon_dist:,} กิโลเมตร</p>
    </div>
    """, unsafe_allow_html=True)

with row2_col2:
    st.markdown(f"""
    <div class="neon-card border-red">
        <h3 class="text-neon-red">☀️ ระยะห่างดวงอาทิตย์</h3>
        <p><b>ระยะห่างจากโลกถึงดวงอาทิตย์:</b> {sun_dist} AU (หน่วยดาราศาสตร์)</p>
        <p><b>คำนวณระยะทางกิโลเมตร:</b> {round(sun_dist * 149597870.7):,} กม.</p>
        <p><b>สถานะพลังงานแสงอาทิตย์:</b> สมบูรณ์ตามตำแหน่งวงโคจรทางดาราศาสตร์</p>
    </div>
    """, unsafe_allow_html=True)

# Row 3: ตำแหน่งและการโคจรของดาวทั้ง 7 ดวง
st.markdown("""
<div class="neon-card border-green">
    <h3 class="text-neon-green">🪐 ตำแหน่งและการโคจรของดาวทั้ง 7 ดวง (คำนวณจริงทางดาราศาสตร์)</h3>
    <p style='color:#aaa; font-size:0.9em; margin-bottom:15px;'>พิกัดการสถิตราศีและองศาของดวงดาวประจำวันที่เลือก</p>
""", unsafe_allow_html=True)

cols_p = st.columns(4)
for idx, (p_name, p_pos) in enumerate(planet_positions):
    with cols_p[idx % 4]:
        st.markdown(f"**{p_name}**  \n<span style='color:#39FF14; font-size:0.95em;'>{p_pos}</span>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Row 4: เลขนำโชค สีมงคล สิ่งที่ควรปฏิบัติ & สิ่งที่ไม่ควรทำ
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
