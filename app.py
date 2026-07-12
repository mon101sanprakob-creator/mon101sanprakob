import streamlit as st
import sys
import os
import glob
import calendar
import pandas as pd
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
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    base_date = datetime(2000, 1, 6).date()  
    diff_days = (target_date - base_date).days
    lunar_age = diff_days % SYNODIC_MONTH
    lunar_day = int(lunar_age) + 1
    return min(max(lunar_day, 1), 30)

def get_thai_zodiac_code(year):
    zodiac_order = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
    base_year = 2000
    index = (year - base_year + 4) % 12
    zodiac_name = zodiac_order[index]
    return ZODIAC.get(zodiac_name, 1), zodiac_name

def parse_date_inputs(selected_date):
    weekday_names_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    current_weekday_name = weekday_names_th[selected_date.weekday()]
    auto_weekday_code = WEEKDAYS_TH.get(current_weekday_name, 1)
    
    thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    current_month_name = thai_months[selected_date.month - 1]
    auto_month_code = MONTHS.get(current_month_name, 1)
    
    auto_zodiac_code, display_zodiac_name = get_thai_zodiac_code(selected_date.year)
    auto_lunar = get_lunar_phase_day(selected_date)
    return {
        "weekday": auto_weekday_code, "month": auto_month_code, "zodiac": auto_zodiac_code, "lunar": auto_lunar,
        "display_weekday": current_weekday_name, "display_month": current_month_name, "display_zodiac": display_zodiac_name
    }

# ==========================================================
# CONFIGURATION & NEON INTERFACE DESIGN
# ==========================================================
st.set_page_config(page_title="SYNAPSE", layout="centered")

PRIMARY = COLOR_PALETTE.get('PRIMARY', '#00ccff')
SECONDARY = COLOR_PALETTE.get('SECONDARY', '#00ff99')
BG_DARK = COLOR_PALETTE.get('SURFACE', '#1a1c23')
TEXT_COLOR = COLOR_PALETTE.get('TEXT_LIGHT', '#ffffff')

st.markdown(f"""
<style>
    .neon-lucky-card {{
        background-color: #0d0e12;
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        margin: 12px 0;
    }}
    .neon-text-primary {{
        color: {PRIMARY};
        text-shadow: 0 0 8px {PRIMARY};
        font-weight: bold;
    }}
    .lucky-number-style {{
        font-size: 42px;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 0 0 10px #ffffff, 0 0 20px {SECONDARY};
        letter-spacing: 5px;
        margin-top: 5px;
    }}
    .stDateInput div[data-baseweb="input"] {{
        border: 2px solid {PRIMARY};
        box-shadow: 0 0 10px {PRIMARY};
        background: {BG_DARK};
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER & LOGO
# ==========================================================
if os.path.exists("logo1.png"):
    st.image("logo1.png", width=120)

st.markdown(f"<h1 style='margin-top:0;'>🧠 <span class='neon-text-primary'>SYNAPSE</span></h1>", unsafe_allow_html=True)
st.caption("🌌 Sound & Visual PERSONAL & PAIR Therapy Resonance Engine")

st.info(ENTERTAINMENT_DISCLAIMER)
st.markdown("---")

tab1, tab2 = st.tabs(["🧬 วิเคราะห์พิกัดบุคคลหลัก", "🔮 พยากรณ์ตารางพลังงานรายเดือน"])

# ==========================================================
# แท็บที่ 1: บุคคลหลัก (และส่วนเสริมบุคคลที่ 2 แบบเลือกได้)
# ==========================================================
with tab1:
    st.subheader("📅 ระบุพิกัดเวลาเกิดหลัก (Main User Integration)")
    
    # กรอกบุคคลหลักเสมอ
    st.markdown(f"<p style='color:{PRIMARY}; font-weight:bold; margin-bottom:0;'>🎁 พิกัดตัวคุณ (บุคคลหลัก)</p>", unsafe_allow_html=True)
    selected_date1 = st.date_input(
        "วันเกิดของคุณ:",
        value=datetime(2000, 1, 1),
        min_value=datetime(1960, 1, 1),
        max_value=datetime(2026, 12, 31),
        key="date1"
    )
    
    # 🔗 สวิตช์เปิด-ปิด โหมดบุคคลที่ 2 เสริม (Optional)
    enable_pair = st.checkbox("🔗 เปิดโหมดคำนวณคู่สมพงษ์ร่วมด้วย (เปิดเฉพาะบางกรณี)", value=False)
    
    selected_date2 = None
    if enable_pair:
        st.markdown(f"<p style='color:#ff00ff; font-weight:bold; margin-bottom:0;'>🔗 พิกัดบุคคลที่สอง (ส่วนเสริมคู่สมพงษ์)</p>", unsafe_allow_html=True)
        selected_date2 = st.date_input(
            "วันเกิดบุคคลที่สอง:",
            value=datetime(2000, 1, 10),
            min_value=datetime(1960, 1, 1),
            max_value=datetime(2026, 12, 31),
            key="date2"
        )
        
    st.markdown("---")
    
    if st.button("🧬 เริ่มต้นระบบประมวลผลสัญญาณคลื่น", use_container_width=True):
        with st.spinner("⚡ กำลังถอดรหัสและผสานสัญญาณพลังงาน..."):
            try:
                engine = SynapseEngine()
                data1 = parse_date_inputs(selected_date1)
                result1 = engine.calculate(data1["weekday"], data1["month"], data1["zodiac"], data1["lunar"])
                freq1 = result1.get('frequency', 0.0)
                
                # --- [1] แสดงผลเฉพาะบุคคลหลักแบบจัดเต็ม (ไม่ให้หายไปไหน) ---
                st.success("✨ ถอดรหัสคลื่นพลังงานเฉพาะบุคคลหลักเสร็จสิ้น!")
                
                # รหัสควอนตัม 3 ตัว 2 ตัว แบบไม่บอกว่าหวย
                lucky_three_1 = str(int(abs(result1['total'] * PHI)) % 900 + 100)
                lucky_two_1 = str(int(abs(result1['energy'] * freq1)) % 90 + 10).zfill(2)
                
                st.markdown(f"""
                <div class="neon-lucky-card" style="border: 2px solid {PRIMARY}; box-shadow: 0 0 15px {PRIMARY};">
                    <h3 style='color:{PRIMARY}; margin:0;'>📊 ผลลัพธ์ความถี่บุคคลหลัก: <span style='color:#fff;'>{freq1:.4f} Hz</span></h3>
                    <p style='font-size:13px; color:#888;'>รหัสฐาน: วัน {data1['display_weekday']} | เดือน {data1['display_month']} | ปี {data1['display_zodiac']} | ดิถีที่ ({data1['lunar']})</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("🧬 **รหัสสัญญาณคลื่นนำโชคประจำพิกัด (Quantum Number Decryption):**")
                col_num1, col_num2 = st.columns(2)
                with col_num1:
                    st.markdown(f"""
                    <div class="neon-lucky-card" style="border: 2px dashed {PRIMARY}; box-shadow: 0 0 10px {PRIMARY};">
                        <span style="color:{PRIMARY}; font-size:12px; font-weight:bold; letter-spacing:1px;">🔺 TRI-RESONANCE MATRIX</span>
                        <div class="lucky-number-style" style="text-shadow: 0 0 10px #ffffff, 0 0 20px {PRIMARY};">{lucky_three_1}</div>
                        <span style="color:#888888; font-size:10px; display:block; margin-top:5px;">*รหัสเชื่อมต่อสนามพลังงาน 3 มิติเฉพาะบุคคล</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_num2:
                    st.markdown(f"""
                    <div class="neon-lucky-card" style="border: 2px dashed {SECONDARY}; box-shadow: 0 0 10px {SECONDARY};">
                        <span style="color:{SECONDARY}; font-size:12px; font-weight:bold; letter-spacing:1px;">🔹 BINARY QUANTUM CORE</span>
                        <div class="lucky-number-style" style="text-shadow: 0 0 10px #ffffff, 0 0 20px {SECONDARY};">{lucky_two_1}</div>
                        <span style="color:#888888; font-size:10px; display:block; margin-top:5px;">*รหัสประจุพลังงานควอนตัมคู่ประจำฐานเวลา</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.write("🧬 **รหัสสัญญาณคลื่นนำโชคประจำพิกัด (Quantum Number Decryption):**")
                col_num1, col_num2 = st.columns(2)
                with col_num1:
                    st.markdown(f"""
                    <div class="neon-lucky-card" style="border: 2px dashed {PRIMARY}; box-shadow: 0 0 10px {PRIMARY};">
                        <span style="color:{PRIMARY}; font-size:12px; font-weight:bold; letter-spacing:1px;">🔺 TRI-RESONANCE MATRIX</span>
                        <div class="lucky-number-style" style="text-shadow: 0 0 10px #ffffff, 0 0 20px {PRIMARY};">{lucky_three_1}</div>
                        <span style="color:#888888; font-size:10px; display:block; margin-top:5px;">*รหัสเชื่อมต่อสนามพลังงาน 3 มิติเฉพาะบุคคล</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_num2:
                    st.markdown(f"""
                    <div class="neon-lucky-card" style="border: 2px dashed {SECONDARY}; box-shadow: 0 0 10px {SECONDARY};">
                        <span style="color:{SECONDARY}; font-size:12px; font-weight:bold; letter-spacing:1px;">🔹 BINARY QUANTUM CORE</span>
                        <div class="lucky-number-style" style="text-shadow: 0 0 10px #ffffff, 0 0 20px {SECONDARY};">{lucky_two_1}</div>
                        <span style="color:#888888; font-size:10px; display:block; margin-top:5px;">*รหัสประจุพลังงานควอนตัมคู่ประจำฐานเวลา</span>
                    </div>
                    """, unsafe_allow_html=True)
                  # แผงตรวจสอบค่าดัชนีดิบ (ปรับให้เก็บรหัสควอนตัมเข้า JSON ด้วย)
with st.expander("🔍 ตรวจสอบโครงสร้างระบบดิบบุคคลหลัก (Main User JSON Metadata)", expanded=True):
    st.json({
        "user_inputs": data1,
        "engine_calculations": result1,
        "quantum_codes": {
            "tri_resonance_matrix": lucky_three_1,  # ค่า 513 จะมาโชว์ในนี้
            "binary_quantum_core": lucky_two_1      # ค่า 27 จะมาโชว์ในนี้
        }
    })


                # ==========================================================
                # 🔍 [เพิ่มตรงนี้!] แผงตรวจสอบค่าดัชนีดิบ (Main User JSON Metadata)
                # ==========================================================
                with st.expander("🔍 ตรวจสอบโครงสร้างระบบดิบบุคคลหลัก (Main User JSON Metadata)", expanded=True):
                    st.json({
                        "user_inputs": data1,
                        "engine_calculations": result1,
                        "quantum_codes": {
                            "tri_resonance_matrix": lucky_three_1,
                            "binary_quantum_core": lucky_two_1
                        }
                    })

                # --- [2] ทำงานของบุคคลที่สองเสริมขึ้นมา (เฉพาะกรณีที่ติ๊กเลือกเท่านั้น) ---
                if enable_pair and selected_date2 is not None:
                    st.markdown("---")
                    st.subheader("🔗 ผลวิเคราะห์การสะท้อนพ้องร่วมกับบุคคลที่สอง (Pair Integration Mode)")
                    
                    data2 = parse_date_inputs(selected_date2)
                    result2 = engine.calculate(data2["weekday"], data2["month"], data2["zodiac"], data2["lunar"])
                    freq2 = result2.get('frequency', 0.0)
                    
                    diff_percent = abs(freq1 - freq2) / max(freq1, freq2) * 100
                    ratio = max(freq1, freq2) / min(freq1, freq2)
                    is_phi_match = abs(ratio - 1.618034) < 0.016  
                    
                    match_score = 0
                    match_status = ""
                    match_color = ""
                    
                    if is_phi_match:
                        match_status = "🏆 Cosmic Soulmates (คู่แท้บุพเพสันนิวาสแห่งจักรวาล)"
                        match_color = "#ffd700"
                        match_score = 100
                    elif diff_percent <= 2.5:
                        match_status = "🟢 Perfect Resonance (คู่มิตรแท้ส่งเสริมกัน)"
                        match_color = SECONDARY
                        match_score = int(100 - (diff_percent * 4))  
                    elif diff_percent <= 7.5:
                        match_status = "🟡 Harmonic Balance (คู่พันธมิตรปลอดภัย)"
                        match_color = PRIMARY
                        match_score = int(90 - (diff_percent * 3))
                    elif diff_percent <= 15.0:
                        match_status = "🔵 Dynamic Friction (คู่เหวี่ยงท้าทาย)"
                        match_color = "#ff00ff"
                        match_score = int(70 - (diff_percent * 2))
                    else:
                        match_status = "🔴 Dissonance Wave (คู่อริหักล้างรุนแรง)"
                        match_color = "#ff3333"
                        match_score = max(10, int(40 - (diff_percent * 0.5)))
                        
                    st.markdown(f"""
                    <div class="neon-lucky-card" style="border: 3px double {match_color}; box-shadow: 0 0 20px {match_color};">
                        <span style="color:#fff; font-size:12px; letter-spacing: 2px;">SYNAPSE PAIR STATUS</span>
                        <div style="color:{match_color}; font-size:26px; font-weight:bold; text-shadow: 0 0 10px #ffffff, 0 0 20px {match_color}; margin: 8px 0;">
                            {match_status}
                        </div>
                        <span style="color:#ffffff;">💯 คะแนนสมดุล: <span style="font-size:24px; font-weight:bold; color:{match_color};">{match_score}%</span> (ต่างกัน {diff_percent:.2f}%)</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # รูปร่างวงแหวนซ้อนทับโหมดคู่
                    def get_neon_shape(calc_total, recommended_freq):
                        shape_index = int(abs(calc_total * recommended_freq)) % 4
                        if shape_index == 0: return "border-radius: 50%;"
                        elif shape_index == 1: return "border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;"
                        elif shape_index == 2: return "border-radius: 0%; transform: rotate(45deg); max-width: 90px; max-height: 90px; margin: 10px;"
                        else: return "border-radius: 50% 50% 0% 0% / 40% 40% 0% 0%;"
                    
                    shape1_style = get_neon_shape(result1['total'], freq1)
                    shape2_style = get_neon_shape(result2['total'], freq2)
                    
                    st.markdown(f"""
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: #0d0e12; padding: 30px; border-radius: 12px; border: 1px solid #222; margin: 15px 0;">
                        <div style="position: relative; width: 130px; height: 130px; display: flex; align-items: center; justify-content: center;">
                            <div style="position: absolute; width: 120px; height: 120px; border: 4px double {PRIMARY}; box-shadow: 0 0 15px {PRIMARY}; {shape1_style}"></div>
                            <div style="position: absolute; width: 90px; height: 90px; border: 4px double #ff00ff; box-shadow: 0 0 15px #ff00ff; opacity: 0.8; {shape2_style}"></div>
                        </div>
                        <div style="font-size:12px; margin-top:15px; color:#888;">คุณ ({freq1:.2f} Hz) ⚡ คู่ของคุณ ({freq2:.2f} Hz)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # --- [3] ส่วนโหลดเพลงประจำตัว (ดึงเพลงตามบุคคลหลัก หรือ ผลรวมคู่) ---
                my_playlist = glob.glob("*.mp3")
                if len(my_playlist) > 0:
                    my_playlist.sort()
                    if enable_pair and selected_date2 is not None:
                        playlist_index = int(abs(result1['total'] + result2['total']) * (freq1 + freq2)) % len(my_playlist)
                    else:
                        playlist_index = int(abs(result1['total'] * PHI)) % len(my_playlist)
                    
                    st.write("🎵 **บทเพลงบำบัดคลื่นเสียงเฉพาะพิกัด (Personalized Audio Therapy):**")
                    st.audio(my_playlist[playlist_index], format="audio/mp3")
                    st.caption(f"✨ *จัดสรรบทเพลงคัดพิเศษ `{my_playlist[playlist_index]}` เพื่อปรับความเสถียรของคลื่น*")
                    
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผลสัญญาณ: {str(e)}")

# ==========================================================
# แท็บที่ 2: โหมดปฏิทินพยากรณ์คลื่นรายเดือน (อ้างอิงบุคคลหลัก)
# ==========================================================
with tab2:
    st.subheader("🔮 เครื่องพยากรณ์คลื่นพลังงานรายเดือน (Monthly Cyber Rhythm)")
    st.caption("ระบบวนลูปคำนวณสเกลเวลาในอนาคตและอดีต เพื่อพยากรณ์ความเบาสบายของบุคคลหลักรายวัน")
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        view_year = st.selectbox("เลือกปีที่ต้องการดู (ย้อนได้ถึง 1960):", range(1960, 2031), index=datetime.now().year - 1960)
    with col_sel2:
        view_month = st.selectbox("เลือกเดือนที่ต้องการดู:", range(1, 13), index=datetime.now().month - 1)
        
    if st.button("📊 เจนเนอเรตตารางสภาพคลื่นรายเดือน", use_container_width=True):
        with st.spinner("⏳ กำลังจำลองฐานมิติเวลา..."):
            try:
                engine = SynapseEngine()
                num_days = calendar.monthrange(view_year, view_month)[1]
                calendar_data = []
                
                for day in range(1, num_days + 1):
                    loop_date = datetime(view_year, view_month, day).date()
                    loop_data = parse_date_inputs(loop_date)
                    
                    res = engine.calculate(loop_data["weekday"], loop_data["month"], loop_data["zodiac"], loop_data["lunar"])
                    f_val = res.get('frequency', 0.0)
                    
                    metric_check = int(abs(res['total'] * f_val)) % 3
                    if metric_check == 0:
                        status = "🟢 เบาสบาย สมองปลอดโปร่ง (Healing Day)"
                    elif metric_check == 1:
                        status = "🟡 นิ่งมั่นคง พลังงานปกติ (Stable Day)"
                    else:
                        status = "🔴 หนักหน่วง/ท้าทาย ควรระวัง (High Friction Day)"
                        
                    calendar_data.append({
                        "วันที่": f"{day:02d}/{view_month:02d}/{view_year}",
                        "วัน": loop_data["display_weekday"],
                        "ความถี่คลื่น (Hz)": f"{f_val:.4f} Hz",
                        "ข้างขึ้นข้างแรม": f"วันจันทรคติที่ {loop_data['lunar']}",
                        "สภาพคลื่นพลังงานรายวัน": status
                    })
                
                df = pd.DataFrame(calendar_data)
                st.success(f"📈 เจนเนอเรตแผนผังพลังงานประจำเดือน {view_month}/{view_year} สำเร็จ!")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"ไม่สามารถประมวลผลปฏิทินได้: {str(e)}")
