import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw, LocateControl
from shapely.geometry import Polygon
import geopy.distance

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบวัดพื้นที่นา (ไร่-งาน-วา)", page_icon="🌾", layout="wide")

st.title("🌾 แอปวัดพื้นที่นาและคำนวณขนาดที่ดิน")
st.caption("เปิด GPS เพื่อระบุตำแหน่งที่คุณอยู่ จากนั้นใช้เครื่องมือวาดรูปบนแผนที่เพื่อลากเส้นรอบพื้นที่นา")

st.divider()

# ---------------------------------------------------------
# ฟังก์ชันคำนวณพื้นที่จากพิกัด (แปลงเป็น ไร่ - งาน - ตารางวา)
# ---------------------------------------------------------
def calculate_thai_area(coords):
    """
    รับพิกัด [(lat, lon), ...] แล้วคำนวณพื้นที่เป็นตารางเมตร 
    พร้อมแปลงเป็นหน่วย ไร่ - งาน - ตารางวา
    """
    if len(coords) < 3:
        return None
    
    # คำนวณพื้นที่ในหน่วยตารางเมตร (เกสเฟียร์)
    # ใช้ Shapely ร่วมกับการแปลงพิกัดพื้นผิวโลก
    poly = Polygon(coords)
    
    # คำนวณพื้นที่ตารางเมตรแบบประมาณการทางภูมิศาสตร์
    # 1 องศา lat/lon โดยเฉลี่ยประมาณ 111,000 เมตร
    # เพื่อความแม่นยำใช้การแปลง Projection พื้นฐาน
    lat_center = sum(p[0] for p in coords) / len(coords)
    meters_per_degree_lat = 111139
    meters_per_degree_lon = 111139 * (abs(sum([abs(p[0]) for p in coords])/len(coords))) # approx latitude adjustment
    
    # แปลงพิกัดเป็นเมตร (Utm Approximation)
    coords_m = [(p[1] * 111320 * abs(sum([p[0] for p in coords])/len(coords)), p[0] * 110540) for p in coords]
    poly_m = Polygon(coords_m)
    area_sqm = poly_m.area
    
    # แปลงหน่วยไทย:
    # 1 ไร่ = 1,600 ตารางเมตร
    # 1 งาน = 400 ตารางเมตร
    # 1 ตารางวา = 4 ตารางเมตร
    
    rai = int(area_sqm // 1600)
    remainder_rai = area_sqm % 1600
    
    ngan = int(remainder_rai // 400)
    remainder_ngan = remainder_rai % 400
    
    sq_wa = remainder_ngan / 4.0
    
    return {
        "sqm": area_sqm,
        "rai": rai,
        "ngan": ngan,
        "sq_wa": sq_wa
    }

# ---------------------------------------------------------
# สร้างแผนที่ดาวเทียม (Esri World Imagery)
# ---------------------------------------------------------
# พิกัดเริ่มต้น (กรุงเทพฯ/ประเทศไทย เป็นค่าเริ่มต้นหากยังไม่ได้เปิด GPS)
default_lat, default_lon = 13.7563, 100.5018

m = folium.Map(
    location=[default_lat, default_lon],
    zoom_start=16,
    max_zoom=20
)

# เพิ่มชั้นแผนที่ภาพถ่ายดาวเทียมมุมสูง (Esri Satellite)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri World Imagery',
    name='แผนที่ดาวเทียมมุมสูง',
    max_zoom=20,
    overlay=False,
    control=True
).add_to(m)

# เพิ่มปุ่มกดดึงพิกัด GPS จุดที่เราอยู่ปัจจุบัน
LocateControl(
    auto_start=False,
    flyTo=True,
    keepCurrentZoomLevel=False,
    localized=True,
    strings={"title": "📍 กดเพื่อไปยังตำแหน่ง GPS ของฉัน"}
).add_to(m)

# เพิ่มเครื่องมือวาดเส้น/ลากแปลงที่ดิน (Draw Tool)
draw = Draw(
    export=False,
    position="topleft",
    draw_options={
        "polyline": False,
        "rectangle": True,
        "polygon": True,     # ใช้ลากเส้นรอบแปลงนา
        "circle": False,
        "marker": True,
        "circlemarker": False
    },
    edit_options={"poly": {"allowIntersection": False}}
)
draw.add_to(m)

# แสดงแผนที่บน Streamlit
col_map, col_res = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ แผนที่ดาวเทียม (กดรูปเครื่องมือวาดทางซ้ายบนของแผนที่)")
    output = st_folium(m, width="100%", height=550)

# ---------------------------------------------------------
# ส่วนประมวลผลคำนวณพื้นที่
# ---------------------------------------------------------
with col_res:
    st.subheader("📊 ผลการวัดพื้นที่")
    
    # ตรวจจับเมื่อผู้ใช้ลากเส้นวาดรูปพื้นที่บนแผนที่
    if output and output.get("all_drawings"):
        drawings = output["all_drawings"]
        if len(drawings) > 0:
            # ดึงโครงร่างรูปล่าสุดที่ผู้ใช้ลากไว้
            last_drawing = drawings[-1]
            geometry_type = last_drawing["geometry"]["type"]
            
            if geometry_type in ["Polygon", "Rectangle"]:
                coordinates = last_drawing["geometry"]["coordinates"][0]
                # พิกัดจาก GeoJSON จะเป็น [lon, lat] ต้องสลับเป็น [lat, lon]
                lat_lon_coords = [(pt[1], pt[0]) for pt in coordinates]
                
                # คำนวณพื้นที่
                result = calculate_thai_area(lat_lon_coords)
                
                if result:
                    st.success("คำนวณพื้นที่สำเร็จ!")
                    
                    st.metric("🌾 พื้นที่ไร่", f"{result['rai']} ไร่")
                    st.metric("📐 พื้นที่งาน", f"{result['ngan']} งาน")
                    st.metric("ปร พื้นที่ตารางวา", f"{result['sq_wa']:.1f} ตารางวา")
                    
                    st.divider()
                    st.info(f"💡 คิดเป็นพื้นที่รวม: **{result['sqm']:,.2f} ตารางเมตร**")
            else:
                st.warning("กรุณาใช้เครื่องมือวาดรูปหลายเหลี่ยม (Polygon) หรือสี่เหลี่ยม เพื่อลากรอบพื้นที่นา")
        else:
            st.info("👈 ใช้เครื่องมือวาดทางซ้ายบนของแผนที่เพื่อเริ่มลากเส้นวัดพื้นที่")
    else:
        st.info("👈 **วิธีใช้งาน:**\n1. กดปุ่ม 📍 บนแผนที่เพื่อไปยังตำแหน่ง GPS ที่คุณอยู่\n2. กดรูปเหลี่ยม (Polygon) ทางซ้ายบนแผนที่เพื่อเริ่มคลิกลากจุดรอบแปลงนา\n3. เมื่อลากบรรจบจุดเดิม ระบบจะคำนวณเป็น **ไร่-งาน-วา** ทันที")
