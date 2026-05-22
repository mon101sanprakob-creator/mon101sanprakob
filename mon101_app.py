import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
from shapely.ops import transform

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="GPS Area Measure App", layout="wide", page_icon="🗺️")

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

# --- ระบบจัดการสถานะ (Session State) ---
if 'app_page' not in st.session_state:
    st.session_state.app_page = 'main_menu'  # หน้าเริ่มต้น: 'main_menu' หรือ 'map_screen'
if 'survey_points' not in st.session_state:
    st.session_state.survey_points = []
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = None
if 'user_lng' not in st.session_state:
    st.session_state.user_lng = None

# ==========================================
# หน้าที่ 1: หน้าแรก (เลือกเมนูและขอสิทธิ์ GPS)
# ==========================================
if st.session_state.app_page == 'main_menu':
    st.title("🗺️ ยินดีต้อนรับสู่แอปวัดพื้นที่อัจฉริยะ")
    st.write("ระบบรังวัดที่ดินภาพดาวเทียมความละเอียดสูง รองรับรูปแปลงที่ดินทุกรูปแบบ (ไม่จำกัดจำนวนเหลี่ยม)")
    
    st.markdown("---")
    st.subheader("📌 ขั้นตอนการใช้งานก่อนเริ่มรังวัด")
    st.info("""
    1. กดปุ่ม **'เปิดตำแหน่งเรียลไทม์ และเปิดสิทธิ์ GPS'** ด้านล่าง
    2. หน้าจอมือถือจะถามขอสิทธิ์เข้าถึงตำแหน่ง ให้กด **'อนุญาต (Allow)'** และเลือก **'ตำแหน่งแม่นยำ (Precise Location)'**
    3. เมื่อระบบดึงพิกัดสำเร็จ หน้าจอจะแสดงตำแหน่งของคุณ จากนั้นกดปุ่ม **'เข้าสู่หน้าจอแผนที่'** เพื่อเริ่มวัดได้ทันที
    """)
    
    # ปุ่มเปิดสัญญาณ GPS เรียลไทม์ (ใช้ JavaScript ดักจับค่าพิกัดสดจากชิปมือถือ)
    if st.button("🎯 1. เปิดตำแหน่งเรียลไทม์ และเปิดสิทธิ์ GPS", type="primary", use_container_width=True):
        st.markdown("""
            <script>
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const url = new URL(window.location.href);
                    url.searchParams.set('lat', lat);
                    url.searchParams.set('lng', lng);
                    window.parent.location.href = url.toString();
                },
                function(error) { alert("กรุณาเปิด GPS บนมือถือและอนุญาตสิทธิ์ในเบราว์เซอร์"); },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
            </script>
        """, unsafe_allow_html=True)

    # ดักรับพิกัดที่ส่งกลับมาจาก JavaScript
    query_params = st.query_params
    if 'lat' in query_params and 'lng' in query_params:
        st.session_state.user_lat = float(query_params['lat'])
        st.session_state.user_lng = float(query_params['lng'])
        
    # แสดงสถานะพิกัดปัจจุบันให้ผู้ใช้มั่นใจว่าตรงแล้ว
    if st.session_state.user_lat is not None:
        st.success(f"✅ ดึงพิกัดเรียลไทม์สำเร็จ! ตำแหน่งปัจจุบันของคุณ: Lat {st.session_state.user_lat:.5f}, Lng {st.session_state.user_lng:.5f}")
        
        # เมื่อพร้อมแล้วให้กดปุ่มนี้เพื่อเปลี่ยนหน้าไปแผนที่
        if st.button("🚀 2. เข้าสู่หน้าจอแผนที่เพื่อเริ่มวัดพื้นที่", type="secondary", use_container_width=True):
            st.session_state.app_page = 'map_screen'
            st.rerun()
    else:
        st.warning("⏳ รอการกดปุ่มและแชร์สัญญาณ GPS ด้านบน...")

# ==========================================
# หน้าที่ 2: หน้าจอแผนที่รังวัดดาวเทียม (ไม่จำกัดจำนวนจุด)
# ==========================================
elif st.session_state.app_page == 'map_screen':
    st.title("📐 หน้าจอแผนที่สำรวจพื้นที่ดาวเทียม")
    st.write("วิธีใช้: ใช้นิ้วจิ้มบนแผนที่ตามมุมที่ดินไปเรื่อย ๆ (กี่จุดก็ได้) เส้นจะลากหากันและระบายสีคำนวณพื้นที่ให้อัตโนมัติ")
    
    current_count = len(st.session_state.survey_points)
    
    # แผงแดชบอร์ดแสดงคะแนนพื้นที่
    st.markdown("### 📊 ผลการคำนวณพื้นที่เรียลไทม์")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_count < 3:
            st.warning(f"📍 ปักหมุดไปแล้ว {current_count} จุด (ต้องปักอย่างน้อย 3 จุดขึ้นไป ระบบจึงจะเริ่มคิดพื้นที่)")
        else:
            st.success(f"✅ ปักหมุดไปแล้ว {current_count} จุด (รูปแปลงที่ดิน {current_count} เหลี่ยม)")
            
    area_sqm = calculate_polygon_area(st.session_state.survey_points)
    thai_unit = convert_sqm_to_thai_unit(area_sqm)
    
    with col2:
        st.metric(label="พื้นที่ในกรอบ (หน่วยไทย)", value=thai_unit)
    with col3:
        st.metric(label="พื้นที่ในกรอบ (หน่วยสากล)", value=f"{area_sqm:,.2f} ตร.ม.")
        
    # ปุ่มควบคุมต่าง ๆ
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 ล้างหมุดทั้งหมดเพื่อเริ่มวาดแปลงใหม่", type="primary", use_container_width=True):
            st.session_state.survey_points = []
            st.rerun()
    with c2:
        if st.button("⬅️ ย้อนกลับไปหน้าแรก", use_container_width=True):
            st.session_state.app_page = 'main_menu'
            st.rerun()
            
    st.markdown("---")
    
    # ตั้งศูนย์กลางแผนที่ดาวเทียมไปยังพิกัดตัวเราที่ได้มาจากหน้าแรกทันที
    if current_count > 0:
        map_center = st.session_state.survey_points[0]
    elif st.session_state.user_lat is not None and st.session_state.user_lng is not None:
        map_center = [st.session_state.user_lat, st.session_state.user_lng]
    else:
        map_center = [13.7563, 100.5018] # ค่าสำรองฉุกเฉิน
        
    m = folium.Map(
        location=map_center, 
        zoom_start=19, 
        max_zoom=22,   
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
        attr='Google'
    )
    
    # เปิดระบบโชว์จุดกลมน้ำเงินวิ่งตามตัวเราหน้างานจริงตลอดเวลา
    folium.plugins = __import__('folium.plugins', fromlist=['LocateControl'])
    folium.plugins.LocateControl(
        locateOptions={'enableHighAccuracy': True, 'maximumAge': 0},
        keepCurrentZoomLevel=True,
        setView='always', # ล็อกหน้าจอให้อยู่กับตัวเราจนกว่าจะกดจุดแรก
        trackUserLocation=True, 
        title="ตำแหน่งปัจจุบันของคุณ"
    ).add_to(m)
    
    # วาดหมุดสีส้มทีละจุดที่เราใช้นิ้วกดเอง
    for idx, pt in enumerate(st.session_state.survey_points):
        folium.Marker(
            location=pt,
            popup=f"มุมที่ {idx+1}",
            icon=folium.Icon(color="orange", icon="info-sign")
        ).add_to(m)
        
    # วาดเส้นและระบายสีพื้นที่เหลืองใส (ทำงานทันทีเมื่อปักหมุดตั้งแต่ 2 จุดขึ้นไป)
    if current_count >= 2:
        folium.Polygon(
            locations=st.session_state.survey_points,
            color="#FF0000",       # เส้นขอบสีแดงสดเห็นชัดบนดาวเทียม
            weight=4,              
            fill=True if current_count >= 3 else False, # ตั้งแต่ 3 จุดขึ้นไป แรเงาสีเหลืองด้านในให้ทันที
            fill_color="#FFFF00",  
            fill_opacity=0.35      
        ).add_to(m)
        
    # แรนเดอร์แผนที่
    map_data = st_folium(m, width="100%", height=550, key=f"survey_map_{current_count}")
    
    # ดักจับการจิ้มเพิ่มหมุดด้วยมือ (ไม่จำกัดจำนวนจุด)
    if map_data and map_data.get("last_clicked"):
        clicked_coords = (map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"])
        
        if not st.session_state.survey_points or st.session_state.survey_points[-1] != clicked_coords:
            st.session_state.survey_points.append(clicked_coords)
            st.rerun()
