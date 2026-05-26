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

# ดึงพิกัดอัตโนมัติจากเบราว์เซอร์
location = streamlit_js_eval(data_name='geocode', reason='Get user location', key='geo_check')

# ตั้งค่าพิกัดเริ่มต้น (กรุงเทพฯ)
auto_lat, auto_lng = 13.7563, 100.5018 
if location:
    auto_lat = location['coords']['latitude']
    auto_lng = location['coords']['longitude']

st.subheader("📡 ตั้งค่าตำแหน่งพิกัดของคุณ")
col1, col2 = st.columns(2)

with col1:
    # ผู้ใช้สามารถพิมพ์เปลี่ยนพิกัดเองได้ หากระบบค้นหาอัตโนมัติไม่ตรง
    current_lat = st.number_input("ละติจูด (Latitude)", value=auto_lat, format="%.6f")
with col2:
    current_lng = st.number_input("ลองจิจูด (Longitude)", value=auto_lng, format="%.6f")

# ค้นหาที่อยู่จากพิกัดที่เลือก
address_text = "กำลังค้นหาชื่อสถานที่..."
try:
    geolocator = Nominatim(user_agent="mon101_geo_app_v2")
    geo_location = geolocator.reverse(f"{current_lat}, {current_lng}", timeout=10)
    if geo_location:
        address_text = geo_location.address
    else:
        address_text = "ไม่พบชื่อสถานที่ในระบบ แต่สามารถใช้พิกัดนี้วาดที่ดินได้"
except Exception:
    address_text = "ใช้พิกัดระบุตำแหน่งบนแผนที่ดาวเทียมแล้ว"

st.info(f"🏠 **สถานที่ตามพิกัดด้านบน:** {address_text}")
st.caption("💡 *หากหมุดยังไม่ตรงบ้านของคุณ คุณสามารถเข้า Google Maps ในมือถือแล้วก๊อปปี้ตัวเลขพิกัดบ้านคุณมาวางในช่องด้านบนนี้ได้เลย แผนที่จะกระโดดไปที่หลังคาบ้านทันที*")

# สร้างแผนที่ตามพิกัดปัจจุบัน
m = folium.Map(
    location=[current_lat, current_lng], 
    zoom_start=19,  # ซูมระดับเห็นหลังคาบ้านชัดเจน
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
    attr='Google'
)

# ปักหมุดตำแหน่งปัจจุบัน
folium.Marker(
    [current_lat, current_lng],
    popup="ตำแหน่งวัดที่ดิน",
    tooltip="จุดพิกัดของคุณ",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# เครื่องมือวาด
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

output = st_folium(m, width=1000, height=500, key="map")

# ส่วนคำนวณพื้นที่
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
            
            st.success(f"🎉 คำนวณพื้นที่สำเร็จ!")
            st.metric(label="พื้นที่ที่ลากเส้นล้อมรอบได้", value=f"{rai} ไร่  {ngan} งาน  {wa:.1f} ตารางวา")
            st.info(f"(คิดเป็น {area_sq_meters:,.2f} ตารางเมตร)")
        else:
            st.warning("⚠️ กรุณาลากเส้นต่อกันให้เป็นรูปปิด (อย่างน้อย 3 จุด) ก่อนกดคำนวณ")
    else:
        st.error("❌ ยังไม่มีการลากเส้นบนแผนที่ กรุณาใช้เครื่องมือวาดรูปบนแผนที่ก่อนครับ")
