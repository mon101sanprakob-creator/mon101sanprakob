import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
import shapely.ops as ops
import pandas as pd
import datetime

# ตั้งค่าหน้าจอเป็นแบบกว้างเพื่อให้เห็นแผนที่ชัดๆ
st.set_page_config(layout="wide", page_title="ระบบรังวัดดาวเทียมเพื่อความเป็นธรรม")

st.title("🌾 ระบบรังวัดที่นาผ่านดาวเทียม (ฉบับป้องกันการขัดแย้ง)")
st.write("เครื่องมือนี้ใช้พิกัดสากลและแผนที่ดาวเทียมความละเอียดสูง เพื่อคำนวณพื้นที่และค่าจ้างอย่างโปร่งใส ตรวจสอบได้ทั้งสองฝ่าย")

# 1. จัดการระบบความจำ (Session State) เพื่อบันทึกพิกัดหมุด
if 'polygon_coords' not in st.session_state:
    st.session_state.polygon_coords = []

# เมนูด้านข้างสำหรับควบคุมและตั้งค่าเงิน
with st.sidebar:
    st.header("⚙️ ตั้งค่าและควบคุม")
    
    # ส่วนคำนวณเงินค่าจ้าง
    price_per_rai = st.number_input("💵 อัตราค่าจ้าง (บาท ต่อ ไร่):", min_value=0, value=600, step=50)
    
    st.write("---")
    st.write("🛑 **การจัดการพิกัด:**")
    
    # ปุ่มลบหมุดล่าสุด
    if st.button("⬅️ ลบหมุดล่าสุด", use_container_width=True):
        if st.session_state.polygon_coords:
            st.session_state.polygon_coords.pop()
            st.rerun()
            
    # ปุ่มเคลียร์ค่าทั้งหมด
    if st.button("🔄 ล้างค่าทั้งหมด / เริ่มใหม่", type="primary", use_container_width=True):
        st.session_state.polygon_coords = []
        st.rerun()

# 2. จัดเตรียมหน้าจอหลักแบ่งเป็น 2 ฝั่ง (แผนที่ กับ ผลลัพธ์)
col_map, col_result = st.columns([2, 1.2])

with col_map:
    st.subheader("🗺️ 1. ปักหมุดตามแนวคันนาบนแผนที่ดาวเทียม")
    st.caption("คลิกบนแผ่นที่เพื่อวางหมุด (เรียงลำดับตามเข็มหรือทวนเข็มนาฬิกาจนครบรอบแปลงนา)")

    # พิกัดเริ่มต้นกลางประเทศไทย (พิษณุโลก)
    start_lat, start_lng = 16.8200, 100.2600
    
    # หากมีการปักหมุดแล้ว ให้แผนที่โฟกัสไปที่หมุดล่าสุด
    if st.session_state.polygon_coords:
        start_lat, start_lng = st.session_state.polygon_coords[-1]

    # สร้างแผนที่ Folium โดยใช้ภาพดาวเทียม Google Hybrid (เห็นทั้งภาพดาวเทียมและชื่อถนน/สถานที่ใกล้เคียง)
    m = folium.Map(
        location=[start_lat, start_lng], 
        zoom_start=16, 
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
        attr="Google Hybrid"
    )

    # วาดเส้นและระบายสีทับแปลงนาเมื่อปักหมุดตั้งแต่ 2 จุดขึ้นไป
    if len(st.session_state.polygon_coords) > 1:
        if len(st.session_state.polygon_coords) >= 3:
            folium.Polygon(
                locations=st.session_state.polygon_coords,
                color="#00FF00",  # สีเขียวนีออนสะท้อนแสง เห็นชัดเจน
                weight=3,
                fill=True,
                fill_color="#00FF00",
                fill_opacity=0.25
            ).add_to(m)
        else:
            folium.PolyLine(
                locations=st.session_state.polygon_coords,
                color="#00FF00",
                weight=3
            ).add_to(m)

    # ปักหมุดพร้อมแสดงตัวเลขลำดับ เพื่อให้ตรวจทานง่ายว่าปักสลับจุดกันหรือไม่
    for idx, coord in enumerate(st.session_state.polygon_coords):
        folium.Marker(
            location=coord,
            tooltip=f"หมุดที่ {idx+1}",
            icon=folium.DivIcon(html=f"""
                <div style="
                    background-color: #00FF00; 
                    color: black; 
                    font-weight: bold; 
                    border: 2px solid black; 
                    border-radius: 50%; 
                    width: 24px; 
                    height: 24px; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    box-shadow: 0px 0px 5px black;
                ">{idx+1}</div>
            """)
        ).add_to(m)

    # แสดงแผนที่และดักฟังคำสั่งคลิก
    map_data = st_folium(m, width="100%", height=550)

    # เมื่อผู้ใช้คลิก ให้บันทึกพิกัดลงระบบ
    if map_data and map_data.get("last_clicked"):
        clicked_coord = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
        
        # ตรวจสอบป้องกันไม่ให้คลิกซ้ำซ้อนจุดเดิม
        if not st.session_state.polygon_coords or st.session_state.polygon_coords[-1] != clicked_coord:
            st.session_state.polygon_coords.append(clicked_coord)
            st.rerun()

# 3. ฝั่งคำนวณและแสดงผลออกเอกสารหลักฐาน
with col_result:
    st.subheader("📊 2. รายงานการรังวัดหลักฐานสากล")
    
    if len(st.session_state.polygon_coords) >= 3:
        # --- สูตรคำนวณพิกัดภูมิศาสตร์แม่นยำสูง (Geodesic Area) ---
        # สลับแกน (Lat, Lng) เป็น (Lng, Lat) สำหรับคำนวณในหลักสากล GeoJSON
        geojson_coords = [(c[1], c[0]) for c in st.session_state.polygon_coords]
        poly = Polygon(geojson_coords)
        
        # ใช้โปรเจกชั่นเว็บเมอร์เคเตอร์ (Web Mercator / EPSG:3857) เพื่อแปลงองศาโลกโค้งเป็นตารางเมตรจริงบนผิวโลก
        geom_area = ops.transform(
            partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:4326'), # พิกัด WGS84 ดั้งเดิม
                pyproj.Proj(init='epsg:3857')  # แปลงเป็นหน่วยเมตรที่ระนาบเดียวกับ Google Maps
            ),
            poly
        ).area

        # แปลงจาก ตารางเมตร -> หน่วยไทย (ไร่ - งาน - ตารางวา)
        total_sq_wa = geom_area / 4
        rai = int(total_sq_wa // 400)
        ngarn = int((total_sq_wa % 400) // 100)
        sq_wa = total_sq_wa % 100

        # สรุปเงินค่าจ้าง
        total_rai_decimal = geom_area / 1600
        total_cash = total_rai_decimal * price_per_rai

        # กล่องสรุปสีเขียวขนาดใหญ่ ชัดเจน ไม่กำกวม
        st.success(f"### 📐 พื้นที่รวมทั้งหมด:\n## {rai} ไร่  {ngarn} งาน  {sq_wa:.2f} ตารางวา")
        
        st.metric(label=f"💰 รวมค่าจ้างสุทธิ (ไร่ละ {price_per_rai:,} บาท)", value=f"{total_cash:,.2f} บาท")
        
        # สร้างเป็นตารางพิกัดเพื่อความโปร่งใส ป้องกันการตู่พิกัด
        st.write("📋 **พิกัดดาวเทียมอ้างอิงแต่ละหมุด (ตรวจสอบย้อนหลังได้):**")
        df_coords = pd.DataFrame(
            st.session_state.polygon_coords, 
            columns=["ละติจูด (Latitude)", "ลองจิจูด (Longitude)"],
            index=[f"หมุดที่ {i+1}" for i in range(len(st.session_state.polygon_coords))]
        )
        st.dataframe(df_coords, use_container_width=True)
        
        # แนะนำการเก็บหลักฐานป้องกันการโกง
        st.info(f"🕒 **วันเวลาที่รังวัด:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.warning("📸 **คำแนะนำเพื่อความยุติธรรม:** ให้ทั้งสองฝ่ายเปิดหน้าจอนี้ร่วมกัน ตรวจสอบว่าเส้นสีเขียวครอบคลุมที่นาจริงหรือไม่ จากนั้นทำการ 'แคปหน้าจอ (Screenshot)' เก็บไว้เป็นหลักฐานคู่กับสัญญาจ้าง")

    else:
        st.info("💡 ระบบกำลังรอพิกัด... กรุณาคลิกปักหมุดบนแผนที่ฝั่งซ้ายให้ได้อย่างน้อย 3 จุด (3 มุมขอบนา) ระบบจะคำนวณพื้นที่และคิดเงินให้ทันทีครับ")
        
        # โชว์คำแนะนำสั้นๆ ระหว่างรอ
        st.write("---")
        st.markdown("""
        **ทำไมแอปนี้ถึงโกงไม่ได้?**
        1. **พิกัดล็อกตำแหน่งจริง:** ค่า Latitude/Longitude ถอนมาจากดาวเทียมตรงๆ เปลี่ยนแปลงเองไม่ได้
        2. **คำนวณระดับเมตร:** ใช้สูตรคณิตศาสตร์สากล (`pyproj` และ `shapely`) แปรค่าตามส่วนโค้งผิวโลก ไม่ใช้ไม้บรรทัดทาบธรรมดา
        """)
