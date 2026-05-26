import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from shapely.ops import transform
from geopy.geocoders import Nominatim
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")
st.title("📌 แอปวัดพื้นที่ดินดาวเทียม & ระบุตำแหน่งปัจจุบัน")

# 1. ระบบดึงพิกัด GPS ปัจจุบันจากอุปกรณ์ของผู้ใช้ (มือถือ/คอมพิวเตอร์)
st.subheader("📡 ตรวจสอบพิกัดและสถานที่ปัจจุบันของคุณ")
location = streamlit_js_eval(data_name='geocode', reason='Get user location', key='搞')

# ตั้งค่าพิกัดเริ่มต้น (หากดึง GPS ไม่สำเร็จจะใช้พิกัดกรุงเทพฯ เป็นค่าเริ่มต้น)
current_lat, current_lng = 13.7563, 100.5018 
address_text = "กำลังค้นหาตำแหน่งของคุณ หรือโปรดเปิดสิทธิ์การเข้าถึง GPS..."

if location:
    current_lat = location['coords']['latitude']
    current_lng = location['coords']['longitude']
    
    # 2. แปลงพิกัด GPS เป็น "ชื่อสถานที่/ที่อยู่" (Reverse Geocoding)
    try:
        geolocator = Nominatim(user_agent="mon101_geo_app")
        geo_location = geolocator.reverse(f"{current_lat}, {current_lng}", timeout=10)
        if geo_location:
            address_text = geo_location.address
        else:
            address_text = f"พิกัด ละติจูด: {current_lat}, ลองจิจูด: {current_lng} (ไม่พบชื่อสถานที่ในระบบ)"
    except Exception as e:
        address_text = f"พิกัด ละติจูด: {current_lat}, ลองจิจูด: {current_lng} (เชื่อมต่อระบบค้นหาชื่อสถานที่ไม่ได้)"

# แสดงชื่อสถานที่ปัจจุบันให้ผู้ใช้เห็นบนหน้าจอชัดเจน
st.info(f"🏠 **สถานที่ปัจจุบันของคุณ:** {address_text}")

st.caption("วิธีใช้: ใช้นิ้วหรือเมาส์คลิกเครื่องมือวาดรูปสี่เหลี่ยม/โพลิกอนทางซ้ายของแผนที่ เพื่อลากเส้นล้อมรอบที่ดินที่ต้องการวัด")

# 3. สร้างแผนที่ดาวเทียมโดยให้จุดกึ่งกลางและหมุด (Marker) อยู่ที่พิกัดปัจจุบันทันที
m = folium.Map(
    location=[current_lat, current_lng], 
    zoom_start=18,  # ซูมเข้าไปใกล้ๆ ให้เห็นหลังคาบ้านชัดเจนขึ้น
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
    attr='Google'
)

# ปักหมุดสีแดงที่ตำแหน่งปัจจุบันของผู้ใช้
folium.Marker(
    [current_lat, current_lng],
    popup="ตำแหน่งปัจจุบันของคุณ",
    tooltip="คุณอยู่ที่นี่",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# เพิ่มเครื่องมือวาด/ลากเส้นบนหน้าแอป
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

# แสดงแผนที่
output = st_folium(m, width=1000, height=500)

# 4. ส่วนคำนวณพื้นที่เมื่อกดปุ่มยืนยัน
st.write("---")
if st.button("✅ ยืนยันลากเส้นเสร็จสิ้น และคำนวณพื้นที่", type="primary"):
    if output and output.get("all_drawings") is not None and len(output["all_drawings"]) > 0:
        geo_data = output["all_drawings"][-1]
        coordinates = geo_data['geometry']['coordinates'][0]
        
        if len(coordinates) >= 3:
            poly = Polygon(coordinates)
            
            # แปลงค่าพิกัดพื้นที่ของไทยเป็นตารางเมตร
            wgs84 = pyproj.CRS('EPSG:4326')
            utm = pyproj.CRS('EPSG:32647') 
            project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
            utm_poly = transform(project, poly)
            
            area_sq_meters = utm_poly.area
            total_wa = area_sq_meters / 4
            
            # คำนวณเป็น ไร่-งาน-วา
            rai = int(total_wa // 400)
            remaining_wa = total_wa % 400
            ngan = int(remaining_wa // 100)
            wa = remaining_wa % 100
            
            st.success(f"🎉 คำนวณพื้นที่สำเร็จ!")
            st.metric(label="พื้นที่ที่ลากเส้นล้อมรอบได้", value=f"{rai} ไร่  {ngan} งาน  {wa:.1f} ตารางวา")
            st.info(f"(คิดเป็น {area_sq_meters:,.2f} ตารางเมตร)")
        else:
            st.warning("⚠️ กรุณาลากเส้นต่อกันให้เป็นรูปปิด (อย่างน้อย 3 จุด) ก่อนกดคำนวณ")
    else:
        st.error("❌ ยังไม่มีการลากเส้นบนแผนที่ กรุณาใช้เครื่องมือวาดรูปบนแผนที่ก่อนครับ")
