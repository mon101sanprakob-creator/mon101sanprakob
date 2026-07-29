import streamlit as st
import datetime
import calendar
import random
import os
import glob

# ---------------------------------------------------------
# 1. Page Configuration & Custom CSS (Neon Dark Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Personal Astro Calendar",
    page_icon="📅",
    layout="wide"
)

# Custom CSS ตกแต่งพื้นหลังดำเงา (Glossy Black) และโทนสีตามระบุ
st.markdown("""
<style>
    /* Background & Main Layout */
    .stApp {
        background: radial-gradient(circle, #1a1a1a 0%, #050505 100%);
        color: #ffffff;
        font-family: 'Sarabun', sans-serif;
    }
    
    /* Neon Glow Custom Cards */
    .neon-card {
        background-color: rgba(15, 15, 20, 0.85);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(5px);
    }
    
    /* Neon Borders for Visual Variety */
    .border-gold { border-left: 5px solid #FFD700; box-shadow: -2px 0 10px rgba(255, 215, 0, 0.3); }
    .border-red { border-left: 5px solid #FF3366; box-shadow: -2px 0 10px rgba(255, 51, 102, 0.3); }
    .border-blue { border-left: 5px solid #00F0FF; box-shadow: -2px 0 10px rgba(0, 240, 255, 0.3); }
    .border-green { border-left: 5px solid #39FF14; box-shadow: -2px 0 10px rgba(57, 255, 20, 0.3); }
    .border-purple { border-left: 5px solid #BF00FF; box-shadow: -2px 0 10px rgba(191, 0, 255, 0.3); }
    
    /* Neon Text Highlights */
    .text-gold { color: #FFD700; text-shadow: 0 0 8px rgba(255, 215, 0, 0.6); }
    .text-neon-blue { color: #00F0FF; text-shadow: 0 0 8px rgba(0, 240, 255, 0.6); }
    .text-neon-green { color: #39FF14; text-shadow: 0 0 8px rgba(57, 255, 20, 0.6); }
    .text-neon-red { color: #FF3366; text-shadow: 0 0 8px rgba(255, 51, 102, 0.6); }
    .text-neon-purple { color: #BF00FF; text-shadow: 0 0 8px rgba(191, 0, 255, 0.6); }
    
    /* Header Styling */
    h1, h2, h3 {
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. Helper Calculation Functions
# ---------------------------------------------------------
DAYS_TH = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
MONTHS_TH = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def get_zodiac_and_element(day, month):
    """คำนวณราศีและธาตุประจำช่วงวันเกิด/วันที่เลือก"""
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

def get_lunar_phase(date_obj):
    """คำนวณระยะดวงจันทร์และข้างขึ้นข้างแรมแบบประมาณการณ์"""
    diff_days = (date_obj - datetime.date(2000, 1, 6)).days
    moon_age = diff_days % 29.53058867
    
    if moon_age < 1.84566:
        phase = "จันทร์ดับ (New Moon) 🌑"
        lunar_day = "แรม 15 ค่ำ"
    elif moon_age < 5.53699:
        phase = "จันทร์เสี้ยวขึ้น (Waxing Crescent) 🌒"
        lunar_day = f"ขึ้น {int(moon_age * 2.8) + 1} ค่ำ"
    elif moon_age < 9.22831:
        phase = "จันทร์ครึ่งดวงขึ้น (First Quarter) 🌓"
        lunar_day = "ขึ้น 8 ค่ำ"
    elif moon_age < 12.91963:
        phase = "จันทร์เกือบเต็มดวง (Waxing Gibbous) 🌔"
        lunar_day = f"ขึ้น {int(moon_age * 1.1) + 7} ค่ำ"
    elif moon_age < 16.61096:
        phase = "จันทร์เพ็ญ (Full Moon) 🌕"
        lunar_day = "ขึ้น 15 ค่ำ"
    elif moon_age < 20.30228:
        phase = "จันทร์เกือบเต็มดวงแรม (Waning Gibbous) 🌖"
        lunar_day = f"แรม {int((moon_age - 15) * 1.1) + 1} ค่ำ"
    elif moon_age < 23.99361:
        phase = "จันทร์ครึ่งดวงแรม (Third Quarter) 🌗"
        lunar_day = "แรม 8 ค่ำ"
    else:
        phase = "จันทร์เสี้ยวแรม (Waning Crescent) 🌘"
        lunar_day = f"แรม {int((moon_age - 22) * 2.8) + 8} ค่ำ"
        
    distance_km = 363300 + (384400 - 363300) * (1 - abs((moon_age - 14.7) / 14.7))
    return phase, lunar_day, round(distance_km, -2)

def get_astronomical_positions(date_obj):
    """สถิติตำแหน่งการย้ายและการโคจรของดาวทั้ง 7 วันนั้น"""
    seed_val = date_obj.year * 10000 + date_obj.month * 100 + date_obj.day
    random.seed(seed_val)
    
    planets = [
        ("อาทิตย์ (1)", "สถิตราศีเมษ องศาที่ " + str(random.randint(1, 29))),
        ("จันทร์ (2)", "โคจรเข้าสู่ภพตนุ ทับลัคนา"),
        ("อังคาร (3)", "ย้ายเข้าสู่เรือนการเงิน (เดินหน้าปกติ)"),
        ("พุธ (4)", "โคจรพักรนกรรถ์ สถิตราศีเมถุน"),
        ("พฤหัสบดี (5)", "มหาอุจจ์ โคจรเสริดในราศีกรกฎ"),
        ("ศุกร์ (6)", "สถิตราศีพฤษภ ได้ตำแหน่งเกษตราธิบดี"),
        ("เสาร์ (7)", "สถิตราศีกุมภ์ โคจรเป็นนิจ")
    ]
    
    sun_dist_au = 0.983 + (1.017 - 0.983) * abs((date_obj.timetuple().tm_yday - 3) / 182.5)
    return planets, round(sun_dist_au, 4)

def get_energy_score(date_obj):
    """คำนวณค่าพลังงานรวมสิริมงคลของวัน"""
    seed_val = date_obj.year + date_obj.month + date_obj.day
    random.seed(seed_val)
    return random.randint(65, 99)


# ---------------------------------------------------------
# 3. Sidebar (Logo, Input Date, Music Player)
# ---------------------------------------------------------
with st.sidebar:
    # 3.1 Show Logo
    if os.path.exists("logo1.png"):
        st.image("logo1.png", use_container_width=True)
    else:
        st.markdown("<h2 class='text-gold' style='text-align:center;'>🌌 ASTRO CALENDAR</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    # 3.2 Date Input
    st.markdown("### 📅 เลือกวัน เดือน ปี")
    selected_date = st.date_input("เลือกวันที่ต้องการดูข้อมูล", datetime.date.today())
    
    st.divider()
    
    # 3.3 Music Player (mp3 in same folder)
    st.markdown("### 🎵 เครื่องเล่นเพลง")
    mp3_files = glob.glob("*.mp3")
    if mp3_files:
        selected_song = st.selectbox("เลือกเพลง MP3", mp3_files)
        st.audio(selected_song)
    else:
        st.caption("⚠️ ไม่พบไฟล์ .mp3 ในโฟลเดอร์เดียวกัน")


# ---------------------------------------------------------
# 4. Main Display Calculation
# ---------------------------------------------------------
year_ce = selected_date.year
year_be = year_ce + 543
month_name = MONTHS_TH[selected_date.month - 1]
day_name = DAYS_TH[selected_date.weekday()]
day_num = selected_date.day

zodiac_name, element_name, element_color = get_zodiac_and_element(day_num, selected_date.month)
moon_phase, lunar_day, moon_dist = get_lunar_phase(selected_date)
planet_positions, sun_dist = get_astronomical_positions(selected_date)
energy_score = get_energy_score(selected_date)

# Lucky numbers & Advice generation
random.seed(selected_date.year * 1000 + selected_date.month * 100 + selected_date.day)
lucky_nums = sorted(random.sample(range(0, 10), 3))
lucky_color = random.choice(["แดงนีออน", "เขียวนีออน", "ม่วงนีออน", "น้ำเงินนีออน", "ทองคำ"])

dos = [
    "เจรจาติดต่อธุรกิจ หรืองานที่ใช้ความคิดสร้างสรรค์",
    "ทำบุญ ถวายสังฆทาน เสริมดวงชะตา",
    "จัดโต๊ะทำงานใหม่ เปิดรับพลังงานบวก",
    "เริ่มต้นเรียนรู้ทักษะใหม่ๆ หรือลงมือทำโครงการใหม่",
    "ออกกำลังกายกลางแจ้งเพื่อรับพลังงานจากธรรมชาติ"
]

donts = [
    "การเซ็นสัญญาหรือเอกสารสำคัญโดยไม่ตรวจสอบอย่างรอบคอบ",
    "หลีกเลี่ยงการใช้อารมณ์ตัดสินปัญหา หรือโต้เถียงในเรื่องไม่เป็นเรื่อง",
    "ให้ผู้อื่นยืมเงิน หรือลงทุนในความเสี่ยงสูง",
    "เดินทางไกลในช่วงยามวิกาลหากไม่จำเป็น",
    "ตัดไม้ใหญ่ หรือการซ่อมแซมใหญ่ในบ้าน"
]

current_do = random.choice(dos)
current_dont = random.choice(donts)

# ---------------------------------------------------------
# 5. Dashboard Layout Render
# ---------------------------------------------------------
st.markdown(f"<h1 style='text-align: center;' class='text-gold'>✨ ปฏิทินพลังงานดาวประจำวัน ✨</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #aaa;'>ประจำวัน {day_name} ที่ {day_num} {month_name} พ.ศ. {year_be} (ค.ศ. {year_ce})</p>", unsafe_allow_html=True)

st.write("")

# Row 1: General Info & Zodiac/Element
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="neon-card border-gold">
        <h3 class="text-gold">📆 วัน เดือน ปี (สุริยคติ)</h3>
        <p><b>วันประจำสัปดาห์:</b> <span class="text-gold">{day_name}</span></p>
        <p><b>เดือน:</b> {month_name} (เดือนที่ {selected_date.month})</p>
        <p><b>ปี พ.ศ.:</b> {year_be} | <b>ปี ค.ศ.:</b> {year_ce}</p>
        <p><b>เวลาอัปเดตระบบ:</b> {datetime.datetime.now().strftime('%H:%M:%S')} น.</p>
        <p><b>สภาพอากาศจำลอง:</b> ท้องฟ้าเปิด เหมาะแก่การดูดาว (28°C)</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="neon-card border-purple">
        <h3 class="text-neon-purple">♈ จักรราศี & ธาตุประจำวัน</h3>
        <p><b>ราศีประจำช่วงเวลา:</b> <span style="color:{element_color}; font-weight:bold;">{zodiac_name}</span></p>
        <p><b>ธาตุประจำราศี:</b> {element_name}</p>
        <p><b>ค่าพลังงานสิริมงคลรวมประจำวัน:</b></p>
        <h2 class="text-neon-green" style="margin:0;">{energy_score} / 100 %</h2>
    </div>
    """, unsafe_allow_html=True)

# Row 2: Lunar & Astronomical Solar Distances
col3, col4 = st.columns(2)

with col3:
    st.markdown(f"""
    <div class="neon-card border-blue">
        <h3 class="text-neon-blue">🌙 ข้างขึ้นข้างแรม & ดวงจันทร์</h3>
        <p><b>ปฏิทินจันทรคติไทย:</b> <span class="text-neon-blue">{lunar_day}</span></p>
        <p><b>ปรากฏการณ์ดวงจันทร์:</b> {moon_phase}</p>
        <p><b>ระยะห่างจากโลก:</b> ประมาณ {moon_dist:,} กิโลเมตร</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="neon-card border-red">
        <h3 class="text-neon-red">☀️ ระยะดวงอาทิตย์</h3>
        <p><b>ระยะห่างจากโลกถึงดวงอาทิตย์:</b> {sun_dist} AU (หน่วยดาราศาสตร์)</p>
        <p><b>ทิศทางพลังงานแสงอาทิตย์:</b> สมบูรณ์ มีกำลังส่งผลต่อธาตุประจำวัน</p>
    </div>
    """, unsafe_allow_html=True)

# Row 3: Planet Motion (7 Planets)
st.markdown("""
<div class="neon-card border-green">
    <h3 class="text-neon-green">🪐 ตำแหน่งและการเคลื่อนย้ายของดาวทั้ง 7</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
""", unsafe_allow_html=True)

cols_p = st.columns(4)
for idx, (p_name, p_pos) in enumerate(planet_positions):
    with cols_p[idx % 4]:
        st.markdown(f"**{p_name}**  \n<span style='color:#ccc; font-size:0.9em;'>{p_pos}</span>", unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# Row 4: Lucky Numbers, Colors, Dos & Donts
st.markdown(f"""
<div class="neon-card border-gold">
    <h3 class="text-gold">🔮 เลขนำโชค ข้อปฏิบัติ และข้อควรระวัง</h3>
    <div style="display: flex; flex-wrap: wrap; justify-content: space-between;">
        <div style="flex: 1; min-width: 250px;">
            <p><b>เลขนำโชคประจำวัน:</b> <span class="text-neon-green" style="font-size: 1.3em; font-weight:bold;">{lucky_nums[0]}, {lucky_nums[1]}, {lucky_nums[2]}</span></p>
            <p><b>สีมงคลเสริมพลัง:</b> <span class="text-gold">{lucky_color}</span></p>
        </div>
        <div style="flex: 2; min-width: 300px;">
            <p><span class="text-neon-green"><b>✅ สิ่งที่ควรปฏิบัติ:</b></span> {current_do}</p>
            <p><span class="text-neon-red"><b>❌ สิ่งที่ไม่ควรทำ:</b></span> {current_dont}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
