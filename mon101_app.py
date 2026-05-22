import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
from shapely.ops import transform

# ตั้งค่าหน้าเว็บให้เต็มจอ
st.set_page_config(page_title="GPS Multi-Point Measure", layout="wide", page_icon="📐")

st.title("📐 แอปวัดที่ดินอัจฉริยะ (รูปหลายเหลี่ยม & พิกัดเรียลไทม์)")
st.write("วิธีใช้: ใช้นิ้วจิ้มบนแผนที่ดาวเทียมตามมุมที่ดินไปเรื่อย ๆ (กี่จุดก็ได้ เช่น 8 เหลี่ยม) ระบบจะลากเส้นเชื่อมกันและคำนวณพื้นที่ให้ทันที")

# --- ฟังก์ชันคำนวณพื้นที่และการแปลงหน่วย ---
def calculate_polygon_area(lat_lons):
    if len(lat_lons) < 3:
        return 0.0
    lon_lats = [(lon, lat) for lat, lon in lat_lons]
    polygon = Polygon(lon_lats)
    
    # คำนวณแบบอ้างอิงส่วนโค้งโลกจริง ไม่คลาดเคลื่อน
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

# --- บันทึกพิกัดในระบบ (Session State) ---
if 'survey_points' not in st.session_state:
    st.session_state.survey_points = []

current_count = len(st.session_state.survey_points)

# --- ส่วนที่ 1: แผงแดชบอร์ดแสดงผลคะแนนและพื้นที่ ---
st.markdown("### 📊 ผลการคำนวณพื้นที่แปลงที่ดิน")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if current_count < 3:
        st.warning(f"📍 ปักไปแล้ว {current_count} จุด (ต้องปักอย่างน้อย 3 จุดขึ้นไปเพื่อคำนวณพื้นที่)")
    else:
        st.success(f"✅ แปลงที่ดินรูปทรง {current_count} เหลี่ยม")

area_sqm = calculate_polygon_area(st.session_state.survey_points)
thai_unit = convert_sqm_to_thai_unit(area_sqm)

with col2:
    st.metric(label="พื้นที่ในกรอบ (หน่วยไทย)", value=thai_unit)
with col3:
    st.metric(label="พื้นที่ในกรอบ (หน่วยสากล)", value=f"{area_sqm:,.2f} ตร.ม.")

# ปุ่มล้างข้อมูลเพื่อเริ่มจับแปลงใหม่
if st.button("🔄 ล้างหมุดทั้งหมด เพื่อเริ่มวาดกรอบใหม่", type="primary", use_container_width=True):
    st.session_state.survey_points = []
    st.rerun()

st.markdown("---")

# --- ส่วนที่ 2: แผนที่ภาพถ่ายดาวเทียมความละเอียดสูง ---
st.markdown("### 🛰️ แผนที่ดาวเทียม (ใช้นิ้วจิ้มเพื่อลากเส้นเชื่อมโยง)")

# ตั้งค่าจุดเริ่มต้นแผนที่ (ยึดตามหมุดแรกที่จิ้ม ถ้าไม่มีให้เปิดที่พิกัดกลางประเทศสแตนบายไว้ก่อน)
map_center = st.session_state.survey_points[0] if current_count > 0 else [13.7563, 100.5018]

m = folium.Map(
    location=map_center, 
    zoom_start=17, 
    max_zoom=22,   
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', # ภาพถ่ายดาวเทียม Google คมชัดเห็นหลังคาบ้าน
    attr='Google'
)

# 🌟 ระบบติดตามตัวเราเรียลไทม์ (ทำงานทันทีเมื่อเปิดแอปผ่านเมนูบนแผนที่)
# ระบบนี้จะขอสิทธิ์ GPS ตรงๆ และวาด "จุดน้ำเงินเรียลไทม์" บนหน้าจอ ขยับตามตัวคุณตลอดเวลา
folium.plugins = __import__('folium.plugins', fromlist=['LocateControl'])
folium.plugins.LocateControl(
    locateOptions={'enableHighAccuracy': True, 'maximumAge': 0}, # ใช้ชิป GPS สดหน้างาน
    keepCurrentZoomLevel=True,
    setView='once', # เด้งหน้าจอไปหาตัวคุณทันทีที่ระบบจับพิกัดได้ครั้งแรก
    trackUserLocation=True, # เดินไปไหนจุดน้ำเงินเดินตามเรียลไทม์
    title="คลิกตรงนี้เพื่อล็อกพิกัดตัวคุณ"
).add_to(m)

# วาดหมุดสีส้มทีละจุดที่เราใช้นิ้วกดเองรอบที่ดิน
for idx, pt in enumerate(st.session_state.survey_points):
    folium.Marker(
        location=pt,
        popup=f"มุมที่ {idx+1}",
        icon=folium.Icon(color="orange", icon="info-sign")
    ).add_to(m)

# 🌟 ลากเส้นขอบและแรเงาพื้นที่ (รองรับรูปหลายเหลี่ยม เช่น 8 เหลี่ยม)
# ยิ่งจิ้มเพิ่ม เส้นสีแดงจะลากคลุมตามนิ้วไปเรื่อยๆ และจะเริ่มแรเงาสีเหลืองใสให้เห็นภาพพื้นที่ตั้งแต่จุดที่ 3 เป็นต้นไป
if current_count >= 2:
    folium.Polygon(
        locations=st.session_state.survey_points,
        color="#FF0000",       # เส้นกรอบสีแดงสดตัดกับดาวเทียม
        weight=4,              # ความหนาของเส้นกรอบ
        fill=True if current_count >= 3 else False, 
        fill_color="#FFFF00",  # แรเงาสีเหลืองโปร่งแสงด้านในกรอบมุด
        fill_opacity=0.35      # ความโปร่งแสงเพื่อให้ยังมองเห็นหลังคาบ้าน
    ).add_to(m)

# เรนเดอร์แผนที่บนหน้าเว็บ
map_data = st_folium(m, width="100%", height=550, key=f"map_survey_{current_count}")

# ระบบดักจับการใช้นิ้วจิ้มหน้าจอเพื่อเพิ่มหมุด (ปักกี่จุดก็ได้ ไม่จำกัด)
if map_data and map_data.get("last_clicked"):
    clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
    
    # ป้องกันค่าพิกัดซ้ำซ้อนตอนรีเฟรชหน้าจอ
    if not st.session_state.survey_points or st.session_state.survey_points[-1] != clicked_coords:
        st.session_state.survey_points.append(clicked_coords)
        st.rerun()
