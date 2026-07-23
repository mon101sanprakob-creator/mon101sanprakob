import streamlit as st
import datetime
import calendar

st.set_page_config(page_title="Date Secrets & Astrology Engine", page_icon="🔮", layout="centered")

st.title("🔮 แอปถอดรหัสดวงชะตา & คำนวณตำแหน่งดวงดาว")
st.write("กรอกวันเดือนปี เพื่อถอดรหัสตำแหน่งดวงดาวทางโหราศาสตร์ เลขศาสตร์ และค้นหาวันที่มีค่าเหมือนกันย้อนหลัง-ล่วงหน้า 50 ปี")

# 1. ส่วนรับอินพุตวันเดือนปี
col1, col2, col3 = st.columns(3)
with col1:
    day = st.number_input("วัน (Day)", min_value=1, max_value=31, value=datetime.date.today().day)
with col2:
    month = st.number_input("เดือน (Month)", min_value=1, max_value=12, value=datetime.date.today().month)
with col3:
    year = st.number_input("ปี ค.ศ. (Year)", min_value=1900, max_value=2100, value=datetime.date.today().year)

# ----------------- ฟังก์ชันคำนวณตำแหน่งดวงดาว & โหราศาสตร์ ----------------- #

ZODIAC_NAMES = [
    "ราศีเมษ ♈", "ราศีพฤษภ ♉", "ราศีเมถุน ♊", "ราศีกรกฎ ♋",
    "ราศีสิงห์ ♌", "ราศีกันย์ ♍", "ราศีตุลย์ ♎", "ราศีพิจิก ♏",
    "ราศีธนู ♐", "ราศีมังกร ♑", "ราศีกุมภ์ ♒", "ราศีมีน ♓"
]

def get_zodiac(d, m):
    """ราศีตามอาทิตย์ยก (Sun Sign)"""
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
    """ปีนักษัตร"""
    animals = ["วอก (ลิง)", "ระกา (ไก่)", "จอ (หมา)", "กุน (หมู)", "ชวด (หนู)", "ฉลู (วัว)",
               "ขาล (เสือ)", "เถาะ (กระต่าย)", "มะโรง (งูใหญ่)", "มะเส็ง (งูเล็ก)", "มะเมีย (ม้า)", "มะเมีย (แพะ)"]
    return animals[y % 12]

def calculate_planetary_positions(target_date):
    """คำนวณตำแหน่งดวงดาวหลักทางโหราศาสตร์แบบประมาณการตามสมการดาราศาสตร์"""
    days_since_2000 = (target_date - datetime.date(2000, 1, 1)).days
    
    # รอบการโคจรของดาวแต่ละดวง (จำนวนวันต่อ 1 รอบวงกว้าง)
    sun_pos = int(((days_since_2000 % 365.25) / 365.25) * 12)
    moon_pos = int(((days_since_2000 % 27.32) / 27.32) * 12)
    mercury_pos = int(((days_since_2000 % 87.97) / 87.97) * 12)
    venus_pos = int(((days_since_2000 % 224.7) / 224.7) * 12)
    mars_pos = int(((days_since_2000 % 686.98) / 686.98) * 12)
    jupiter_pos = int(((days_since_2000 % 4332.59) / 4332.59) * 12)
    saturn_pos = int(((days_since_2000 % 10759.22) / 10759.22) * 12)
    
    planets = [
        {"ดาว": "☀️ ดาวอาทิตย์ (1)", "ตำแหน่ง": ZODIAC_NAMES[sun_pos], "ความหมาย": "ตัวตน พลังชีวิต และความมุ่งมั่น"},
        {"ดาว": "🌙 ดาวจันทร์ (2)", "ตำแหน่ง": ZODIAC_NAMES[moon_pos], "ความหมาย": "อารมณ์ จิตใต้สำนึก และความรู้สึก"},
        {"ดาว": "☿ ดาวพุธ (4)", "ตำแหน่ง": ZODIAC_NAMES[mercury_pos], "ความหมาย": "การสื่อสาร สติปัญญา และเจรจา"},
        {"ดาว": "♀ ดาวศุกร์ (6)", "ตำแหน่ง": ZODIAC_NAMES[venus_pos], "ความหมาย": "ความรัก เสน่ห์ และโชคลาภเงินทอง"},
        {"ดาว": "♂ ดาวอังคาร (3)", "ตำแหน่ง": ZODIAC_NAMES[mars_pos], "ความหมาย": "ความขยัน กล้าหาญ และพลังการต่อสู้"},
        {"ดาว": "♃ ดาวพฤหัสบดี (5)", "ตำแหน่ง": ZODIAC_NAMES[jupiter_pos], "ความหมาย": "ผู้ใหญ่เมตตา คุณธรรม และความสำเร็จ"},
        {"ดาว": "♄ ดาวเสาร์ (7)", "ตำแหน่ง": ZODIAC_NAMES[saturn_pos], "ความหมาย": "ความอดทน บทเรียนชีวิต และความมั่นคง"}
    ]
    return planets

def get_moon_phase(target_date):
    diff = (target_date - datetime.date(2000, 1, 6)).days
    lunar_cycle = 29.53058867
    phase = (diff % lunar_cycle) / lunar_cycle
    day_in_cycle = int(phase * 29.53)
    
    if day_in_cycle < 15:
        return f"ขึ้น {day_in_cycle + 1} ค่ำ 🌓 (สว่าง {int(phase*200)}%)"
    else:
        return f"แรม {day_in_cycle - 14} ค่ำ 🌗 (สว่าง {int((1-phase)*200)}%)"

def calculate_life_path(d, m, y):
    digits = f"{d}{m}{y}"
    total = sum(int(digit) for digit in digits)
    while total > 9 and total not in [11, 22, 33]:
        total = sum(int(digit) for digit in str(total))
    return total

def get_day_power(weekday_index):
    powers = [15, 8, 17, 19, 21, 12, 6]
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    return day_names[weekday_index], powers[weekday_index]

# ----------------- เริ่มการประมวลผล ----------------- #

if st.button("🔮 ถอดรหัสผูกดวง & คำนวณตำแหน่งดวงดาว"):
    try:
        target_date = datetime.date(year, month, day)
        day_name, day_power = get_day_power(target_date.weekday())
        year_th = year + 543
        zodiac = get_zodiac(day, month)
        zodiac_animal = get_zodiac_animal(year)
        moon_phase = get_moon_phase(target_date)
        life_path = calculate_life_path(day, month, year)
        planet_data = calculate_planetary_positions(target_date)

        st.markdown("---")
        st.header(f"✨ แผ่นผูกดวงชะตา: {day} / {month} / {year} (พ.ศ. {year_th})")
        st.subheader(f"🗓️ เจ้าชะตากำเนิด: **วัน{day_name}** | ปี{zodiac_animal}")

        # กล่องสรุปค่าหลัก
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("ราศีประจำตัว", zodiac)
        with c2:
            st.metric("เลขกำลังวัน", day_power)
        with c3:
            st.metric("เลขชะตาลิขิต (Life Path)", life_path)

        st.info(f"🌙 **สภาวะดวงจันทร์ (ข้างขึ้น/ข้างแรม):** {moon_phase}")

        st.markdown("---")
        st.subheader("🪐 ตารางตำแหน่งดวงดาวประทับราศี (Astro Planetary Map)")
        st.write("ตำแหน่งของดาวเคราะห์สำคัญในสถิตราศีขณะนั้น:")
        
        # แสดงตารางตำแหน่งดาว
        st.dataframe(planet_data, use_container_width=True)

        st.markdown("---")
        
        # ----------------- ค้นหาวันที่มีค่าดวงดาวตรงกัน 100 ปี ----------------- #
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
