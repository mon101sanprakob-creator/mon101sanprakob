import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
from shapely.ops import transform

# ตั้งค่าหน้าเว็บให้เต็มจอและแสดงผลได้ดีกลางแดด
st.set_page_config(page_title="Realtime GPS Measure", layout="wide", page_icon="🛰️")

st.title("🛰️ แอปวัดที่ดินดาวเทียมพิกัดจริง (Realtime Lat/Lng)")
st.write("ระบบจะดึงค่าละติจูด/ลองจิจูดจริงจากดาวเทียม ณ ตำแหน่งที่คุณยืนอยู่มาเปิดแผนที่ทันที โดยไม่ผ่านกรุงเทพฯ")

# --- ฟังก์ชันคำนวณพื้นที่และการแปลงหน่วย ---
def calculate_polygon_area(lat_lons):
    if len(lat_lons) < 3:
        return 0.0
    lon_lats = [(lon, lat) for lat, lon in lat_lons]
    polygon = Polygon(lon_lats)
    
    # คำนวณตามส่วนโค้งโลกจริง แม่นยำสูง
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

# --- ระบบบันทึกพิกัดในหน่วยความจำ (Session State) ---
if 'survey_points' not in st.session_state:
    st.session_state.survey_points = []
if 'calculated_area' not in st.session_state:
    st.session_state.calculated_area = 0.0
if 'show_result' not in st.session_state:
    st.session_state.show_result = False

# ส่วนเก็บพิกัดละติจูด/ลองจิจูดจริงของตัวผู้ใช้
if 'device_lat' not in st.session_state:
    st.session_state.device_lat = None
if 'device_lng' not in st.session_state:
    st.session_state.device_lng = None

current_count = len(st.session_state.survey_points)

# 🌟 กลไกพิเศษ: บังคับให้เบราว์เซอร์อ่านค่าพิกัดโลกจริง (Lat/Lng) จากชิป GPS ก่อนเริ่มวาดส่วนอื่น
if st.session_state.device_lat is None:
    st.markdown("""
        <script>
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                // ส่งค่าพิกัดจริงฝังกลับเข้ามาที่ URL ของระบบ
                const url = new URL(window.location.href);
                url.searchParams.set('gps_lat', lat);
                url.searchParams.set('gps_lng', lng);
                window.parent.location.href = url.toString();
            },
            function(error) { console.error(error); },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
        </script>
    """, unsafe_allow_html=True)
    
    # อ่านพิกัดจาก URL ที่ JavaScript ดักจับมาได้
    query_params = st.query_params
    if 'gps_lat' in query_params and 'gps_lng' in query_params:
        st.session_state.device_lat = float(query_params['gps_lat'])
        st.session_state.device_lng = float(query_params['gps_lng'])
        st.rerun()

# --- แผงแสดงผลพิกัดดาวเทียมจริง ---
st.markdown("### 📊 ค่าพิกัดดาวเทียมและการคำนวณ")
col_latlng, col_thai, col_sqm = st.columns([1.2, 1, 1])

with col_latlng:
    if st.session_state.device_lat is not None:
        st.success(f"📡 พิกัดโลกจริงของคุณในขณะนี้:\nLat: {st.session_state.device_lat:.6f}\nLng: {st.session_state.device_lng:.6f}")
    else:
        st.info("🔄 กำลังเชื่อมต่อสัญญาณดาวเทียมหาตำแหน่งจริง...")

# คำนวณพื้นที่
area_sqm = calculate_polygon_area(st.session_state.survey_points) if st.session_state.show_result else st.session_state.calculated_area
thai_unit = convert_sqm_to_thai_unit(area_sqm)

with col_thai:
    if st.session_state.show_result:
        st.metric(label="ขนาดพื้นที่ (หน่วยไทย)", value=thai_unit)
    else:
        st.metric(label="ขนาดพื้นที่ (หน่วยไทย)", value="รอการกดคำนวณ...")
with col_sqm:
    if st.session_state.show_result:
        st.metric(label="ขนาดพื้นที่ (หน่วยสากล)", value=f"{area_sqm:,.2f} ตร.ม.")
    else:
        st.metric(label="ขนาดพื้นที่ (หน่วยสากล)", value="รอการกดคำนวณ...")

# --- ปุ่มควบคุมระบบรังวัด ---
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("📍 1. บันทึกจุดเป้าเล็งปัจจุบัน", type="primary", use_container_width=True):
        if 'center_lat' in st.session_state and 'center_lng' in st.session_state:
            current_center = (st.session_state.center_lat, st.session_state.center_lng)
            if not st.session_state.survey_points or st.session_state.survey_points[-1] != current_center:
                st.session_state.survey_points.append(current_center)
                st.session_state.show_result = False
                st.rerun()
with c2:
    if st.button("🧮 2. สั่งคำนวณพื้นที่ (ปักกี่จุดก็ได้)", type="secondary", use_container_width=True):
        if current_count >= 3:
            st.session_state.calculated_area = calculate_polygon_area(st.session_state.survey_points)
            st.session_state.show_result = True
            st.rerun()
        else:
            st.error("❌ ต้องบันทึกหมุดมุมที่ดินอย่างน้อย 3 จุดขึ้นไปครับ")
with c3:
    if st.button("🔄 ล้างหมุดทั้งหมด เพื่อเริ่มแปลงใหม่", use_container_width=True):
        st.session_state.survey_points = []
        st.session_state.calculated_area = 0.0
        st.session_state.show_result = False
        st.rerun()

st.markdown("---")

# --- ส่วนแผนที่ดาวเทียมล็อกพิกัดเวลาจริง ---
st.markdown("### 🛰️ แผนที่ดาวเทียมโลกจริงเรียลไทม์")

# ตั้งพิกัดเริ่มต้นแผนที่: ถ้าดึงพิกัดตัวตนจริงได้แล้ว ให้ล็อกเข้าที่ตัวเราทันทีตั้งแต่เสี้ยววินาทีแรก!
if current_count > 0:
    map_start = st.session_state.survey_points[-1]
elif st.session_state.device_lat is not None:
    map_start = [st.session_state.device_lat, st.session_state.device_lng]
else:
    map_start = [13.7563, 100.5018] # กรณีสัญญาณหลุดชั่วคราว

m = folium.Map(
    location=map_start, 
    zoom_start=19, # ซูมระดับหลังคาบ้านเห็นแนวเขตชัดเจน
    max_zoom=22,   
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', # ภาพถ่ายดาวเทียมจริงของ Google Maps
    attr='Google'
)

# ระบบจุดน้ำเงิน GPS เรียลไทม์ เดินไปไหนจุดขยับตามห้ามคลาดเคลื่อน
folium.plugins = __import__('folium.plugins', fromlist=['LocateControl'])
folium.plugins.LocateControl(
    locateOptions={'enableHighAccuracy': True, 'maximumAge': 0, 'timeout': 10000},
    keepCurrentZoomLevel=True,
    setView='always', # ล็อกหน้าจอให้อยู่กับพิกัดจริงตามเวลาจริงตลอดเวลา จนกว่าจะเริ่มปักหมุด
    trackUserLocation=True,
    title="พิกัดจริงของคุณ"
).add_to(m)

# วาดหมุดรังวัดสีส้มที่เรากดบันทึก
for idx, pt in enumerate(st.session_state.survey_points):
    folium.Marker(
        location=pt,
        popup=f"มุมที่ {idx+1}",
        icon=folium.Icon(color="orange", icon="cloud")
    ).add_to(m)

# ลากเส้นกรอบที่ดินรูปหลายเหลี่ยม (เช่น 8 เหลี่ยม)
if current_count >= 2:
    folium.Polygon(
        locations=st.session_state.survey_points,
        color="#FF0000",       # เส้นขอบสีแดงสดชัดเจน
        weight=4,
        fill=True if current_count >= 3 else False,
        fill_color="#FFFF00",  # สีเหลืองโปร่งแสงระบายข้างในแปลง
        fill_opacity=0.3
    ).add_to(m)

# เรนเดอร์แผนที่
map_data = st_folium(m, width="100%", height=520, key=f"realtime_map_{current_count}")

# อัปเดตพิกัดกึ่งกลางหน้าจอ (เป้าเล็งกากบาท)
if map_data and map_data.get("center"):
    st.session_state.center_lat = map_data["center"]["lat"]
    st.session_state.center_lng = map_data["center"]["lng"]

# สร้างสัญลักษณ์เป้าเล็งกากบาทสีแดงล็อกไว้ตรงกลางแผนที่ เพื่อใช้ชี้จุดรังวัด
st.markdown("""
    <style>
    .stFolium { position: relative; }
    .stFolium::after {
        content: "➕";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 30px;
        color: #FF0000;
        text-shadow: 0px 0px 4px #FFFFFF;
        pointer-events: none;
        z-index: 9999;
    }
    </style>
""", unsafe_allow_html=True)
