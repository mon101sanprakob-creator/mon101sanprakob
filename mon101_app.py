import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from shapely.ops import transform
from geopy.geocoders import Nominatim
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")
st.title("📌 แอปวัดพื้นที่ดินดาวเทียมแบบระบุสถานที่")

# 1. โค้ดดึงค่าละติจูดและลองจิจูดปัจจุบันจากระบบ GPS ของอุปกรณ์โดยตรง
st.subheader("📡 ระบบดึงพิกัด GPS ปัจจุบัน")
with st.expander("คลิกที่นี่หากต้องการตรวจสอบหรือปรับเปลี่ยนพิกัดด้วยตนเอง", expanded=True):
    # ใช้ streamlit_js_eval ดึงพิกัดสดจากเบราว์เซอร์/มือถือ
    gps_data = streamlit_js_eval(data_name='geocode', reason='ขอเข้าถึงพิกัด GPS เพื่อระบุตำแหน่งบ้านของคุณ', key='get_current_gps')
    
    # ค่าเริ่มต้นกรณี GPS ยังไม่โหลด (พิกัดกลางประเทศไทย)
    default_lat, default_lng = 13.7563, 100.5018 
    
    if gps_data and 'coords' in gps_data:
        default_lat = gps_data['coords']['latitude']
        default_lng = gps_data['coords']['longitude']
        st.success("🎯 ดึงพิกัดจาก GPS ของคุณสำเร็จแล้ว!")
    else:
        st.warning("⚠️ กำลังค้นหาพิกัด GPS... (หากหมุดไม่ตรง โปรดกด 'อนุญาตแชร์ตำแหน่ง' ที่มุมบนของเบราว์เซอร์ หรือกรอกพิกัดเองด้านล่าง)")

    col1, col2 = st.columns(2)
    with col1:
        current_lat = st.number_input("ค่าละติจูด (Latitude)", value=default_lat, format="%.6f")
    with col2:
        current_lng = st.number_input("ค่าลองจิจูด (Longitude)", value=default_lng, format="%.6f")

# 2. ค้นหาชื่อสถานที่และที่อยู่จากพิกัด (Reverse Geocoding)
address_text = "กำลังค้นหาชื่อสถานที่จากฐานข้อมูล..."
try:
    geolocator = Nominatim(user_agent="mon101_land_measure_app")
    geo_location = geolocator.reverse(f"{current_lat}, {current_lng}", timeout=5)
    if geo_location:
        address_text = geo_location.address
except Exception:
    address_text = "แสดงผลบนแผนที่ดาวเทียมไฮบริดแล้ว"

st.info(f"🏠 **สถานที่ปัจจุบันของคุณ:** {address_text}")
st.caption("🗺️ **วิธีใช้นิ้วลากเส้น:** คลิกเครื่องมือรูปห้าเหลี่ยม (Draw a polygon) ที่มุมซ้ายบนของแผนที่ จากนั้นใช้นิ้วจิ้มลากเส้นล้อมรอบแปลงที่ดิน เมื่อเสร็จแล้วให้กดปุ่มคำนวณด้านล่าง")

# 3. สร้างแผนที่ดาวเทียมแบบ Hybrid (เห็นหลังคาบ้าน + เห็นชื่อสถานที่และถนน)
m = folium.Map(
    location=[current_lat, current_lng], 
    zoom_start=18, # ซูมใกล้ระดับเห็นหลังคาบ้าน
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', # lyrs=y คือ Google Satellite Hybrid (ดาวเทียม + ชื่อสถานที่/ถนน)
    attr='Google Maps'
)

# ปักหมุดสีแดงตรงจุดพิกัดปัจจุบัน
folium.Marker(
    [current_lat, current_lng],
    popup=f"ตำแหน่งของคุณ\n{current_lat}, {current_lng}",
    tooltip="คุณอยู่ที่นี่",
    icon=folium.Icon(color="red", icon="home")
).add_to(m)

# เพิ่มเครื่องมือสำหรับวาด/ลากเส้นบนแผนที่
folium.plugins.Draw(
    export=False,
    position='topleft',
    draw_options={
        'polyline': False,
        'circle': False,
        'rectangle': True,
        'polygon': True,
        'marker': False,
        'circlemarker': False
    }
).add_to(m)

# แสดงผลแผนที่ออกหน้าจอ
output = st_folium(m, width=1000, height=550, key="map_layer")

# 4. ส่วนคำนวณพื้นที่ (ไร่-งาน-ตารางวา) เมื่อผู้ใช้กดปุ่มยืนยัน
st.write("---")
if st.button("✅ ยืนยันลากเส้นเสร็จสิ้น และคำนวณพื้นที่", type="primary"):
    if output and output.get("all_drawings") is not None and len(output["all_drawings"]) > 0:
        # ดึงพิกัดของรูปทรงล่าสุดที่ผู้ใช้วาด
        geo_data = output["all_drawings"][-1]
        coordinates = geo_data['geometry']['coordinates'][0]
        
        if len(coordinates) >= 3:
            poly = Polygon(coordinates)
            
            # แปลงค่าพิกัดพิกัดโลก (องศา) ให้เป็นเมตรตามมาตรฐานประเทศไทย (UTM Zone 47N)
            wgs84 = pyproj.CRS('EPSG:4326')
            utm = pyproj.CRS('EPSG:32647') 
            project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
            utm_poly = transform(project, poly)
            
            area_sq_meters = utm_poly.area
            total_wa = area_sq_meters / 4
            
            # แปลงเป็นหน่วย ไร่ - งาน - ตารางวา
            rai = int(total_wa // 400)
            remaining_wa = total_wa % 400
            ngan = int(remaining_wa // 100)
            wa = remaining_wa % 100
            
            st.success(f"🎉 คำนวณพื้นที่ดินเสร็จเรียบร้อย!")
            st.metric(label="ขนาดพื้นที่แปลงที่ดิน", value=f"{rai} ไร่  {ngan} งาน  {wa:.1f} ตารางวา")
            st.text(f"(คิดเป็นพื้นที่รวมทั้งหมด: {area_sq_meters:,.2f} ตารางเมตร)")
        else:
            st.warning("⚠️ กรุณาลากเส้นต่อกันให้เป็นรูปปิด (อย่างน้อย 3 จุดขึ้นไป) ก่อนกดคำนวณพื้นที่")
    else:
        st.error("❌ ไม่พบเส้นวาดบนแผนที่ กรุณาใช้เครื่องมือรูปห้าเหลี่ยมทางซ้ายบนเพื่อลากเส้นก่อนครับ")
