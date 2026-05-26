import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from shapely.ops import transform
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide")
st.title("📌 แอปวัดที่ดินดาวเทียม (ดึงพิกัด GPS จากโทรศัพท์โดยตรง)")

# 1. ฟังก์ชัน JavaScript ดึงค่าพิกัดจากชิป GPS ของโทรศัพท์มือถือโดยตรง
st.subheader("📡 สัญญาณ GPS จากโทรศัพท์ของคุณ")

# คำสั่งเรียกพิกัดสดจากมือถือ (ระบบจะบังคับเปิดสิทธิ์แชร์ตำแหน่ง)
gps_location = streamlit_js_eval(data_name='geocode', reason='ขอเข้าถึงพิกัด GPS เพื่อระบุตำแหน่งบ้านและหลังคาบ้านของคุณ', key='phone_gps_direct')

# ตั้งค่าพิกัดสำรองไว้ชั่วคราวระหว่างรอสัญญาณดาวเทียม
lat, lng = 13.7563, 100.5018 
gps_ready = False

if gps_location and 'coords' in gps_location:
    lat = gps_location['coords']['latitude']
    lng = gps_location['coords']['longitude']
    gps_ready = True
    st.success(f"🎯 เชื่อมต่อ GPS โทรศัพท์สำเร็จ! พิกัดปัจจุบันของคุณคือ: {lat}, {lng}")
else:
    st.warning("🔄 กำลังพยายามดึงพิกัดจากโทรศัพท์ของคุณ... โปรดตรวจสอบว่าคุณได้กด 'อนุญาต' หรือ 'Allow' ให้เว็บเข้าถึงตำแหน่งแล้ว")
    st.info("💡 หากหน้าจอโทรศัพท์มีป๊อปอัปเด้งถามเรื่องการเข้าถึงตำแหน่ง (Location) ต้องกด **'อนุญาต (Allow)'** เท่านั้น หมุดถึงจะเด้งไปที่บ้านของคุณครับ")

st.caption("🗺️ **วิธีใช้นิ้วลากเส้น:** คลิกเครื่องมือรูปห้าเหลี่ยม (Draw a polygon) ที่มุมซ้ายบนของแผนที่ จากนั้นใช้นิ้วจิ้มลากเส้นล้อมรอบแปลงที่ดิน เมื่อเสร็จแล้วให้กดปุ่มคำนวณด้านล่าง")

# 2. สร้างแผนที่ดาวเทียมแบบ Hybrid (เห็นหลังคาบ้าน + ชื่อสถานที่และเส้นถนน)
# โดยตั้งพิกัดศูนย์กลางตามพิกัดที่ดึงได้จากโทรศัพท์ทันที
m = folium.Map(
    location=[lat, lng], 
    zoom_start=19, # ซูมระดับ 19 เพื่อให้เห็นหลังคาบ้านและต้นไม้ชัดเจนที่สุด
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', # Google Hybrid (ดาวเทียม + ชื่อสถานที่/ถนน)
    attr='Google Maps'
)

# ปักหมุดสีแดงตรงจุดที่โทรศัพท์ของคุณอยู่ปัจจุบัน
folium.Marker(
    [lat, lng],
    popup="คุณยืนอยู่ตรงนี้",
    tooltip="ตำแหน่งปัจจุบันของคุณ",
    icon=folium.Icon(color="red", icon="user")
).add_to(m)

# เพิ่มเครื่องมือวาดเส้นรอบที่ดิน (รูปห้าเหลี่ยมมุมซ้ายบน)
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

# แสดงแผนที่ออกหน้าจอเว็บแอป
output = st_folium(m, width=1000, height=550, key="map_layer_v4")

# 3. ส่วนคำนวณพื้นที่ (ไร่-งาน-ตารางวา) เมื่อผู้ใช้ใช้นิ้วลากเส้นเสร็จสิ้น
st.write("---")
if st.button("✅ ยืนยันลากเส้นเสร็จสิ้น และคำนวณพื้นที่", type="primary"):
    if output and output.get("all_drawings") is not None and len(output["all_drawings"]) > 0:
        # ดึงพิกัดรูปทรงล่าสุดที่ผู้ใช้วาดเส้นล้อมรอบไว้
        geo_data = output["all_drawings"][-1]
        coordinates = geo_data['geometry']['coordinates'][0]
        
        if len(coordinates) >= 3:
            poly = Polygon(coordinates)
            
            # แปลงค่าพิกัดพิกัดโลกให้เป็นเมตรตามมาตรฐานประเทศไทย (UTM Zone 47N) เพื่อความแม่นยำ
            wgs84 = pyproj.CRS('EPSG:4326')
            utm = pyproj.CRS('EPSG:32647') 
            project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
            utm_poly = transform(project, poly)
            
            area_sq_meters = utm_poly.area
            total_wa = area_sq_meters / 4
            
            # แปลงตารางเมตรออกเป็นหน่วย ไร่ - งาน - ตารางวา
            rai = int(total_wa // 400)
            remaining_wa = total_wa % 400
            ngan = int(remaining_wa // 100)
            wa = remaining_wa % 100
            
            st.success(f"🎉 คำนวณพื้นที่ดินเสร็จเรียบร้อย!")
            st.metric(label="ขนาดพื้นที่ของแปลงที่ดินที่ลากเส้นได้", value=f"{rai} ไร่  {ngan} งาน  {wa:.1f} ตารางวา")
            st.text(f"(คิดเป็นพื้นที่รวมทั้งหมด: {area_sq_meters:,.2f} ตารางเมตร)")
        else:
            st.warning("⚠️ กรุณาใช้นิ้วลากเส้นต่อกันให้เป็นรูปปิด (อย่างน้อย 3 จุดขึ้นไป) ก่อนกดคำนวณ")
    else:
        st.error("❌ ไม่พบเส้นวาดบนแผนที่ กรุณาใช้เครื่องมือรูปห้าเหลี่ยมทางซ้ายบนเพื่อลากเส้นรอบที่ดินก่อนครับ")
