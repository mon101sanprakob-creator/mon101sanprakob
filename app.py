import streamlit as st
import sys
import os
from datetime import datetime

# บังคับให้ Python มองเห็น Root Path เสมอ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# นำเข้าค่าคงที่และ Engine จากไฟล์ระบบ
from engine.constants import WEEKDAYS_TH, MONTHS, ZODIAC, COLOR_PALETTE, ENTERTAINMENT_DISCLAIMER
from engine.synapse_engine import SynapseEngine

# ==========================================================
# HELPER FUNCTIONS FOR CONVERSION
# ==========================================================
def get_lunar_phase_day(target_date):
    """คำนวณดิถีดวงจันทร์ (1-30 วันรอบจันทรคติ) คืนค่าเป็นตัวเลข Integer"""
    base_date = datetime(2000, 1, 6)  # วันจันทร์ดับอ้างอิง
    diff_days = (target_date - base_date).days
    lunar_age = diff_days % 29.530588
    lunar_day = int(lunar_age) + 1
    return min(max(lunar_day, 1), 30)

def get_thai_zodiac_code(year):
    """แปลงปี ค.ศ. เกิดให้กลายเป็นรหัสตัวเลขปีนักษัตรไทย (1-12)"""
    zodiac_order = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
    base_year = 2000
    index = (year - base_year + 4) % 12
    zodiac_name = zodiac_order[index]
    
    # ดึงค่าตัวเลขรหัส (1-12) จากไฟล์ constants เช่น ชวด=1, มะโรง=5
    return ZODIAC.get(zodiac_name, 1), zodiac_name

# ==========================================================
# CONFIGURATION & INITIALIZATION
# ==========================================================
st.set_page_config(page_title="SYNAPSE ENGINE", layout="centered")
st.title("🧠 SYNAPSE ENGINE")
st.caption("Sound & Visual Therapy - Entertainment & Data Exploration")

st.info(ENTERTAINMENT_DISCLAIMER)
st.markdown("---")

# ==========================================================
# INPUT SECTION (รับอินพุตเพียงจุดเดียว)
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
            # 1. แปลงวันที่เป็น "ตัวเลขรหัสวัน" (อาทิตย์=1, จันทร์=2, ... เสาร์=7)
            weekday_names_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
            current_weekday_name = weekday_names_th[selected_date.weekday()]
            auto_weekday_code = WEEKDAYS_TH.get(current_weekday_name, 1)
            
            # 2. แปลงเป็น "ตัวเลขรหัสเดือน" (มกราคม=1 ... ธันวาคม=12)
            thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
                           "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
            current_month_name = thai_months[selected_date.month - 1]
            auto_month_code = MONTHS.get(current_month_name, 1)
            
            # 3. แปลงปีเกิดเป็น "ตัวเลขรหัสปีนักษัตร" (1-12)
            auto_zodiac_code, display_zodiac_name = get_thai_zodiac_code(selected_date.year)
            
            # 4. คำนวณค่าดิถีดวงจันทร์ (1-30)
            datetime_obj = datetime(selected_date.year, selected_date.month, selected_date.day)
            auto_lunar = get_lunar_phase_day(datetime_obj)
            
            # --- เรียกใช้งาน Engine โดยส่งเป็นตัวเลขรหัสทั้งหมดตามที่ MathEngine รอไว้ ---
            engine = SynapseEngine()
            result = engine.calculate(
                weekday=auto_weekday_code,
                month=auto_month_code,
                zodiac=auto_zodiac_code,
                lunar=auto_lunar
            )
            
            st.success("✨ ประมวลผลและแปลงสัญญาณเสร็จสิ้น!")
            
            # ดึงธีมสีแสดงผลจาก COLOR_PALETTE
            bg_color = COLOR_PALETTE.get('SURFACE', '#1a1c23')
            primary_color = COLOR_PALETTE.get('PRIMARY', '#00ccff')
            text_color = COLOR_PALETTE.get('TEXT_LIGHT', '#ffffff')
            secondary_color = COLOR_PALETTE.get('SECONDARY', '#00ff99')
            
            recommended_freq = result.get('analysis', {}).get('recommended_frequency_hz', 0)
            
            # แสดงค่าสรุปที่อ่านง่ายให้ยูสเซอร์ดูบนหน้าต่าง UI
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; border-left: 5px solid {primary_color};">
                <h4 style="color: {primary_color}; margin-top:0;">📡 สรุปสัญญาณ SYNAPSE จากวันเกิด</h4>
                <p style="color: {text_color};"><b>วันเกิด:</b> วัน{current_weekday_name} ที่ {selected_date.day} {current_month_name} ค.ศ. {selected_date.year}</p>
                <p style="color: {text_color};"><b>ปีนักษัตร (Zodiac):</b> ปี{display_zodiac_name} (รหัส: {auto_zodiac_code})</p>
                <p style="color: {text_color};"><b>ระดับดิถีดวงจันทร์ (Lunar Phase):</b> วันที่ {auto_lunar} ของรอบดวงจันทร์</p>
                <hr style="border-color: #333;">
                <p style="color: {secondary_color}; font-size: 20px;"><b>ความถี่ที่แนะนำ:</b> {recommended_freq} Hz</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            
            # แสดงข้อมูล JSON metadata เต็มรูปแบบสำหรับการส่งข้อมูลหลังบ้าน
            with st.expander("🔍 ดูข้อมูลโครงสร้างสัญญาณระบบ (JSON Metadata)"):
                st.json({
                    "inputs_parsed_to_engine_codes": {
                        "weekday_code": auto_weekday_code,
                        "month_code": auto_month_code,
                        "zodiac_code": auto_zodiac_code,
                        "lunar_phase": auto_lunar
                    },
                    "engine_result": result
                })
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในระบบ Engine: {str(e)}")
            st.info("โปรดลอง Reboot App ในแถบเมนู Manage app อีกครั้งเพื่อล้าง Cache ระบบ")
