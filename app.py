import streamlit as st
import sys
import os
import glob
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
    if isinstance(target_date, datetime):
        target_date = target_date.date()
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
# CONFIGURATION & NEON INTERFACE DESIGN (คำสั่งนี้ต้องอยู่บนสุดของ Streamlit)
# ==========================================================
st.set_page_config(page_title="SYNAPSE", layout="centered")

# ดึงสีจากระบบมาสร้างสไตล์นีออนเรืองแสง
PRIMARY = COLOR_PALETTE.get('PRIMARY', '#00ccff')
SECONDARY = COLOR_PALETTE.get('SECONDARY', '#00ff99')
BG_DARK = COLOR_PALETTE.get('SURFACE', '#1a1c23')
TEXT_COLOR = COLOR_PALETTE.get('TEXT_LIGHT', '#ffffff')

st.markdown(f"""
<style>
    /* ตกแต่งกล่องนีออนเรืองแสงหลัก */
    .neon-box {{
        background-color: {BG_DARK};
        padding: 25px;
        border-radius: 15px;
        border: 2px solid {PRIMARY};
        box-shadow: 0 0 15px {PRIMARY};
        margin-bottom: 20px;
    }}
    /* กล่องหมายเลขนำโชคแยกเดี่ยวป้องกันโค้ดหลุด */
    .neon-lucky-card {{
        background-color: #0d0e12;
        padding: 15px;
        border-radius: 10px;
        border: 2px dashed {SECONDARY};
        box-shadow: 0 0 10px {SECONDARY};
        text-align: center;
        margin: 10px 0;
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
    .lucky-number-style {{
        font-size: 42px;
        font-weight: bold;
        color: #ffffff;
        text-shadow: 0 0 10px #ffffff, 0 0 20px {SECONDARY};
        letter-spacing: 3px;
        margin-top: 5px;
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
    /* ตกแต่งช่องกรอกให้มีนีออนแยกสีตามลำดับ User */
    .stDateInput div[data-baseweb="input"] {{
        border: 2px solid {PRIMARY};
        box-shadow: 0 0 10px {PRIMARY};
        background: {BG_DARK};
    }}
    .stDateInput:last-of-type div[data-baseweb="input"] {{
        border: 2px solid #ff00ff;
        box-shadow: 0 0 10px #ff00ff;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# HEADER & LOGO DISPLAY
# ==========================================================
if os.path.exists("logo1.png"):
    st.image("logo1.png", width=120)

st.markdown(f"<h1 style='margin-top:0;'>🧠 <span class='neon-text-primary'>SYNAPSE</span></h1>", unsafe_allow_html=True)
st.caption("🌌 Sound & Visual PERSONAL & PAIR Therapy Resonance Engine")

st.info(ENTERTAINMENT_DISCLAIMER)
st.markdown("---")


# ==========================================================
# [UPDATE!!] INPUT SECTION — รองรับ 2 พิกัดวันเกิด (ขยายเวลาถึงปี 1960)
# ==========================================================
st.subheader("📅 ระบุพิกัดคู่รหัสจักรวาล (Birth Sign Pair Integration)")

col_input1, col_input2 = st.columns(2)

with col_input1:
    st.markdown(f"<p style='color:{PRIMARY}; font-weight:bold; margin-bottom:0;'>🎁 พิกัดตัวคุณ (User 1)</p>", unsafe_allow_html=True)
    selected_date1 = st.date_input(
        "วันเกิด User 1:",
        value=datetime(2000, 1, 1),
        min_value=datetime(1960, 1, 1),  # <-- เพิ่มบรรทัดนี้เพื่อขยายไปปี 1960
        max_value=datetime(2026, 12, 31),
        key="date1"
    )

with col_input2:
    st.markdown(f"<p style='color:#ff00ff; font-weight:bold; margin-bottom:0;'>🔗 พิกัดคู่ของคุณ (User 2)</p>", unsafe_allow_html=True)
    selected_date2 = st.date_input(
        "วันเกิด User 2:",
        value=datetime(2000, 1, 10),
        min_value=datetime(1960, 1, 1),  # <-- เพิ่มบรรทัดนี้เพื่อขยายไปปี 1960
        max_value=datetime(2026, 12, 31),
        key="date2"
    )
    

st.markdown("---")

# ==========================================================
# PROCESSING & OUTPUT SECTION — ระบบตรวจคู่สมพงษ์
# ==========================================================
if st.button("🧬 เริ่มต้นระบบตรวจการสะท้อนพ้องของคลื่น (SYNC PAIR)", use_container_width=True):
    with st.spinner("⚡ กำลังผสานคลื่นพลังงานและวิเคราะห์สัดส่วนทองคำ..."):
        try:
            engine = SynapseEngine()
            
            # --- ฟังก์ชันช่วยสกัดรหัส (Helper) ---
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
            
            # --- คำนวณคลื่นของทั้งสองคนแยกกัน ---
            data1 = parse_date_inputs(selected_date1)
            data2 = parse_date_inputs(selected_date2)
            
            result1 = engine.calculate(data1["weekday"], data1["month"], data1["zodiac"], data1["lunar"])
            result2 = engine.calculate(data2["weekday"], data2["month"], data2["zodiac"], data2["lunar"])
            
            freq1 = result1.get('frequency', 0.0)
            freq2 = result2.get('frequency', 0.0)
            
            # --- 🔮 ระบบคำนวณ Resonance Match ---
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

            st.success("✨ สัญญาณเสถียร! ถอดรหัสโครงสร้างคลื่นคู่สำเร็จ")
            st.markdown(f"<p style='color:{match_color}; font-size:14px;'>🧬 ระบบวัดความ Resonance สำเร็จ: ห่างกัน {diff_percent:.2f}%</p>", unsafe_allow_html=True)
            
            # 🌟 ส่วนที่ 1: การ์ดสถานะ Resonance นีออน
            st.markdown(f"""
            <div class="neon-lucky-card" style="border: 3px double {match_color}; box-shadow: 0 0 20px {match_color}; margin-top: 20px;">
                <span style="color:{TEXT_COLOR}; font-size:14px; opacity:0.8; text-transform: uppercase; letter-spacing: 2px;">SYNAPSE PAIR STATUS</span>
                <div style="color:{match_color}; font-size:32px; font-weight:bold; text-shadow: 0 0 10px #ffffff, 0 0 20px {match_color}; margin: 10px 0;">
                    {match_status}
                </div>
                <hr style="border-color:#333; margin:10px 0;">
                <span style="color:#ffffff; font-size:16px;">💯 คะแนนความสมดุลพ้องของคลื่น: <span style="font-size:36px; font-weight:bold; color:{match_color};">{match_score}%</span></span>
            </div>
            """, unsafe_allow_html=True)

            # 🌟 ส่วนที่ 2: ผังวิเคราะห์คลื่นคู่ (ภาพวงแหวนซ้อนทับ)
            st.write("🌌 **ผังวิเคราะห์โครงสร้างคลื่นคู่ (Dynamic Pair Visualizer Active):**")
            
            def get_neon_shape(calc_total, recommended_freq):
                shape_index = int(abs(calc_total * recommended_freq)) % 4
                if shape_index == 0: return f"border-radius: 50%;"
                elif shape_index == 1: return f"border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;"
                elif shape_index == 2: return f"border-radius: 0%; transform: rotate(45deg); max-width: 90px; max-height: 90px; margin: 10px;"
                else: return f"border-radius: 50% 50% 0% 0% / 40% 40% 0% 0%;"

            shape1_style = get_neon_shape(result1['total'], freq1)
            shape2_style = get_neon_shape(result2['total'], freq2)
            
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: #0d0e12; padding: 40px; border-radius: 12px; border: 1px solid #222; margin: 15px 0;">
                <div style="position: relative; width: 150px; height: 150px; display: flex; align-items: center; justify-content: center;">
                    <div style="position: absolute; width: 140px; height: 140px; border: 4px double {PRIMARY}; box-shadow: 0 0 15px {PRIMARY}, inset 0 0 10px {PRIMARY}; {shape1_style}"></div>
                    <div style="position: absolute; width: 110px; height: 110px; border: 4px double #ff00ff; box-shadow: 0 0 15px #ff00ff, inset 0 0 10px #ff00ff; opacity: 0.8; {shape2_style}"></div>
                </div>
                <div style="display: flex; gap: 30px; margin-top: 30px; font-size: 13px;">
                    <span style="color: {PRIMARY}; border-bottom: 2px solid {PRIMARY};">User 1 ({freq1:.2f} Hz)</span>
                    <span style="color: #ff00ff; border-bottom: 2px solid #ff00ff;">User 2 ({freq2:.2f} Hz)</span>
                </div>
                <span style="color: {match_color}; font-size: 11px; letter-spacing: 2px; margin-top: 15px; text-transform: uppercase; opacity: 0.8;">⚡ Visualizer Shape Match Sync Active ⚡</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 🌟 ส่วนที่ 3: ระบบเพลงคู่
            my_playlist = glob.glob("*.mp3")
            st.write("🎵 **ระบบคัดสรรบทเพลงสำหรับคู่เรา (Personalized Pair Active Trace):**")
            
            if len(my_playlist) > 0:
                my_playlist.sort()
                playlist_index = int(abs(result1['total'] + result2['total']) * (freq1 + freq2)) % len(my_playlist)
                audio_filename = my_playlist[playlist_index]
                st.audio(audio_filename, format="audio/mp3")
                st.caption(f"✨ *บทเพลง `{audio_filename}` ถูกเลือกมาเพื่อจูนพลังงานของทั้งสองคนให้เข้าหากัน*")
            else:
                st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์หลัก")

            # 🌟 ส่วนที่ 4: แผงเปรียบเทียบรหัสปัจจัยดิบ
            st.subheader("🧮 แผงแจกแจงพิกัดรหัสจักรวาล (Math Matrix Comparison)")
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.markdown(f"<p style='color:{PRIMARY}; font-weight:bold; margin-bottom:0;'>User 1 (🎁)</p>", unsafe_allow_html=True)
                st.metric("ความถี่ (Hz)", f"{freq1:.4f} Hz")
                st.markdown(f"**รหัส:** วัน ({data1['weekday']}) เดือน ({data1['month']}) {data1['display_zodiac']} ({data1['zodiac']}) Lunar ({data1['lunar']})")
                
            with col_metric2:
                st.markdown(f"<p style='color:#ff00ff; font-weight:bold; margin-bottom:0;'>User 2 (🔗)</p>", unsafe_allow_html=True)
                st.metric("ความถี่ (Hz)", f"{freq2:.4f} Hz")
                st.markdown(f"**รหัส:** วัน ({data2['weekday']}) เดือน ({data2['month']}) {data2['display_zodiac']} ({data2['zodiac']}) Lunar ({data2['lunar']})")

            # ส่วนตรวจดู JSON คู่
            with st.expander("🔍 ตรวจสอบโครงสร้างระบบดิบ (Pair JSON Metadata)"):
                st.json({"inputs_v1_v2": {"user1": data1, "user2": data2}, "engine_result_v1": result1, "engine_result_v2": result2, "resonance_score": {"diff_percent": diff_percent, "ratio": ratio, "status": match_status, "phi_match": is_phi_match}})
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในระบบ Sync: {str(e)}")
            st.info("โปรดลอง Reboot App ในแถบเมนู Manage app อีกครั้ง")
