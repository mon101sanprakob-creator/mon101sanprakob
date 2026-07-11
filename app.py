import streamlit as st
import sys
import os
from datetime import datetime

# บังคับให้ Python มองเห็น Root Path เสมอ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# นำเข้าค่าคงที่และ Engine จากไฟล์ระบบ
from engine.constants import WEEKDAYS_TH, MONTHS, ZODIAC, COLOR_PALETTE, ENTERTAINMENT_DISCLAIMER, PHI, SYNODIC_MONTH
from engine.synapse_engine import SynapseEngine

# ==========================================================
# HELPER FUNCTIONS FOR CONVERSION
# ==========================================================
def get_lunar_phase_day(target_date):
    """คำนวณดิถีดวงจันทร์โดยอ้างอิงรอบดวงจันทร์จาก constants.py"""
    # 🔥 [FIXED] แปลงฐานเวลาเป็น datetime.date เพื่อป้องกันบั๊ก Type mismatch
    base_date = datetime(2000, 1, 6).date()  
    diff_days = (target_date - base_date).days
    lunar_age = diff_days % SYNODIC_MONTH
    lunar_day = int(lunar_age) + 1
    return min(max(lunar_day, 1), 30)

def get_thai_zodiac_code(year):
    """แปลงปี ค.ศ. เกิดให้กลายเป็นรหัสตัวเลขปีนักษัตรไทย (1-12)"""
    zodiac_order = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
    base_year = 2000
    index = (year - base_year + 4) % 12
    zodiac_name = zodiac_order[index]
    return ZODIAC.get(zodiac_name, 1), zodiac_name

# ==========================================================
# CONFIGURATION & NEON INTERFACE DESIGN (CUSTOM CSS)
# ==========================================================
st.set_page_config(page_title="SYNAPSE", layout="centered")

# ดึงสีจากระบบมาสร้างสไตล์นีออนเรืองแสง
PRIMARY = COLOR_PALETTE.get('PRIMARY', '#00ccff')
SECONDARY = COLOR_PALETTE.get('SECONDARY', '#00ff99')
BG_DARK = COLOR_PALETTE.get('SURFACE', '#1a1c23')
TEXT_COLOR = COLOR_PALETTE.get('TEXT_LIGHT', '#ffffff')

st.markdown(f"""
<style>
    /* ตกแต่งกล่องนีออนเรืองแสง */
    .neon-box {{
        background-color: {BG_DARK};
        padding: 25px;
        border-radius: 15px;
        border: 2px solid {PRIMARY};
        box-shadow: 0 0 15px {PRIMARY}, inset 0 0 10px {BG_DARK};
        margin-bottom: 25px;
    }}
    .neon-lucky-box {{
        background-color: #0d0e12;
        padding: 20px;
        border-radius: 12px;
        border: 2px dashed {SECONDARY};
        box-shadow: 0 0 15px {SECONDARY};
        text-align: center;
        margin-top: 20px;
    }}
    .neon-text-primary {{
        color: {PRIMARY};
        text-shadow: 0 0 8px {PRIMARY};
        font-weight: bold;
    }}
    .neon-text-secondary {{
        color: {SECONDARY};
        text-shadow: 0 0 8px {SECONDARY};
        font-weight: bold;
    }}
    .lucky-number {{
        font-size: 38px;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 0 0 12px #ffffff, 0 0 20px {SECONDARY};
        letter-spacing: 5px;
    }}
    /* จำลองคลื่น Waveform เคลื่อนไหวด้วย CSS */
    .wave-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 60px;
        margin: 20px 0;
        background: #0d0e12;
        border-radius: 8px;
        border: 1px solid #333;
    }}
    .bar {{
        display: inline-block;
        width: 4px;
        height: 10px;
        background-color: {SECONDARY};
        margin: 0 3px;
        border-radius: 2px;
        animation: pulse 1s ease-in-out infinite alternate;
    }}
    .bar:nth-child(2n) {{ background-color: {PRIMARY}; animation-delay: 0.2s; }}
    .bar:nth-child(3n) {{ animation-delay: 0.4s; }}
    .bar:nth-child(4n) {{ animation-delay: 0.6s; }}
    @keyframes pulse {{
        0% {{ height: 10px; transform: scaleY(1); }}
        100% {{ height: 45px; transform: scaleY(1.1); box-shadow: 0 0 10px {SECONDARY}; }}
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER & LOGO DISPLAY
# ==========================================================
if os.path.exists("logo1.png"):
    st.image("logo1.png", width=120)

st.markdown(f"<h1 style='margin-top:0;'>🧠 <span class='neon-text-primary'>SYNAPSE</span></h1>", unsafe_allow_html=True)
st.caption("🌌 Sound & Visual Personal Therapy Engine — Cyberpunk Edition")

st.info(ENTERTAINMENT_DISCLAIMER)
st.markdown("---")

# ==========================================================
# INPUT SECTION
# ==========================================================
st.subheader("📅 ระบุพิกัดเวลาเกิด (Birth Sign Integration)")

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
if st.button("🚀 เริ่มต้นระบบคำนวณและซิงค์สัญญาณนีออน", use_container_width=True):
    with st.spinner("⚡ กำลังประมวลผลอัลกอริทึมและผสานค่าดาราศาสตร์สากล..."):
        try:
            # 1. ถอดรหัสค่าวัน-เดือน
            weekday_names_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
            current_weekday_name = weekday_names_th[selected_date.weekday()]
            auto_weekday_code = WEEKDAYS_TH.get(current_weekday_name, 1)
            
            thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
                           "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
            current_month_name = thai_months[selected_date.month - 1]
            auto_month_code = MONTHS.get(current_month_name, 1)
            
            # 2. ถอดรหัสปีนักษัตรและคำนวณวันจันทรคติ
            auto_zodiac_code, display_zodiac_name = get_thai_zodiac_code(selected_date.year)
            auto_lunar = get_lunar_phase_day(selected_date)
            
            # 3. สั่งประมวลผลผ่าน Engine หลัก
            engine = SynapseEngine()
            result = engine.calculate(
                weekday=auto_weekday_code,
                month=auto_month_code,
                zodiac=auto_zodiac_code,
                lunar=auto_lunar
            )
            
            # ดึงตัวแปรผลลัพธ์ย่อยทั้งหมดออกมาใช้งาน
            recommended_freq = result.get('frequency', 0.0)
            calc_day = result.get('day', 0.0)
            calc_month = result.get('month', 0.0)
            calc_zodiac = result.get('zodiac', 0.0)
            calc_lunar = result.get('lunar', 0.0)
            calc_total = result.get('total', 0.0)
            calc_energy = result.get('energy', 0.0)
            calc_root = result.get('root', 2)
            
            # 🔮 [NEW] อัลกอริทึมสกัดเลขเด่น 3 ตัว และเลขท้าย 2 ตัว จากสัญญาณความถี่จริง
            # ดึงเลข 3 หลักแรกหน้าทศนิยม (หรือตัดเศษ)
            freq_str = f"{recommended_freq:.4f}".replace('.', '')
            digit_3 = freq_str[1:4]  # สกัดเลขเด่น 3 ตัวจากตำแหน่งแกนกลางความถี่
            digit_2 = freq_str[-3:-1] # สกัดเลขท้าย 2 ตัวจากแกนพลังงานทศนิยมปลายสาย
            
            st.success("✨ สัญญาณเสถียร! ถอดรหัสโครงสร้างคลื่นสำเร็จ")
            
            # 🌟 ส่วนที่ 1: การ์ดนีออนแสดงผลคลื่นแนะนำหลัก
            st.markdown(f"""
            <div class="neon-box">
                <h4 style="margin-top:0; color:{TEXT_COLOR};">📡 สรุปสัญญาณผลลัพธ์ SYNAPSE</h4>
                <p style="color:{TEXT_COLOR}; font-size:15px; margin-bottom:5px;">
                    <b>พิกัดวันเกิดของคุณ:</b> วัน{current_weekday_name}ที่ {selected_date.day} {current_month_name} ค.ศ. {selected_date.year}
                </p>
                <p style="color:{TEXT_COLOR}; font-size:14px; opacity:0.8;">
                    รหัสตัวแปร: วัน ({auto_weekday_code}) | เดือน ({auto_month_code}) | ปี{display_zodiac_name} ({auto_zodiac_code}) | ดิถีดวงจันทร์ ({auto_lunar})
                </p>
                <hr style="border-color:#333; margin:15px 0;">
                <p style="color:{TEXT_COLOR}; font-size:16px; margin-bottom:5px;">✨ คลื่นความถี่จำลองที่แนะนำสำหรับคุณ:</p>
                <h2 class="neon-text-primary" style="margin:0; font-size:36px;">{recommended_freq:.4f} Hz</h2>
                
                <div class="neon-lucky-box">
                    <span style="color:{SECONDARY}; font-weight:bold; font-size:14px; text-transform:uppercase; letter-spacing:2px;">🔮 SYNAPSE MATRIX MATRIX NUMBERS 🔮</span>
                    <div style="display:flex; justify-content:space-around; margin-top:15px;">
                        <div>
                            <div style="color:{TEXT_COLOR}; font-size:13px; opacity:0.7;">เลขเด่น (3 ตัว)</div>
                            <div class="lucky-number">{digit_3}</div>
                        </div>
                        <div style="border-left: 1px solid #333; height: 60px;"></div>
                        <div>
                            <div style="color:{TEXT_COLOR}; font-size:13px; opacity:0.7;">เลขท้าย (2 ตัว)</div>
                            <div class="lucky-number" style="color:{PRIMARY}; text-shadow: 0 0 12px #ffffff, 0 0 20px {PRIMARY};">{digit_2}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 🌟 ส่วนที่ 2: แถบแอนิเมชันจำลองการปล่อยคลื่นเสียงบำบัด
            st.write("🎵 **ระบบจำลองสัญญาณคลื่นเสียง (Frequencies Bio-feedback Active):**")
            st.markdown(
                '<div class="wave-container">' + ''.join(['<div class="bar"></div>' for _ in range(35)]) + '</div>', 
                unsafe_allow_html=True
            )
            
            # 🌟 ส่วนที่ 3: แผงแจกแจงที่มาและสูตรคำนวณ (เปิดเผยค่า 1.618 และ 29.53)
            st.subheader("🧮 แผงวงจรคำนวณและค่าคงที่สากล (Math Matrix)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="📊 ผลลัพธ์ปัจจัยรายวัน (Day Factor)", value=f"{calc_day:.4f}")
                st.metric(label="🌙 ผลลัพธ์ปัจจัยจันทรคติ (Lunar Factor)", value=f"{calc_lunar:.4f}")
                st.markdown(f"**📐 ค่าสัดส่วนทองคำธรรมชาติ ($\Phi$):** `{PHI}`")
            
            with col2:
                st.metric(label="📅 ผลลัพธ์ปัจจัยรายเดือน (Month Factor)", value=f"{calc_month:.4f}")
                st.metric(label="🧬 ผลลัพธ์ปัจจัยราศี (Zodiac Factor)", value=f"{calc_zodiac:.4f}")
                st.markdown(f"**🌑 รอบดวงจันทร์ดาราศาสตร์:** `{SYNODIC_MONTH}` วัน")
                
            st.markdown("---")
            
            # รายละเอียดสรุปสมการ
            st.info(f"""
            💡 **ถอดรหัสลอจิกคณิตศาสตร์หลังบ้าน:**
            1. ระบบนำค่าตัวแปรวันเกิดที่แปลงเป็นรหัสแล้ว ไปคำนวณร่วมกับเครื่องยนต์หลักจนได้ผลรวมปัจจัยดิบ **{calc_total:.4f}**
            2. นำไปประมวลผลสัญญาณจนได้ค่าพลังงานสุทธิที่ **{calc_energy:.4f}** แล้วนำไปถอดค่ารากกำลังระดับมิติ **รากที่ {calc_root}**
            3. นำพลังงานสุดท้ายผสานร่วมกับอัตราส่วนทองคำธรรมชาติ **({PHI:.4f})** ออกมาเป็นคลื่นเฉพาะบุคคล **{recommended_freq:.4f} Hz** และสกัดรหัส Matrix ออกมาเป็นเลข **{digit_3}** และ **{digit_2}**
            """)
            
            # 🌟 ส่วนที่ 4: ปุ่มกดดาวน์โหลดเอกสารรายงานสรุปสัญญาณ
            report_text = f"""--- SYNAPSE ENGINE REPORT ---
Date Calculated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
User Birthday: {selected_date.strftime('%Y-%m-%d')}
---------------------------------
[Final personal Frequency Output]
=> RECOMMENDED FREQUENCY: {recommended_freq} Hz
=> MATRIX CODES DECODED: 3-Digits [{digit_3}] | 2-Digits [{digit_2}]
---------------------------------
"""
            st.download_button(
                label="📥 ดาวน์โหลดบันทึกผลการถอดรหัสคลื่น (.txt)",
                data=report_text,
                file_name=f"synapse_signal_{selected_date.strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            # ส่วนตรวจดู JSON
            with st.expander("🔍 ตรวจสอบโครงสร้างระบบดิบ (JSON Metadata)"):
                st.json({"inputs_parsed_to_engine_codes": {"weekday_code": auto_weekday_code, "month_code": auto_month_code, "zodiac_code": auto_zodiac_code, "lunar_phase": auto_lunar}, "engine_result": result})
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในระบบ Engine: {str(e)}")
            st.info("โปรดลอง Reboot App ในแถบเมนู Manage app อีกครั้งเพื่อเคลียร์ Cache")
