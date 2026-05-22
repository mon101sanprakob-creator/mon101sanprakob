import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
from shapely.ops import transform

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(page_title="GPS Area Measure & Survey", layout="wide", page_icon="🗺️")

st.title("🗺️ Web GPS แอปวัดพื้นที่และสำรวจพิกัด 2 ระบบ")
st.write("คำนวณพื้นที่อย่างละเอียดเป็นหน่วย ไร่-งาน-ตารางวา และตารางเมตร")

# ฟังก์ชันทางคณิตศาสตร์: คำนวณพื้นที่ผิวโลก (ตร.ม.) จากพิกัด Lat/Lon (ป้องกันการเพี้ยนจากส่วนโค้งของโลก)
def calculate_polygon_area(lat_lons):
    if len(lat_lons) < 3:
        return 0.0
    # แปลงพิกัด Lon, Lat เป็นรูปหลายเหลี่ยม
    lon_lats = [(lon, lat) for lat, lon in lat_lons]
    polygon = Polygon(lon_lats)
    
    # ใช้การโปรเจกชันแผ่นที่ระบุพื้นที่เท่าจริง (Equal Area Projection) เพื่อความแม่นยำ
    proj_wgs84 = pyproj.Proj(init='epsg:4326')
    proj_aea = pyproj.Proj(proj='aea', lat_1=polygon.bounds[1], lat_2=polygon.bounds[3], lat_0=(polygon.bounds[1]+polygon.bounds[3])/2, lon_0=(polygon.bounds[0]+polygon.bounds[2])/2)
    
    project = partial(pyproj.transform, proj_wgs84, proj_aea)
    polygon_transformed = transform(project, polygon)
    return abs(polygon_transformed.area)

# ฟังก์ชันแปลงตารางเมตร -> ไร่-งาน-ตารางวา
def convert_sqm_to_thai_unit(sqm):
    if sqm == 0:
        return "0 ไร่ 0 งาน 0 ตร.วา"
    rai = int(sqm // 1600)
    remain = sqm % 1600
    ngan = int(remain // 400)
    remain = remain % 400
    wa = remain / 4
    return f"{rai} ไร่ {ngan} งาน {wa:.1f} ตร.วา"

# --- ส่วนของการจัดการสถานข้อมูล (State) ---
if 'points' not in st.session_state:
    st.session_state.points = []

# --- แถบควบคุมฝั่งซ้าย (Sidebar): ตัวเลือกอินพุตและโหมดการวัด ---
st.sidebar.header("⚙️ การตั้งค่าและอินพุต")

# 1. ตัวเลือกโหมดการทำงาน
mode = st.sidebar.radio(
    "เลือกโหมดการวัดพื้นที่:",
    ("ระบบที่ 1: จิ้มปักหมุดบนแผนที่", "ระบบที่ 2: กรอกพิกัดด้วยตัวเอง")
)

# 2. ตัวเลือกหน่วยวัดที่ต้องการเน้นแสดงผล
unit_choice = st.sidebar.selectbox(
    "เลือกหน่วยวัดที่ต้องการแสดงผล:",
    ["แสดงทุกหน่วยอย่างละเอียด", "ไร่", "งาน", "ตารางวา", "ตารางเมตร"]
)

st.sidebar.markdown("---")

# ฟังก์ชันการทำงานของแต่ละระบบ
if mode == "ระบบที่ 1: จิ้มปักหมุดบนแผนที่":
    st.sidebar.subheader("💡 วิธีใช้งานโหมดจิ้ม")
    st.sidebar.info("1. คลิกเมาส์หรือใช้นิ้วจิ้มบนแผนที่ขวาเพื่อปักหมุด\n2. ปักหมุดอย่างน้อย 3 จุดขึ้นไปเพื่อสร้างแปลงพื้นที่\n3. สามารถกดปุ่มเคลียร์ด้านล่างเพื่อเริ่มใหม่ได้")
    
    if st.sidebar.button("🗑️ ล้างข้อมูลหมุดทั้งหมด", use_container_width=True):
        st.session_state.points = []
        st.rerun()

elif mode == "ระบบที่ 2: กรอกพิกัดด้วยตัวเอง":
    st.sidebar.subheader("📥 ช่องกรอกพิกัดสำรวจ (Manual Input)")
    
    # อินพุตกรอกพิกัดรายจุด
    input_lat = st.sidebar.number_input("ละติจูด (Latitude) เช่น 13.7563", format="%.6f", value=13.756300)
    input_lon = st.sidebar.number_input("ลองจิจูด (Longitude) เช่น 100.5018", format="%.6f", value=100.501800)
    
    if st.sidebar.button("➕ เพิ่มพิกัดนี้เข้าสู่ระบบ", use_container_width=True):
        st.session_state.points.append((input_lat, input_lon))
        st.success(f"เพิ่มพิกัด ({input_lat}, {input_lon}) เรียบร้อย!")
        st.rerun()
        
    if st.sidebar.button("🗑️ ลบจุดล่าสุด", use_container_width=True):
        if st.session_state.points:
            st.session_state.points.pop()
            st.rerun()

# --- หน้าจอหลักฝั่งขวา: แสดงผลการคำนวณและแผนที่ ---

# คำนวณพื้นที่ปัจจุบัน
area_sqm = calculate_polygon_area(st.session_state.points)

# ส่วนแสดงผลลัพธ์ (Result Dashboard)
st.subheader("📊 ผลการคำนวณพื้นที่")
col1, col2 = st.columns(2)

with col1:
    if unit_choice == "แสดงทุกหน่วยอย่างละเอียด" or unit_choice == "ตารางเมตร":
        st.metric(label="พื้นที่ในหน่วยสากล", value=f"{area_sqm:,.2f} ตร.ม.")
with col2:
    if unit_choice == "แสดงทุกหน่วยอย่างละเอียด" or unit_choice in ["ไร่", "งาน", "ตารางวา"]:
        thai_unit_str = convert_sqm_to_thai_unit(area_sqm)
        st.metric(label="พื้นที่ในหน่วยไทย", value=thai_unit_str)

# แสดงตารางพิกัดอินพุตที่ถูกบันทึกไว้
if st.session_state.points:
    with st.expander("📋 รายชื่อพิกัดที่บันทึกอยู่ตอนนี้"):
        st.write(st.session_state.points)

st.markdown("---")

# --- การวาดแผ่นที่แผนที่เชิงโต้ตอบ (Folium Map) ---
st.subheader("🗺️ แผนที่สำรวจบริเวณ")

# ตั้งค่าจุดศูนย์กลางแผนที่ (ถ้ามีจุดให้โฟกัสที่จุดแรก ถ้าไม่มีให้โฟกัสที่กรุงเทพฯ)
center_location = st.session_state.points[0] if st.session_state.points else [13.7563, 100.5018]
m = folium.Map(location=center_location, zoom_start=16, control_scale=True)

# วาดหมุดและเส้นพื้นที่เชื่อมโยงกัน
for idx, pt in enumerate(st.session_state.points):
    folium.Marker(location=pt, popup=f"จุดที่ {idx+1}").add_to(m)

if len(st.session_state.points) >= 3:
    folium.Polygon(
        locations=st.session_state.points,
        color="green",
        weight=3,
        fill=True,
        fill_color="limegreen",
        fill_opacity=0.4
    ).add_to(m)

# ดักจับเหตุการณ์คลิกจิ้มบนแผ่นที่ (สำหรับโหมดที่ 1)
map_data = st_folium(m, width="100%", height=500)

if mode == "ระบบที่ 1: จิ้มปักหมุดบนแผนที่" and map_data and map_data.get("last_clicked"):
    clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
    
    # ป้องกันไม่ให้แอปบันทึกจุดซ้ำซ้อนตอนโหลดหน้าใหม่
    if not st.session_state.points or st.session_state.points[-1] != clicked_coords:
        st.session_state.points.append(clicked_coords)
        st.rerun()
