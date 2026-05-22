import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
from shapely.ops import transform

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="GPS 4-Point Area Measure", layout="wide", page_icon="📐")

st.title("📐 แอปวัดพื้นที่อัจฉริยะ (ภาพดาวเทียมซูมพิกัดปัจจุบัน)")
st.write("วิธีใช้: ระบบจะซูมแผนที่ไปที่ตำแหน่งของคุณ (จุดน้ำเงิน) จากนั้นให้ใช้นิ้วจิ้มปักหมุด 4 มุม เพื่อลากเส้นคำนวณพื้นที่")

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

# --- บันทึกพิกัดจุดรังวัดในระบบ (Session State) ---
if 'survey_points' not in st.session_state:
    st.session_state.survey_points = []

current_count = len(st.session_state.survey_points)

# --- ส่วนที่ 1: หน้าจอแสดงผลคะแนนและสถานะ ---
st.markdown("### 📊 ผลการสำรวจกรอบพื้นที่")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if current_count < 4:
        st.warning(f"📍 ปักหมุดไปแล้ว {current_count} / 4 จุด (กรุณาจิ้มบนแผนที่ให้ครบ 4 จุดเพื่อปิดกรอบ)")
    else:
        st.success("✅ ครบ 4 จุด สร้างกรอบพื้นที่สำเร็จ!")

area_sqm = calculate_polygon_area(st.session_state.survey_points)
thai_unit = convert_sqm_to_thai_unit(area_sqm)

with col2:
    st.metric(label="พื้นที่ในกรอบ (หน่วยไทย)", value=thai_unit)
with col3:
    st.metric(label="พื้นที่ในกรอบ (หน่วยสากล)", value=f"{area_sqm:,.2f} ตร.ม.")

if st.button("🔄 ล้างข้อมูลหมุดทั้งหมด เพื่อเริ่มวาดกรอบใหม่", type="primary"):
    st.session_state.survey_points = []
    st.rerun()

st.markdown("---")

# --- ส่วนที่ 2: แผนที่ภาพถ่ายดาวเทียมความละเอียดสูง ---
st.markdown("### 🛰️ แผนที่ดาวเทียม (ใช้นิ้วจิ้มเพื่อปักหมุดรอบตัวคุณ)")

# ตั้งศูนย์กลางแผนที่ (ถ้ายังไม่จิ้ม จุดศูนย์กลางจะวิ่งไปหาพิกัดตัวเราผ่านระบบ LocateControl อัตโนมัติ)
map_center = st.session_state.survey_points[0] if current_count > 0 else [13.7563, 100.5018]

m = folium.Map(
    location=map_center, 
    zoom_start=19, # ซูมใกล้ระดับเห็นหลังคาบ้านทันที
    max_zoom=22,   
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', # Google Satellite Hybrid
    attr='Google'
)

# 🌟 ฟังก์ชันเปิดใช้งานระบบ GPS อัตโนมัติ (เปิดแอปปุ๊บ วิ่งหาตัวเราปั๊บ และโชว์จุดน้ำเงินทันที)
folium.plugins = __import__('folium.plugins', fromlist=['LocateControl'])
folium.plugins.LocateControl(
    locateOptions={'enableHighAccuracy': True, 'maximumAge': 0}, # ดึงค่าจริงหน้างานไม่ใช้ค่าเก่าค้าง
    keepCurrentZoomLevel=True,
    setView='once', # สั่งให้วิ่งไปหาตำแหน่งเราอัตโนมัติ "เฉพาะตอนเปิดแอปครั้งแรก"
    title="เลื่อนไปตำแหน่งปัจจุบันของคุณ"
).add_to(m)

# วาดหมุดสีส้มเด่นชัดที่เราจิ้มเองกับมือทีละจุด
for idx, pt in enumerate(st.session_state.survey_points):
    folium.Marker(
        location=pt,
        popup=f"มุมที่ {idx+1}",
        icon=folium.Icon(color="orange", icon="info-sign")
    ).add_to(m)

# ลากเส้นขอบและแรเงาพื้นที่ (เส้นขอบสีแดงสด พื้นที่ข้างในสีเหลืองใส)
if current_count >= 2:
    folium.Polygon(
        locations=st.session_state.survey_points,
        color="#FF0000",       
        weight=4,              
        fill=True if current_count == 4 else False, 
        fill_color="#FFFF00",  
        fill_opacity=0.35      
    ).add_to(m)

# แรนเดอร์แผนที่บนเว็บ Streamlit
map_data = st_folium(m, width="100%", height=550)

# ดักจับการจิ้มปักหมุดด้วยมือ
if map_data and map_data.get("last_clicked"):
    clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
    
    # จำกัดไว้สูงสุด 4 จุด และป้องกันจุดซ้ำซ้อน
    if current_count < 4:
        if not st.session_state.survey_points or st.session_state.survey_points[-1] != clicked_coords:
            st.session_state.survey_points.append(clicked_coords)
            st.rerun()
