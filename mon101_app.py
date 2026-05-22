import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
from shapely.ops import transform

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="GPS 4-Point Area Measure", layout="wide", page_icon="📐")

st.title("📐 แอปวัดพื้นที่อัจฉริยะ (ปักหมุด 4 จุดสร้างกรอบ)")
st.write("วิธีใช้: ใช้นิ้วจิ้มบนแผนที่ด้านล่างให้ครบ 4 มุมของที่ดิน ระบบจะลากเส้นสร้างกรอบและคำนวณพื้นที่ให้ทันที")

# ฟังก์ชันคำนวณพื้นที่ผิวโลก (ตารางเมตร) จากพิกัด Lat/Lon
def calculate_polygon_area(lat_lons):
    if len(lat_lons) < 3:
        return 0.0
    # แปลงพิกัดเป็น Lon, Lat สำหรับ Shapely
    lon_lats = [(lon, lat) for lat, lon in lat_lons]
    polygon = Polygon(lon_lats)
    
    # คำนวณพื้นที่แบบอ้างอิงส่วนโค้งโลกจริง (Equal Area Projection)
    proj_wgs84 = pyproj.Proj(init='epsg:4326')
    proj_aea = pyproj.Proj(proj='aea', lat_1=polygon.bounds[1], lat_2=polygon.bounds[3], lat_0=(polygon.bounds[1]+polygon.bounds[3])/2, lon_0=(polygon.bounds[0]+polygon.bounds[2])/2)
    
    project = partial(pyproj.transform, proj_wgs84, proj_aea)
    polygon_transformed = transform(project, polygon)
    return abs(polygon_transformed.area)

# ฟังก์ชันแปลง ตร.ม. -> ไร่-งาน-ตารางวา
def convert_sqm_to_thai_unit(sqm):
    if sqm == 0:
        return "0 ไร่ 0 งาน 0 ตร.วา"
    rai = int(sqm // 1600)
    remain = sqm % 1600
    ngan = int(remain // 400)
    remain = remain % 400
    wa = remain / 4
    return f"{rai} ไร่ {ngan} งาน {wa:.1f} ตร.วา"

# บันทึกสถานะจุดพิกัดในระบบ (Session State)
if 'survey_points' not in st.session_state:
    st.session_state.survey_points = []

current_count = len(st.session_state.survey_points)

# --- ส่วนที่ 1: หน้าจอแสดงผลคะแนนและสถานะ ---
st.markdown("### 📊 ผลการสำรวจกรอบพื้นที่")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if current_count < 4:
        st.warning(f"📍 ปักหมุดไปแล้ว {current_count} / 4 จุด (กรุณาจิ้มเพิ่มให้ครบ)")
    else:
        st.success("✅ ครบ 4 จุด สร้างกรอบพื้นที่สำเร็จ!")

# คำนวณพื้นที่เมื่อได้พิกัด
area_sqm = calculate_polygon_area(st.session_state.survey_points)
thai_unit = convert_sqm_to_thai_unit(area_sqm)

with col2:
    st.metric(label="พื้นที่ในกรอบ (หน่วยไทย)", value=thai_unit)
with col3:
    st.metric(label="พื้นที่ในกรอบ (หน่วยสากล)", value=f"{area_sqm:,.2f} ตร.ม.")

# ปุ่มสำหรับล้างข้อมูลเพื่อเริ่มลากกรอบใหม่
if st.button("🔄 ล้างข้อมูลหมุดทั้งหมด เพื่อเริ่มวาดกรอบใหม่", type="primary"):
    st.session_state.survey_points = []
    st.rerun()

st.markdown("---")

# --- ส่วนที่ 2: แผนที่สำหรับกดจิ้มลากเส้น ---
st.markdown("### 🗺️ แผนที่ระบุพิกัด (ใช้นิ้วจิ้มเพื่อปักหมุด)")

# ตั้งศูนย์กลางแผนที่ไปที่จุดแรกที่จิ้ม หรือถ้าไม่มีให้ตั้งที่กรุงเทพฯ
map_center = st.session_state.survey_points[0] if current_count > 0 else [13.7563, 100.5018]
m = folium.Map(location=map_center, zoom_start=16, control_scale=True)

# วาดหมุดทีละจุดที่ผู้ใช้จิ้ม
for idx, pt in enumerate(st.session_state.survey_points):
    folium.Marker(
        location=pt, 
        popup=f"มุมที่ {idx+1}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

# ถ้าปักหมุดตั้งแต่ 2 จุดขึ้นไป ให้ลากเส้นเชื่อม (ถ้าครบ 4 จุดจะปิดกรอบเป็นสี่เหลี่ยมระบายสี)
if current_count >= 2:
    folium.Polygon(
        locations=st.session_state.survey_points,
        color="blue",
        weight=3,
        fill=True if current_count == 4 else False, # ถ้ารบ 4 จุดให้แรเงาพื้นที่ข้างใน
        fill_color="cyan",
        fill_opacity=0.4
    ).add_to(m)

# แรนเดอร์แผนที่บนเว็บ
map_data = st_folium(m, width="100%", height=500)

# ดักจับการคลิก/จิ้มบนแผนที่
if map_data and map_data.get("last_clicked"):
    clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
    
    # ป้องกันการบันทึกจุดซ้ำและจำกัดไว้แค่ 4 จุดเท่านั้น
    if current_count < 4:
        if not st.session_state.survey_points or st.session_state.survey_points[-1] != clicked_coords:
            st.session_state.survey_points.append(clicked_coords)
            st.rerun()
