import streamlit as st
import folium
from streamlit_folium import st_folium
from shapely.geometry import Polygon
import pyproj
from functools import partial
import shapely.ops as ops
import pandas as pd
import datetime
from folium.plugins import LocateControl  # ✅ นำเข้าตัวจับพิกัดตั้งแต่เริ่มเพื่อความปลอดภัย

# ตั้งค่าหน้าจอเป็นแบบกว้างเพื่อให้เห็นแผนที่ชัดๆ
st.set_page_config(layout="wide", page_title="ระบบรังวัดดาวเทียมตามพิกัดจริง")

st.title("🌾 ระบบรังวัดที่นาผ่านดาวเทียม (ดักจับพิกัดปัจจุบัน)")
st.write("แอปพลิเคชันจะจับตำแหน่งที่คุณยืนอยู่ปัจจุบันโดยอัตโนมัติ เพื่อความแม่นยำในการเริ่มจับขอบแปลงนา")

# 1. จัดการระบบความจำ (Session State)
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
    st.subheader("🗺️ 1. แผนที่ดาวเทียมตรงจุดที่คุณอยู่")
    st.caption("💡 แผนที่จะขยับมาหาตำแหน่งปัจจุบันของคุณอัตโนมัติ จากนั้นคลิกปักหมุดล้อมรอบแปลงนา")

    # พิกัดเริ่มต้น (กรณียังจับ GPS ไม่ได้ จะใช้ค่ากลางประเทศไทยก่อน)
    start_lat, start_lng = 16.8200, 100.2600
    
    # หากมีการคลิกปักหมุดแล้ว ให้แผนที่ยึดตามหมุดล่าสุด
    if st.session_state.polygon_coords:
        start_lat, start_lng = st.session_state.polygon_coords[-1]

    # สร้างแผนที่ Folium โดยใช้ภาพดาวเทียม Google Hybrid (เห็นทั้งภาพถ่ายและชื่อสถานที่)
    m = folium.Map(
        location=[start_lat, start_lng], 
        zoom_start=17,  # ซูมเข้าไปใกล้ระดับแปลงนา
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
        attr="Google Hybrid"
    )

    # ✅ แก้ไขจุดนี้: เรียกใช้งานปุ่มจับพิกัดปัจจุบันโดยไม่ใช้คำสั่งล้างปลั๊กอินเก่า
    LocateControl(
        auto_start=True, # เปิดปุ๊บวิ่งไปหาตำแหน่งปัจจุบันปั๊บ
        fly_to=True,
        keep_current_zoom_level=False,
        strings={"title": "🔍 ค้นหาตำแหน่งของฉัน", "metersUnit": "เมตร"}
    ).add_to(m)

    # วาดเส้นและระบายสีทับแปลงนาเมื่อปักหมุดตั้งแต่ 2 จุดขึ้นไป
    if len(st.session_state.polygon_coords) > 1:
        if len(st.session_state.polygon_coords) >= 3:
            folium.Polygon(
                locations=st.session_state.polygon_coords,
                color="#00FF00",  # สีเขียวนีออนสะท้อนแสง เห็นชัดเจนไม่สับสน
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

    # ปักหมุดพร้อมแสดงตัวเลขลำดับ 1, 2, 3... เพื่อความโปร่งใส
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

    # เมื่อผู้ใช้คลิกบนแผนที่ดาวเทียม ให้บันทึกพิกัดลงระบบ
    if map_data and map_data.get("last_clicked"):
        clicked_coord = [map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]]
        
        # ป้องกันไม่ให้คลิกซ้ำจุดเดิม
        if not st.session_state.polygon_coords or st.session_state.polygon_coords[-1] != clicked_coord:
            st.session_state.polygon_coords.append(clicked_coord)
            st.rerun()

# 3. ฝั่งคำนวณและแสดงผลลัพธ์ (เน้นหน่วย ไร่-งาน-ตารางวา ขึ้นก่อน)
with col_result:
    st.subheader("📊 2. สรุปเนื้อที่นาจริง")
    
    if len(st.session_state.polygon_coords) >= 3:
        # --- สูตรคำนวณพิกัดภูมิศาสตร์สากลเพื่อความแม่นยำสูง ---
        geojson_coords = [(c[1], c[0]) for c in st.session_state.polygon_coords]
        poly = Polygon(geojson_coords)
        
        # แปลงพิกัดโลกโค้งเป็นระนาบหน่วยเมตร (EPSG:3857) เพื่อหาพื้นที่ตารางเมตรที่แท้จริง
        geom_area = ops.transform(
            partial(
                pyproj.transform,
                pyproj.Proj(init='epsg:4326'), 
                pyproj.Proj(init='epsg:3857')  
            ),
            poly
        ).area

        # แปลงจาก ตารางเมตร -> หน่วยไทย (ไร่ - งาน - ตารางวา)
        total_sq_wa = geom_area / 4
        rai = int(total_sq_wa // 400)
        ngarn = int((total_sq_wa % 400) // 100)
        sq_wa = total_sq_wa % 100

        # คำนวณเงินสุทธิ
        total_rai_decimal = geom_area / 1600
        total_cash = total_rai_decimal * price_per_rai

        # โชว์หน่วยวัด ไร่ งาน ตารางวา ตัวใหญ่ๆ นำหน้าชัดเจนตามคำขอครับ
        st.success(f"""
        ### 📐 ขนาดพื้นที่วัดได้จริง:
        # {rai} ไร่  {ngarn} งาน  {sq_wa:.2f} ตารางวา
        """)
        
        st.metric(label=f"💰 คิดเป็นค่าบริการสุทธิ (ไร่ละ {price_per_rai:,} บาท)", value=f"{total_cash:,.2f} บาท")
        
        # แสดงตารางพิกัดแต่ละหมุดเพื่อเป็นหลักฐานความโปร่งใส ยืนยันว่าไม่ได้เมคตัวเลขขึ้นมาเอง
        st.write("📋 **พิกัดดาวเทียมแต่ละหมุด (ห้ามโกง):**")
        df_coords = pd.DataFrame(
            st.session_state.polygon_coords, 
            columns=["ละติจูด (Latitude)", "ลองจิจูด (Longitude)"],
            index=[f"หมุดที่ {i+1}" for i in range(len(st.session_state.polygon_coords))]
        )
        st.dataframe(df_coords, use_container_width=True)
        
        st.info(f"🕒 **วันเวลาที่รังวัดสำเร็จ:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.warning("📸 **แนะแนวทาง:** ถ่ายรูปหน้าจอนี้เก็บไว้ทั้งคนขับรถและเจ้าของนา ตัวเลขนี้คำนวณตามจริงจากดาวเทียม ไม่มีใครโกงใครได้แน่นอนครับ")

    # ✅ แก้ไขจุดนี้: ขยับเว้นวรรคถอยหลังให้สอดคล้องกับโครงสร้างเงื่อนไข `else:` ของระบบ
    else:
        st.info("💡 **กำลังรอพิกัดจากคุณ...** โปรดกดอนุญาตให้แอปเข้าถึงตำแหน่ง (ถ้ามี) แผนที่จะซูมมาที่ตัวคุณทันที จากนั้นเริ่มคลิกปักหมุดให้ครบอย่างน้อย 3 จุดล้อมรอบที่นาได้เลยครับ")
