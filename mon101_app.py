import streamlit as st
from PIL import Image
import math
from engine.math_engine import MathEngine
from engine.calendar_engine import CalendarEngine
from engine.lunar_engine import LunarEngine
# ----------------------------
# PAGE
# ----------------------------

st.set_page_config(
    page_title="SYNAPSE",
    page_icon="🧠",
    layout="wide"
)

# ----------------------------
# CONSTANT
# ----------------------------

PHI = 1.61803398875
MOON = 29.530588

DAY = {
    "อาทิตย์": 1,
    "จันทร์": 2,
    "อังคาร": 3,
    "พุธ": 4,
    "พฤหัส": 5,
    "ศุกร์": 6,
    "เสาร์": 7
}

MONTH = {
    "มกราคม":1,
    "กุมภาพันธ์":2,
    "มีนาคม":3,
    "เมษายน":4,
    "พฤษภาคม":5,
    "มิถุนายน":6,
    "กรกฎาคม":7,
    "สิงหาคม":8,
    "กันยายน":9,
    "ตุลาคม":10,
    "พฤศจิกายน":11,
    "ธันวาคม":12
}

ZODIAC = {
    "ชวด":1,
    "ฉลู":2,
    "ขาล":3,
    "เถาะ":4,
    "มะโรง":5,
    "มะเส็ง":6,
    "มะเมีย":7,
    "มะแม":8,
    "วอก":9,
    "ระกา":10,
    "จอ":11,
    "กุน":12
}

# ----------------------------
# LOGO
# ----------------------------

try:
    image = Image.open("logo1.png")
    st.image(image, width=260)
except:
    st.warning("ไม่พบไฟล์ logo1.png")

st.markdown(
"<h1 style='text-align:center;color:gold;'>SYNAPSE</h1>",
unsafe_allow_html=True
)

st.markdown(
"<h3 style='text-align:center;color:#00FFFF;'>SOUND & VISUAL THERAPY</h3>",
unsafe_allow_html=True
)

st.markdown(
"<h4 style='text-align:center;color:white;'>อยู่นิ้งๆไม่เจ็บตัว</h4>",
unsafe_allow_html=True
)

st.divider()

# ----------------------------
# INPUT
# ----------------------------

day = st.selectbox("วัน", list(DAY.keys()))

month = st.selectbox("เดือน", list(MONTH.keys()))

zodiac = st.selectbox("ปีนักษัตร", list(ZODIAC.keys()))

moon_side = st.radio("ข้าง", ["ขึ้น", "แรม"])

moon_day = st.slider("ค่ำ",1,15,1)

# ----------------------------
# BUTTON
# ----------------------------

if st.button("🚀 CALCULATE"):

    d = DAY[day]
    m = MONTH[month]
    z = ZODIAC[zodiac]

    if moon_side=="ขึ้น":
        l = moon_day
    else:
        l = moon_day + 15

    day_weight = d * PHI

    month_weight = m * MOON

    zodiac_weight = z * (PHI**2)

    lunar_weight = l * math.sqrt(PHI)

    total = day_weight + month_weight + zodiac_weight + lunar_weight

    energy = total % 100

    root = sum(int(x) for x in str(int(total)))

    st.success("คำนวณสำเร็จ")

    c1,c2,c3 = st.columns(3)

    c1.metric("Synapse Value",round(total,6))
    c2.metric("Energy",f"{energy:.2f}%")
    c3.metric("Root",root)

    st.divider()

    st.subheader("รายละเอียด")

    st.write(f"วัน : {d} × {PHI} = {day_weight:.6f}")

    st.write(f"เดือน : {m} × {MOON} = {month_weight:.6f}")

    st.write(f"ปีนักษัตร : {z} × φ² = {zodiac_weight:.6f}")

    st.write(f"ข้างขึ้น/แรม : {l} × √φ = {lunar_weight:.6f}")

    st.write("---")

    st.write(f"ผลรวม = {total:.6f}")

    st.info("""
Golden Ratio = 1.61803398875

Moon Cycle = 29.530588

สูตรนี้เป็น SYNAPSE Mathematical Engine
ซึ่งเป็นแบบจำลองที่ผสมข้อมูลวันเกิดกับค่าคงที่ทางคณิตศาสตร์และดาราศาสตร์
""")
