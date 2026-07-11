import streamlit as st
import sys
import os

# บังคับให้ Python มองเห็น Root Path เสมอไม่ว่าจะรันบนเครื่องคอมหรือบน Cloud Server
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# นำเข้าค่าคงที่และ Engine
from engine.constants import WEEKDAYS, ZODIAC_SIGNS, COLOR_PALETTE, ENTERTAINMENT_DISCLAIMER
from engine.synapse_engine import SynapseEngine
# ==========================================================
# CONFIGURATION & INITIALIZATION
# ==========================================================
st.set_page_config(page_title="SYNAPSE ENGINE", layout="centered")
st.title("🧠 SYNAPSE ENGINE")
st.caption("Sound & Visual Therapy - Entertainment & Data Exploration")

# แสดงข้อความชี้แจงเพื่อความบันเทิงที่ด้านบนสุด
st.info(ENTERTAINMENT_DISCLAIMER)

st.markdown("---")

# ==========================================================
# INPUT SECTION (UI)
# ==========================================================
st.subheader("📊 เลือกข้อมูลเพื่อคำนวณและปรับสมดุล")

col1, col2 = st.columns(2)

with col1:
    # เลือกวันในสัปดาห์
    selected_weekday = st.selectbox("เลือกวันในสัปดาห์ (Weekday):", WEEKDAYS)
    
    # ดึงรายชื่อราศีจาก ZODIAC_SIGNS ใน constants.py
    zodiac_names = [zodiac["name"] for zodiac in ZODIAC_SIGNS]
    selected_zodiac = st.selectbox("เลือกกลุ่มดาวจักรราศี (Zodiac Sign):", zodiac_names)

with col2:
    # ปฏิทินจันทรคติ (ข้างขึ้น-ข้างแรม เชิงดาราศาสตร์ 1-30 วันรอบดวงจันทร์)
    lunar_phase = st.slider("ระดับดิถีดวงจันทร์ (Lunar Phase Days):", 1, 30, 15)
    
    # เพิ่มตัวเลือกปีเกิดคริสต์ศักราชเพื่อนำไปคำนวณอายุเชิงข้อมูล (อัปเดตปีปัจจุบันเป็น ค.ศ. 2026)
    birth_year = st.number_input("ปี ค.ศ. เกิด (คริสต์ศักราช):", min_value=1900, max_value=2026, value=2000)

st.markdown("---")

# ==========================================================
# PROCESSING & OUTPUT SECTION
# ==========================================================
if st.button("🚀 เริ่มต้นระบบคำนวณและซิงค์สัญญาณ", use_container_width=True):
    with st.spinner("กำลังประมวลผลข้อมูลทางคณิตศาสตร์และดาราศาสตร์..."):
        try:
            # เรียกใช้งาน SynapseEngine
            engine = SynapseEngine()
            
            # ส่งค่าไปยังฟังก์ชัน calculate ของ Engine
            result = engine.calculate(
                weekday=selected_weekday,
                zodiac=selected_zodiac,
                lunar=lunar_phase,
                birth_year=birth_year
            )
            
            st.success("✨ ประมวลผลสัญญาณเสร็จสิ้น!")
            
            # ดึงค่าสีออกมาก่อนเพื่อป้องกัน F-String Syntax Error ใน HTML
            bg_color = COLOR_PALETTE.get('SURFACE', '#f0f2f6')
            primary_color = COLOR_PALETTE.get('PRIMARY', '#ff4b4b')
            text_color = COLOR_PALETTE.get('TEXT_LIGHT', '#31333f')
            secondary_color = COLOR_PALETTE.get('SECONDARY', '#1c83e1')
            
            recommended_freq = result.get('analysis', {}).get('recommended_frequency_hz', 0)
            
            # ตกแต่งกล่องข้อความจำลองค่าความถี่และธีมสีที่เหมาะสมด้วย COLOR_PALETTE
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 20px; border-radius: 10px; border-left: 5px solid {primary_color};">
                <h4 style="color: {primary_color}; margin-top:0;">📡 สรุปสัญญาณ SYNAPSE</h4>
                <p style="color: {text_color};"><b>วัน:</b> {selected_weekday} | <b>จักรราศี:</b> {selected_zodiac}</p>
                <p style="color: {text_color};"><b>รอบดวงจันทร์:</b> วันที่ {lunar_phase} ของเดือนจันทรคติ</p>
                <p style="color: {secondary_color};"><b>ความถี่ที่แนะนำ:</b> {recommended_freq} Hz</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            
            # แสดงข้อมูล JSON ตัวเต็มสำหรับการตรวจสอบข้อมูลหลังบ้าน
            with st.expander("🔍 ดูข้อมูลโครงสร้างสัญญาณระบบ (JSON Metadata)"):
                st.json(result)
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในระบบ Engine: {str(e)}")
            st.info("โปรดตรวจสอบว่าคลาส SynapseEngine ในไฟล์ synapse_engine.py ทำงานได้ถูกต้อง และคืนค่าเป็น Dictionary ที่มีคีย์ ['analysis']['recommended_frequency_hz']")
