import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from shapely.ops import transform
from geopy.geocoders import Nominatim
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")
st.title("📌 แอปวัดพื้นที่ดินดาวเทียมแบบไฮบริด")

# เรียกใช้ตัวค้นหาพิกัด
geolocator = Nominatim(user_agent="mon101_land_measure_v3")

# 1. สร้างระบบค้นหาตำแหน่ง (พิมพ์ค้นหาได้เลย ไม่ต้องง้อ GPS เบราว์เซอร์)
st.subheader("🔍 ค้นหาและปักหมุดตำแหน่งของคุณ")
search_query = st.text_input("พิมพ์ชื่อสถานที่ เช่น 'อ.เมือง จ.เชียงใหม่' หรือ 'วัดพระแก้ว' หรือ 'ชื่อหมู่บ้าน ตำบล จังหวัด' ของคุณ :", "")

# ค่าพิกัดเริ่มต้น (ถ้าไม่มีการค้นหา และ GPS ไม่ทำงาน จะอยู่ตรงนี้)
current_lat, current_lng = 13.7563, 100.5018 
location_found = False

# ถ้าผู้ใช้พิมพ์ค้นหา ให้วิ่งไปที่นั่นทันที
if search_query:
    try:
        geo_search = geolocator.geocode(search_query, timeout=10)
        if geo_search:
            current_lat = geo_search.latitude
            current_lng = geo_search.longitude
            location_found = True
            st.success(f"📍 เจอตำแหน่งแล้ว! กำลังวาร์ปไปที่: {geo_search.address}")
        else:
            st.error("❌ ไม่พบชื่อสถานที่นี้ กรุณาพิมพ์ให้ละเอียดขึ้น เช่น ใส่ชื่อตำบล หรืออำเภอ เพิ่มเติมครับ")
    except Exception:
        st.warning("⚠️ ระบบค้นหาขัดข้องชั่วคราว กำลังพยายามใช้ระบบดึงพิกัดอัตโนมัติ...")

# ถ้าผู้ใช้ไม่ได้พิมพ์ค้นหา ให้ลองดึงค่า GPS สดจากเครื่อง (เผื่อกดอนุญาตแล้ว)
if not location_found:
    gps_data = streamlit_js_eval(data_name='geocode', reason='ขอพิกัดเพื่อระบุตำแหน่งบ้าน', key='get_current_gps_v3')
    if gps_data and 'coords' in gps_data:
        current_lat = gps_data['coords']['latitude']
        current_lng = gps_data['coords']['longitude']

# ช่องแสดงและปรับแต่งตัวเลขพิกัดแบบละเอียด
with st.expander("ตรวจสอบ/กรอกตัวเลขพิกัดละติจูด ลองจิจูด เองคลิกที่นี่"):
    current_lat = st.number_input("ค่าละติจูด (Latitude)", value=current_lat, format="%.6f")
    current_lng = st.number_input("ค่าลองจิจูด (Longitude)", value=current_lng, format="%.6f")

# 2. ค้นหาชื่อที่อยู่ปัจจุบันมาแสดงผล
try:
    geo_location = geolocator.reverse(f"{current_lat}, {current_lng}", timeout=5)
    address_text = geo_location.address if geo_location else "พิกัดระบุบนแผนที่แล้ว"
except Exception:
    address_text = "แสดงผลบนแผนที่ดาวเทียมไฮบริด"

st.info(f"🏠 **พิกัดปัจจุบันบนแผนที่:** {address_text}")

# 3. สร้างแผนที่ดาวเทียมแบบ Hybrid (เห็นหลังคาบ้าน + มีชื่อถนน/สถานที่บอกชัดเจน)
m = folium.Map(
    location=[current_lat, current_lng], 
    zoom_start=18, # ซูมระดับเห็นสังกะสี/หลังคาบ้าน
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', # Google Hybrid
    attr='Google Maps'
)

# ปักหมุดสีแดง
folium.Marker(
    [current_lat, current_lng],
    popup=f"พิกัด: {current_lat}, {current_lng}",
    tooltip="จุดพิกัดหลัก",
    icon=folium.Icon(color="red", icon="home")
).add_to(m)

# เพิ่มเครื่องมือวาดเส้นล้อมรอบที่ดิน (รูปห้าเหลี่ยมมุมซ้ายบน)
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

# แสดงแผนที่บนหน้าเว็บ
output = st_folium(m, width=1000, height=550, key="map_v3")

# 4. ปุ่มยืนยันและคำนวณพื้นที่เป็นไร่
st.write("---")
if st.button("✅ ยืนยันลากเส้นเสร็จสิ้น และคำนวณพื้นที่", type="primary"):
    if output and output.get("all_drawings") is not None and len(output["all_drawings"]) > 0:
        geo_data = output["all_drawings"][-1]
        coordinates = geo_data['geometry']['coordinates'][0]
        
        if len(coordinates) >= 3:
            poly = Polygon(coordinates)
            wgs84 = pyproj.CRS('EPSG:4326')
            utm = pyproj.CRS('EPSG:32647') 
            project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
            utm_poly = transform(project, poly)
            
            area_sq_meters = utm_poly.area
            total_wa = area_sq_meters / 4
            
            rai = int(total_wa // 400)
            remaining_wa = total_wa % 400
            ngan = int(remaining_wa // 100)
            wa = remaining_wa % 100
            
            st.success(f"🎉 คำนวณพื้นที่ดินสำเร็จ!")
            st.metric(label="ขนาดพื้นที่แปลงที่ดินของคุณ", value=f"{rai} ไร่  {ngan} งาน  {wa:.1f} ตารางวา")
            st.text(f"(คิดเป็น {area_sq_meters:,.2f} ตารางเมตร)")
        else:
            st.warning("⚠️ กรุณาใช้นิ้วลากเส้นต่อกันให้เป็นรูปปิด (อย่างน้อย 3 จุดขึ้นไป)")
    else:
        st.error("❌ ไม่พบเส้นที่วาด กรุณาคลิกเครื่องมือรูปห้าเหลี่ยมทางซ้ายบนของแผนที่แล้วลากเส้นก่อนครับ")
