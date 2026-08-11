import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw, LocateControl
from shapely.geometry import Polygon
from pyproj import Geod

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบวัดพื้นที่นา (ไร่-งาน-วา)", page_icon="🌾", layout="wide")

st.title("🌾 แอปวัดพื้นที่นาและคำนวณขนาดที่ดิน (สูตรแม่นยำสูง)")
st.caption("เปิด GPS เพื่อระบุตำแหน่ง แล้วลากเส้นรอบพื้นที่นาเพื่อคำนวณพื้นที่จริง")

st.divider()

# ---------------------------------------------------------
# ฟังก์ชันคำนวณพื้นที่จริงด้วย Geodesic (WGS84)
# ---------------------------------------------------------
def calculate_thai_area_precise(coords):
    """
    รับพิกัด [(lat, lon), ...] คำนวณพื้นที่จริงบนพื้นผิวโค้งของโลก (หน่วย: ตารางเมตร)
    แล้วแปลงเป็น ไร่ - งาน - ตารางวา
    """
    if len(coords) < 3:
        return None
    
    # ใช้มาตรฐานทรงกลมโลก WGS84 ในการวัดพื้นที่จริง
    geod = Geod(ellps="WGS84")
    
    # PyProj Geod รับพิกัดแบบ (lon, lat)
    lons = [pt[1] for pt in coords]
    lats = [pt[0] for pt in coords]
    
    # คำนวณพื้นที่ (Geodesic Area)
    poly_area, _ = geod.polygon_area_perimeter(lons, lats)
    area_sqm = abs(poly_area) # ค่าที่ได้จะเป็นตารางเมตรจริง
    
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
# สร้างแผนที่ดาวเทียม
# ---------------------------------------------------------
default_lat, default_lon = 13.7563, 100.5018

m = folium.Map(
    location=[default_lat, default_lon],
    zoom_start=16,
    max_zoom=20
)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri World Imagery',
    name='แผนที่ดาวเทียมมุมสูง',
    max_zoom=20,
    overlay=False,
    control=True
).add_to(m)

LocateControl(
    auto_start=False,
    flyTo=True,
    localized=True,
    strings={"title": "📍 กดเพื่อไปยังตำแหน่ง GPS ของฉัน"}
).add_to(m)

draw = Draw(
    export=False,
    position="topleft",
    draw_options={
        "polyline": False,
        "rectangle": True,
        "polygon": True,
        "circle": False,
        "marker": False,
        "circlemarker": False
    },
    edit_options={"poly": {"allowIntersection": False}}
)
draw.add_to(m)

# แสดงแผนที่
col_map, col_res = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ แผนที่ดาวเทียม")
    output = st_folium(m, width="100%", height=550)

# ---------------------------------------------------------
# ประมวลผลคำนวณพื้นที่
# ---------------------------------------------------------
with col_res:
    st.subheader("📊 ผลการวัดพื้นที่")
    
    if output and output.get("all_drawings"):
        drawings = output["all_drawings"]
        if len(drawings) > 0:
            last_drawing = drawings[-1]
            geometry_type = last_drawing["geometry"]["type"]
            
            if geometry_type in ["Polygon", "Rectangle"]:
                coordinates = last_drawing["geometry"]["coordinates"][0]
                lat_lon_coords = [(pt[1], pt[0]) for pt in coordinates]
                
                # เรียกใช้ฟังก์ชันคำนวณพื้นที่แบบแม่นยำสูง
                result = calculate_thai_area_precise(lat_lon_coords)
                
                if result:
                    st.success("คำนวณพื้นที่แม่นยำสำเร็จ!")
                    
                    st.metric("🌾 พื้นที่ไร่", f"{result['rai']} ไร่")
                    st.metric("📐 พื้นที่งาน", f"{result['ngan']} งาน")
                    st.metric("ปร พื้นที่ตารางวา", f"{result['sq_wa']:.1f} ตารางวา")
                    
                    st.divider()
                    st.info(f"💡 คิดเป็นพื้นที่รวม: **{result['sqm']:,.2f} ตารางเมตร**")
            else:
                st.warning("กรุณาใช้เครื่องมือ Polygon หรือ Rectangle เพื่อวาดพื้นที่")
    else:
        st.info("👈 ใช้เครื่องมือวาดทางซ้ายบนของแผนที่เพื่อเริ่มลากเส้นวัดพื้นที่")
