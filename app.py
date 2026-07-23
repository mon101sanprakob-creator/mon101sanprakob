import streamlit as st
import datetime
import calendar

st.set_page_config(page_title="Date Secrets & Numerology Decrypter", page_icon="🔮", layout="centered")

st.title("🔮 แอปถอดรหัสวันที่ & วิเคราะห์ตัวเลขชะตา")
st.write("กรอก วัน เดือน ปี เพื่อถอดรหัสค่าโหราศาสตร์ จันทรคติไทย เลขศาสตร์ และค้นหาวันที่มีค่าเหมือนกันย้อนหลัง-ล่วงหน้า 50 ปี")

# 1. ส่วนรับอินพุตวันเดือนปี
col1, col2, col3 = st.columns(3)
with col1:
    day = st.number_input("วัน (Day)", min_value=1, max_value=31, value=datetime.date.today().day)
with col2:
    month = st.number_input("เดือน (Month)", min_value=1, max_value=12, value=datetime.date.today().month)
with col3:
    year = st.number_input("ปี ค.ศ. (Year)", min_value=1900, max_value=2100, value=datetime.date.today().year)

# ----------------- ฟังก์ชันคำนวณค่าพิเศษ ----------------- #

def get_zodiac(d, m):
    """คำนวณราศีตามวันที่"""
    zodiacs = [
        (1, 20, "มังกร (Capricorn) ♑"), (2, 19, "กุมภ์ (Aquarius) ♒"),
        (3, 21, "มีน (Pisces) ♓"), (4, 20, "เมษ (Aries) ♈"),
        (5, 21, "พฤษภ (Taurus) ♉"), (6, 21, "เมถุน (Gemini) ♊"),
        (7, 23, "กรกฎ (Cancer) ♋"), (8, 23, "สิงห์ (Leo) ♌"),
        (9, 23, "กันย์ (Virgo) ♍"), (10, 23, "ตุลย์ (Libra) ♎"),
        (11, 22, "พิจิก (Scorpio) ♏"), (12, 22, "ธนู (Sagittarius) ♐"),
        (12, 31, "มังกร (Capricorn) ♑")
    ]
    for month_end, day_end, name in zodiacs:
        if m < month_end or (m == month_end and d <= day_end):
            return name
    return "มังกร (Capricorn) ♑"

def get_zodiac_animal(y):
    """คำนวณปีนักษัตร"""
    animals = ["วอก (ลิง)", "ระกา (ไก่)", "จอ (หมา)", "กุน (หมู)", "ชวด (หนู)", "ฉลู (วัว)",
               "ขาล (เสือ)", "เถาะ (กระต่าย)", "มะโรง (งูใหญ่)", "มะเส็ง (งูเล็ก)", "มะเมีย (ม้า)", "มะเมีย (แพะ)"]
    return animals[y % 12]

def get_moon_phase(target_date):
    """คำนวณข้างขึ้น/ข้างแรมอย่างง่ายโดยประมาณ"""
    # ใช้วันอ้างอิง New Moon: 2000-01-06
    diff = (target_date - datetime.date(2000, 1, 6)).days
    lunar_cycle = 29.53058867
    phase = (diff % lunar_cycle) / lunar_cycle
    
    day_in_cycle = int(phase * 29.53)
    if day_in_cycle < 15:
        phase_str = f"ขึ้น {day_in_cycle + 1} ค่ำ 🌓 (สว่างประมาณ {int(phase*200)}%)"
    else:
        phase_str = f"แรม {day_in_cycle - 14} ค่ำ 🌗 (สว่างประมาณ {int((1-phase)*200)}%)"
    return phase_str

def calculate_life_path(d, m, y):
    """คำนวณเลขศาสตร์รวม (Life Path Number)"""
    digits = f"{d}{m}{y}"
    total = sum(int(digit) for digit in digits)
    while total > 9 and total not in [11, 22, 33]: # เว้นเลข Master Numbers
        total = sum(int(digit) for digit in str(total))
    return total

def get_day_power(weekday_index):
    """คำนวณเลขกำลังวันประจำวันเกิด"""
    powers = [15, 8, 17, 19, 21, 12, 6] # จันทร์=15, อังคาร=8, พุธ=17, พฤหัส=19, ศุกร์=21, เสาร์=12, อาทิตย์=6
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    return day_names[weekday_index], powers[weekday_index]

# ----------------- ปุ่มเริ่มคำนวณ ----------------- #

if st.button("🔮 ถอดรหัสชะตาและคำนวณค่าทั้งหมด"):
    try:
        target_date = datetime.date(year, month, day)
        day_name, day_power = get_day_power(target_date.weekday())
        year_th = year + 543
        zodiac = get_zodiac(day, month)
        zodiac_animal = get_zodiac_animal(year)
        moon_phase = get_moon_phase(target_date)
        life_path = calculate_life_path(day, month, year)
        day_of_year = target_date.timetuple().tm_yday
        is_leap = calendar.isleap(year)

        st.markdown("---")
        st.header(f"✨ ผลลัพธ์การถอดรหัส: {day} / {month} / {year} (พ.ศ. {year_th})")
        st.subheader(f"🗓️ ตรงกับ: **วัน{day_name}**")

        # แสดงผลแบบกล่องการ์ดสวยงาม
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.info(f"""
            **🌌 ค่าทางโหราศาสตร์ & ปฏิทิน**
            * **ปีนักษัตร:** ปี{zodiac_animal}
            * **ราศี:** {zodiac}
            * **ข้างขึ้น/ข้างแรม:** {moon_phase}
            * **ลำดับวันในรอบปี:** วันที่ {day_of_year} จาก 365/366 วัน
            * **สถานะปีอธิกสุรทิน:** {'มี 29 ก.พ. (ปีอธิกสุรทิน)' if is_leap else 'ปกติ (28 ก.พ.)'}
            """)

        with col_b:
            st.success(f"""
            **ต ถอดรหัสตัวเลขศาสตร์ (Numerology)**
            * **เลขกำลังวันประจำวัน{day_name}:**  `{day_power}`
            * **เลขศาสตร์รวมชะตา (Life Path Number):**  `{life_path}`
            * **โค้ดรหัสวันที่ (Date Code):** `{day:02d}{month:02d}{year}`
            * **รวมรหัสตัวเลขแบบโดด:** `{sum(int(digit) for digit in f'{day}{month}{year}')}`
            """)

        st.markdown("---")
        
        # ----------------- ค้นหาวันที่มีค่าตรงกัน 100 ปี ----------------- #
        st.subheader("🎯 ค้นหาวันที่มีชะตาตรงกันเป๊ะ (ย้อนหลัง 50 ปี - ล่วงหน้า 50 ปี)")
        
        start_year = year - 50
        end_year = year + 50
        matching_dates = []
        
        for y in range(start_year, end_year + 1):
            if y == year:
                continue
            try:
                check_date = datetime.date(y, month, day)
                # เงื่อนไข: วันในสัปดาห์ตรงกัน + ราศีเดียวกัน
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
