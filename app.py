import streamlit as st
import sys
import os
from datetime import datetime

# บังคับให้ Python มองเห็น Root Path เสมอ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# นำเข้าค่าคงที่และ Engine (อ้างอิงตาม constants.py อันที่คุณยุบรวมแล้ว)
from engine.constants import WEEKDAYS, MONTHS, ZODIAC, COLOR_PALETTE, ENTERTAINMENT_DISCLAIMER
from engine.synapse_engine import SynapseEngine

# ==========================================================
# HELPER FUNCTIONS FOR CONVERSION (แปลงเป็นค่าที่ Engine ชุดเดิมต้องการ)
# ==========================================================
def get_lunar_phase_day(target_date):
    """คำนวณดิถีดวงจันทร์ (1-30 วัน)"""
    base_date = datetime(2000, 1, 6) # วันจันทร์ดับอ้างอิง
    diff_days = (target_date - base_date).days
    lunar_age = diff_days % 29.530588
    lunar_day = int(lunar_age) + 1
    return min(max(lunar_day, 1), 30)

def get_thai_zodiac_year(year):
    """แปลงปี ค.ศ. เป็นปีนักษัตรไทย (ชวด, ฉลู, ขาล...) ตามที่คีย์ ZODIAC กำหนด"""
    # ปี ค.ศ. 2000 คือปีมะโรง (ลำดับที่ 5 ใน ZODIAC ของคุณ)
    zodiac_order = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
    base_year = 2000
    index = (year - base_year + 4) % 12
    return zodiac_order[index]

# ==========================================================
# CONFIGURATION & INITIALIZATION
# ==========================================================
st.set_page_config(page_title="SYNAPSE ENGINE", layout="centered")
st.title("🧠 SYNAPSE ENGINE")
st.caption("Sound & Visual Therapy - Entertainment & Data Exploration")

st.info(ENTERTAINMENT_DISCLAIMER)
st.markdown("---")

# ==========================================================
# INPUT SECTION (กรอกแค่วันเดือนปีจบเลย)
# ==========================================================
st.subheader("📅 กรอกข้อมูลวันเกิดเพื่อวิเคราะห์สัญญาณ")

selected_date = st.date_input(
    "เลือก วัน/เดือน/ปี ค.ศ. เกิดของคุณ:",
    value=datetime(2000, 1, 1),
    min_value=datetime(1900, 1, 1),
    max_value=datetime(2026, 12, 31)
)

st.markdown("---")

# ==========================================================
# PROCESSING & OUTPUT SECTION
# ==========================================================
if st.button("🚀 เริ่มต้นระบบคำนวณและซิงค์สัญญาณ", use_container_width=True):
    with st.spinner("กำลังถอดรหัสและประมวลผลข้อมูล..."):
        try:
            # 1. แปลงวันที่เป็น "วันภาษาไทย" ให้ตรงกับคีย์ใน WEEKDAYS (อาทิตย์ - เสาร์)
            thai_weekdays = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
            auto_weekday = thai_weekdays[selected_date.weekday()]
            
            # 2. แปลงเป็น "เดือนภาษาไทย" ให้ตรงกับคีย์ใน MONTHS (มกราคม - ธันวาคม)
            thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
                           "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
            auto_month = thai_months[selected_date.month - 1]
            
            # 3. แปลงปีเกิดเป็น "ปีนักษัตรภาษาไทย" ให้ตรงกับคีย์ใน ZODIAC (ชวด - กุน)
            auto_zodiac = get_thai_zodiac_year(selected_date.year)
            
            # 4. คำนวณดิถีดวงจันทร์ (1-30)
            datetime_obj = datetime(selected_date.year, selected_date.month, selected_date.day)
            auto_lunar = get_lunar_phase_day(datetime_obj)
            
            # --- เรียกใช้งาน SynapseEngine ตัวเดิมของคุณเป๊ะๆ ---
            # โครงสร้างเดิมต้องการ: weekday, month, zodiac, lunar (ไม่มี birth_year มารบกวน)
            engine = SynapseEngine()
            result = engine.calculate(
                weekday=auto_weekday,
                month=auto_month,
                zodiac=auto_zodiac,
                lunar=auto_lunar
            )
            
            st.success("✨ ประมวลผลและแปลงสัญญาณเสร็จสิ้น!")
            
            # ดึงค่าสีจาก COLOR_PALETTE
            bg_color = COLOR_PALETTE.get('SURFACE', '#1a1c23')
            primary_color = COLOR_PALETTE.get('PRIMARY', '#00ccff')
            text_color = COLOR_PALETTE.get('TEXT_LIGHT', '#ffffff')
            secondary_color = COLOR_PALETTE.get('SECONDARY', '#00ff99')
            
            recommended_freq = result.get('analysis', {}).get('recommended_frequency_hz', 0)
            
            # แสดงค่าทั้งหมดที่ระบบคำนวณและแปลงออกมาให้
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; border-left: 5px solid {primary_color};">
                <h4 style="color: {primary_color}; margin-top:0;">📡 สรุปสัญญาณ SYNAPSE จากวันเกิด</h4>
                <p style="color: {text_color};"><b>วันเกิด:</b> วัน{auto_weekday} ที่ {selected_date.day} {auto_month} ค.ศ. {selected_date.year}</p>
                <p style="color: {text_color};"><b>ปีนักษัตร (Zodiac):</b> ปี{auto_zodiac}</p>
                <p style="color: {text_color};"><b>ระดับดิถีดวงจันทร์ (Lunar Phase):</b> ประมาณวันที่ {auto_lunar} ของเดือนจันทรคติ</p>
                <hr style="border-color: #333;">
                <p style="color: {secondary_color}; font-size: 18px;"><b>ความถี่ที่แนะนำ:</b> {recommended_freq} Hz</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            
            # แสดงข้อมูล JSON
            with st.expander("🔍 ดูข้อมูลโครงสร้างสัญญาณระบบ (JSON Metadata)"):
                st.json({
                    "inputs_parsed_to_engine": {
                        "weekday": auto_weekday,
                        "month": auto_month,
                        "zodiac": auto_zodiac,
                        "lunar": auto_lunar
                    },
                    "engine_result": result
                })
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในระบบ Engine: {str(e)}")
            st.info("โปรดตรวจสอบความสอดคล้องของตัวแปรใน engine/synapse_engine.py หรือลอง Reboot App")
