import streamlit as st
import folium
from streamlit_folium import st_folium
import json
from shapely.geometry import Polygon
import pyproj
from shapely.ops import transform

st.set_page_config(layout="wide")
st.title("📌 แอปวัดพื้นที่ดินดาวเทียม (หน่วย: ไร่-งาน-วา)")
st.caption("วิธีใช้: ใช้นิ้วหรือเมาส์คลิกเครื่องมือวาดรูปสี่เหลี่ยม/โพลิกอนทางซ้ายของแผนที่ เพื่อลากเส้นล้อมรอบที่ดิน")

# 1. ตั้งค่าพิกัดเริ่มต้น (ดาวเทียมเห็นหลังคาบ้าน)
# สามารถเปลี่ยนพิกัดเริ่มต้นตรงนี้ได้ [ละติจูด, ลองจิจูด]
START_LOCATION = [13.7563, 100.5018] 

m = folium.Map(
    location=START_LOCATION, 
    zoom_start=16, 
    tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', # ใช้แผนที่ดาวเทียม Google Satellite (เห็นหลังคาชัดเจน)
    attr='Google'
)

# 2. เพิ่มเครื่องมือสำหรับให้ผู้ใช้ลากเส้นบนหน้าจอ
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

# แสดงแผนที่บนหน้าแอป streamlit
output = st_folium(m, width=1000, height=500)

# 3. ส่วนควบคุมการกด "ยืนยันลากเส้นเสร็จสิ้น" และคำนวณค่า
st.write("---")
if st.button("✅ ยืนยันลากเส้นเสร็จสิ้น และคำนวณพื้นที่", type="primary"):
    # ดึงค่าพิกัดที่ผู้ใช้วาดเส้นจากหน้าจอ
    if output and output.get("all_drawings") is not None and len(output["all_drawings"]) > 0:
        
        # เอาพิกัดจุดสุดท้ายที่ผู้วาดวาดไว้
        geo_data = output["all_drawings"][-1]
        coordinates = geo_data['geometry']['coordinates'][0]
        
        if len(coordinates) >= 3:
            # สร้างรูปทรงจากพิกัด
            poly = Polygon(coordinates)
            
            # แปลงค่าพิกัดเชิงภูมิศาสตร์ (องศา) ให้เป็นเมตร เพื่อคำนวณพื้นที่จริง
            wgs84 = pyproj.CRS('EPSG:4326')
            utm = pyproj.CRS('EPSG:32647') # โซน UTM ของประเทศไทย
            project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
            utm_poly = transform(project, poly)
            
            # พื้นที่รวมเป็นตารางเมตร
            area_sq_meters = utm_poly.area
            
            # แปลงเป็นตารางวา (4 ตารางเมตร = 1 ตารางวา)
            total_wa = area_sq_meters / 4
            
            # คำนวณ หน่วยไทย (ไร่-งาน-ตารางวา)
            rai = int(total_wa // 400)
            remaining_wa = total_wa % 400
            ngan = int(remaining_wa // 100)
            wa = remaining_wa % 100
            
            # แสดงผลลัพธ์บนหน้าจอ
            st.success(f"🎉 คำนวณพื้นที่สำเร็จ!")
            st.metric(label="พื้นที่ทั้งหมด", value=f"{rai} ไร่  {ngan} งาน  {wa:.1f} ตารางวา")
            st.info(f"(คิดเป็น {area_sq_meters:,.2f} ตารางเมตร)")
        else:
            st.warning("⚠️ กรุณาลากเส้นต่อกันให้เป็นรูปปิด (อย่างน้อย 3 จุด) ก่อนกดคำนวณ")
    else:
        st.error("❌ ยังไม่มีการลากเส้นบนแผนที่ กรุณาใช้เครื่องมือวาดรูปบนแผนที่ก่อนครับ")
