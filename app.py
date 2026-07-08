import streamlit as st  # แก้ไขตรงนี้
import sys
import os

# บังคับให้ Python มองเห็นโฟลเดอร์ปัจจุบันและโฟลเดอร์ย่อยทั้งหมด
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# นำเข้าค่าคงที่และ Engine
# ❌ แบบเดิม (พิมพ์ตกตัว R ท้ายประโยค)
from engine.constants import WEEKDAYS, ZODIAC_SIGNS, COLOR_PALETTE, ENTERTAINMENT_DISCLAIME

#  แบบที่ถูกต้อง (เติมตัว R ให้สมบูรณ์)
from engine.constants import WEEKDAYS, ZODIAC_SIGNS, COLOR_PALETTE, ENTERTAINMENT_DISCLAIMER
from engine import SynapseEngine
# ... โค้ดส่วนที่เหลือเหมือนเดิมได้เลยครับ ...

# แสดงข้อความชี้แจงเพื่อความบันเทิงที่ด้านบนสุด
st.info(ENTERTAINMENT_DISCLAIMER)

st.markdown("---")

# 2. ส่วนรับข้อมูลจากผู้ใช้งาน (Input Section)
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
    
    # เพิ่มตัวเลือกปีเกิดคริสต์ศักราชเพื่อนำไปคำนวณอายุเชิงข้อมูล
    birth_year = st.number_input("ปี ค.ศ. เกิด (คริสต์ศักราช):", min_value=1900, max_value=2026, value=2000)

st.markdown("---")

# 3. ส่วนการคำนวณและแสดงผลลัพธ์ (Processing & Output)
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
            
            # แสดงผลลัพธ์แบบจัดระเบียบให้สวยงาม
            st.success("✨ ประมวลผลสัญญาณเสร็จสิ้น!")
            
            # ตกแต่งกล่องข้อความจำลองค่าความถี่และธีมสีที่เหมาะสม
            st.markdown(f"""
            <div style="background-color: {COLOR_PALETTE['SURFACE']}; padding: 20px; border-radius: 10px; border-left: 5px solid {COLOR_PALETTE['PRIMARY']};">
                <h4 style="color: {COLOR_PALETTE['PRIMARY']}; margin-top:0;">📡 สรุปสัญญาณ SYNAPSE</h4>
                <p style="color: {COLOR_PALETTE['TEXT_LIGHT']};"><b>วัน:</b> {selected_weekday} | <b>จักรราศี:</b> {selected_zodiac}</p>
                <p style="color: {COLOR_PALETTE['TEXT_LIGHT']};"><b>รอบดวงจันทร์:</b> วันที่ {lunar_phase} ของเดือนจันทรคติ</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            
            # แสดงข้อมูล JSON ตัวเต็มสำหรับการตรวจสอบข้อมูลหลังบ้าน (Debug)
            with st.expander("🔍 ดูข้อมูลโครงสร้างสัญญาณระบบ (JSON Metadata)"):
                st.json(result)
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในระบบ Engine: {str(e)}")
            st.info("โปรดตรวจสอบว่าคลาส SynapseEngine และฟังก์ชัน calculate รองรับพารามิเตอร์ครบถ้วนแล้ว")
# 1. การตั้งค่าหน้าจอและแสดงข้อความ Disclaimer ตามหลักเกณฑ์ความปลอดภัย
st.set_page_config(page_title="SYNAPSE ENGINE", layout="centered")
st.title("🧠 SYNAPSE ENGINE")
st.caption("Sound & Visual Therapy - Entertainment & Data Exploration")

# แสดงข้อความชี้แจงเพื่อความบันเทิงที่ด้านบนสุด
st.info(ENTERTAINMENT_DISCLAIMER)

st.markdown("---")

# 2. ส่วนรับข้อมูลจากผู้ใช้งาน (Input Section)
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
    
    # เพิ่มตัวเลือกปีเกิดคริสต์ศักราชเพื่อนำไปคำนวณอายุเชิงข้อมูล
    birth_year = st.number_input("ปี ค.ศ. เกิด (คริสต์ศักราช):", min_value=1900, max_value=2026, value=2000)

st.markdown("---")

# 3. ส่วนการคำนวณและแสดงผลลัพธ์ (Processing & Output)
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
            
            # แสดงผลลัพธ์แบบจัดระเบียบให้สวยงาม
            st.success("✨ ประมวลผลสัญญาณเสร็จสิ้น!")
            
            # ตกแต่งกล่องข้อความจำลองค่าความถี่และธีมสีที่เหมาะสม
            st.markdown(f"""
            <div style="background-color: {COLOR_PALETTE['SURFACE']}; padding: 20px; border-radius: 10px; border-left: 5px solid {COLOR_PALETTE['PRIMARY']};">
                <h4 style="color: {COLOR_PALETTE['PRIMARY']}; margin-top:0;">📡 สรุปสัญญาณ SYNAPSE</h4>
                <p style="color: {COLOR_PALETTE['TEXT_LIGHT']};"><b>วัน:</b> {selected_weekday} | <b>จักรราศี:</b> {selected_zodiac}</p>
                <p style="color: {COLOR_PALETTE['TEXT_LIGHT']};"><b>รอบดวงจันทร์:</b> วันที่ {lunar_phase} ของเดือนจันทรคติ</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            
            # แสดงข้อมูล JSON ตัวเต็มสำหรับการตรวจสอบข้อมูลหลังบ้าน (Debug)
            with st.expander("🔍 ดูข้อมูลโครงสร้างสัญญาณระบบ (JSON Metadata)"):
                st.json(result)
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในระบบ Engine: {str(e)}")
            st.info("โปรดตรวจสอบว่าคลาส SynapseEngine และฟังก์ชัน calculate รองรับพารามิเตอร์ครบถ้วนแล้ว")
