import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
from shapely.ops import transform

# ตั้งค่าหน้าเว็บให้เต็มจอและเปิดสไตล์เข้มขรึมช่วยให้อ่านง่ายกลางแดด
st.set_page_config(page_title="GPS Precision Measure", layout="wide", page_icon="🎯")

st.title("🎯 แอปวัดที่ดินความแม่นยำสูง (ระบบเล็งหมุดพิกัดจริง)")
st.write("วิธีใช้: เดินไปยังมุมที่ดินจริง เล็งให้กากบาทสีแดงกลางแผนที่ตรงกับตัวคุณ หรือตำแหน่งที่ต้องการ จากนั้นกด 'บันทึกจุดนี้' เมื่อครบทุกมุมแล้วจึงกด 'สั่งคำนวณพื้นที่'")

# --- ฟังก์ชันคำนวณพื้นที่และการแปลงหน่วย ---
def calculate_polygon_area(lat_lons):
    if len(lat_lons) < 3:
        return 0.0
    lon_lats = [(lon, lat) for lat, lon in lat_lons]
    polygon = Polygon(lon_lats)
    
    proj_wgs84 = pyproj.Proj(init='epsg:4326')
    proj_aea = pyproj.Proj(proj='aea', lat_1=polygon.bounds[1], lat_2=polygon.bounds[3], lat_0=(polygon.bounds[1]+polygon.bounds[3])/2, lon_0=(polygon.bounds[0]+polygon.bounds[2])/2)
    
    project = partial(pyproj.transform, proj_wgs84, proj_aea)
    polygon_transformed = transform(project, polygon)
    return abs(polygon_transformed.area)

def convert_sqm_to_thai_unit(sqm):
    if sqm == 0:
        return "0 ไร่ 0 งาน 0 ตร.วา"
    rai = int(sqm // 1600)
    remain = sqm % 1600
    ngan = int(remain // 400)
    remain = remain % 400
    wa = remain / 4
    return f"{rai} ไร่ {ngan} งาน {wa:.1f} ตร.วา"

# --- ระบบบันทึกพิกัดในความจำ (Session State) ---
if 'survey_points' not in st.session_state:
    st.session_state.survey_points = []
if 'calculated_area' not in st.session_state:
    st.session_state.calculated_area = 0.0
if 'show_result' not in st.session_state:
    st.session_state.show_result = False

current_count = len(st.session_state.survey_points)

# --- ส่วนที่ 1: ปุ่มควบคุมและแดชบอร์ดแสดงผลพื้นที่ ---
st.markdown("### 🎛️ แผงควบคุมระบบรังวัดแม่นยำ")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    # ปุ่มกดบันทึกพิกัดมุมที่ดิน (ดักจับพิกัดจากเป้าเล็งตรงกลางแผนที่)
    if st.button("📍 1. บันทึกจุดเล็งปัจจุบัน ลงในระบบ", type="primary", use_container_width=True):
        if 'center_lat' in st.session_state and 'center_lng' in st.session_state:
            current_center = (st.session_state.center_lat, st.session_state.center_lng)
            if not st.session_state.survey_points or st.session_state.survey_points[-1] != current_center:
                st.session_state.survey_points.append(current_center)
                st.session_state.show_result = False # รีเซ็ตสถานะคำนวณ เพื่อให้กดคำนวณใหม่เมื่อปักครบ
                st.rerun()

with col_btn2:
    # ปุ่มสั่งคำนวณพื้นที่ (จะทำงานเมื่อสั่งกดเท่านั้น ป้องกันค่าดีดไปมา)
    if st.button("🧮 2. สั่งคำนวณผลพื้นที่แปลงที่ดิน", type="secondary", use_container_width=True):
        if current_count >= 3:
            st.session_state.calculated_area = calculate_polygon_area(st.session_state.survey_points)
            st.session_state.show_result = True
            st.rerun()
        else:
            st.error("❌ ต้องบันทึกหมุดมุมที่ดินให้ได้ 3 จุดขึ้นไปก่อน จึงจะกดคำนวณได้ครับ")

with col_btn3:
    if st.button("🔄 ล้างข้อมูลทั้งหมด เพื่อเริ่มวาดแปลงใหม่", use_container_width=True):
        st.session_state.survey_points = []
        st.session_state.calculated_area = 0.0
        st.session_state.show_result = False
        st.rerun()

# แผงแสดงผลคะแนนพื้นที่ (จะแสดงตัวเลขสรุปที่แน่นอนเมื่อกดปุ่ม คำนวณ แล้วเท่านั้น)
st.markdown("#### 📊 รายงานขนาดพื้นที่ดินทางการ")
card1, card2 = st.columns(2)

thai_unit = convert_sqm_to_thai_unit(st.session_state.calculated_area)

with card1:
    if st.session_state.show_result:
        st.success(f"แปลงที่ดินรูปทรง: {current_count} เหลี่ยม")
        st.metric(label="ขนาดพื้นที่ (หน่วยไทย)", value=thai_unit)
    else:
        st.info(f"สถานะ: กำลังจับข้อมูลรังวัด (บันทึกไปแล้ว {current_count} หมุด)")
        st.metric(label="ขนาดพื้นที่ (หน่วยไทย)", value="รอการกดคำนวณ...")

with card2:
    if st.session_state.show_result:
        st.metric(label="ขนาดพื้นที่ (หน่วยสากล)", value=f"{st.session_state.calculated_area:,.2f} ตร.ม.")
    else:
        st.metric(label="ขนาดพื้นที่ (หน่วยสากล)", value="รอการกดคำนวณ...")

st.markdown("---")

# --- ส่วนที่ 2: ระบบแผนที่ดาวเทียมเป้าเล็งตรงกลางจอ ---
st.markdown("### 🛰️ แผนที่ดาวเทียมพร้อมเป้าเล็งพิกัดความแม่นยำสูง")

# เลือกศูนย์กลางแผนที่
if current_count > 0:
    map_start = st.session_state.survey_points[-1]
elif 'center_lat' in st.session_state and st.session_state.center_lat is not None:
    map_start = [st.session_state.center_lat, st.session_state.center_lng]
else:
    map_start = [13.7563, 100.5018] # เปิดสแตนบายรอ GPS ดึงตัวเรา

m = folium.Map(
    location=map_start, 
    zoom_start=19, 
    max_zoom=22,   
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
    attr='Google'
)

# 🌟 1. ดึงชิปตำแหน่งเรียลไทม์ (โชว์จุดน้ำเงินห้ามคลาดเคลื่อน วิ่งตามตัวจริง)
folium.plugins = __import__('folium.plugins', fromlist=['LocateControl'])
folium.plugins.LocateControl(
    locateOptions={'enableHighAccuracy': True, 'maximumAge': 0, 'timeout': 5000},
    keepCurrentZoomLevel=True,
    setView='once', # ซูมหาตัวเราทันทีในเสี้ยววินาทีแรกที่เปิดแอป
    trackUserLocation=True, 
    title="พิกัดปัจจุบันของคุณ"
).add_to(m)

# 🌟 2. วาดหมุดสีส้มสำหรับจุดต่างๆ ที่เรากด "บันทึกพิกัด" ไปแล้ว
for idx, pt in enumerate(st.session_state.survey_points):
    folium.Marker(
        location=pt,
        popup=f"มุมที่ {idx+1}",
        icon=folium.Icon(color="orange", icon="cloud")
    ).add_to(m)

# 🌟 3. ลากเส้นโครงร่างสีแดงโชว์แนวแปลงที่ดินสด ๆ
if current_count >= 2:
    folium.Polygon(
        locations=st.session_state.survey_points,
        color="#FF0000",
        weight=4,
        fill=True if current_count >= 3 else False,
        fill_color="#FFFF00",
        fill_opacity=0.3
    ).add_to(m)

# เรนเดอร์แผนที่บนหน้าเว็บ
map_data = st_folium(m, width="100%", height=500, key=f"precision_map_{current_count}")

# 🌟 4. ดักจับค่ากึ่งกลางหน้าจอแผนที่ตลอดเวลาเมื่อเราเลื่อนจอหรือเดินขยับ (ใช้เป็นเป้าเล็ง)
if map_data and map_data.get("center"):
    st.session_state.center_lat = map_data["center"]["lat"]
    st.session_state.center_lng = map_data["center"]["lng"]

# สร้างสัญลักษณ์กากบาท (Crosshair) ล็อกไว้กลางหน้าจอแผนที่เพื่อเป็นเป้าเล็งชี้นิ้วจุดวัดค่า
st.markdown("""
    <style>
    .stFolium { position: relative; }
    .stFolium::after {
        content: "➕";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 32px;
        color: #FF0000;
        text-shadow: 0px 0px 4px #FFFFFF;
        pointer-events: none;
        z-index: 9999;
    }
    </style>
""", unsafe_allow_html=True)
