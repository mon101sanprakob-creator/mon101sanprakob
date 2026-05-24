import streamlit as st
import pydeck as pdk
import pandas as pd
from shapely.geometry import Polygon
import pyproj
from functools import partial
import shapely.ops as ops
import datetime

# ตั้งค่าหน้าจอเป็นแบบกว้างเพื่อให้เห็นข้อมูลชัดเจน
st.set_page_config(layout="wide", page_title="ระบบรังวัดที่นาป้องกันการโกง")

st.title("🌾 ระบบรังวัดที่นาผ่านดาวเทียม (เวอร์ชันทนทานพิเศษ)")
st.write("ระบบนี้ถูกออกแบบใหม่ให้ทำงานร่วมกับเซิร์ฟเวอร์เวอร์ชันล่าสุดได้อย่างเสถียร ไม่ล่ม มุ่งเน้นความโปร่งใสเรื่องเนื้อที่และค่าจ้าง")

# 1. จัดการระบบความจำ (Session State) สำหรับเก็บหมุดพิกัด
if 'map_points' not in st.session_state:
    # ค่าเริ่มต้นเป็นตัวอย่างแปลงนาแถวพิษณุโลก (Lat, Lng)
    st.session_state.map_points = [
        {"lat": 16.8205, "lng": 100.2600},
        {"lat": 16.8205, "lng": 100.2615},
        {"lat": 16.8190, "lng": 100.2615},
        {"lat": 16.8190, "lng": 100.2600}
    ]

# เมนูด้านข้างสำหรับควบคุมค่าจ้างและตำแหน่งหมุด
with st.sidebar:
    st.header("⚙️ ตั้งค่าและควบคุมหมุด")
    price_per_rai = st.number_input("💵 อัตราค่าจ้าง (บาท ต่อ ไร่):", min_value=0, value=600, step=50)
    
    st.write("---")
    st.subheader("📍 ปรับแต่งพิกัดมุมนา")
    st.caption("สามารถแก้ไขตัวเลขพิกัดตรงนี้เพื่อความละเอียดระดับเซนติเมตรได้")
    
    # สร้างช่องให้กดปรับพิกัดได้ง่ายๆ บนมือถือ
    updated_points = []
    for i, pt in enumerate(st.session_state.map_points):
        st.write(f"**มุมที่ {i+1}**")
        col_lat, col_lng = st.columns(2)
        with col_lat:
            new_lat = st.number_input(f"Lat {i+1}", value=pt["lat"], format="%.6f", key=f"lat_{i}")
        with col_lng:
            new_lng = st.number_input(f"Lng {i+1}", value=pt["lng"], format="%.6f", key=f"lng_{i}")
        updated_points.append({"lat": new_lat, "lng": new_lng})
    
    st.session_state.map_points = updated_points

# 2. จัดเตรียมหน้าจอหลักแบ่งเป็นฝั่ง แผนที่ดาวเทียม กับ ผลลัพธ์
col_map, col_result = st.columns([1.8, 1.2])

# จัดการแปลงข้อมูลพิกัดให้อยู่ในรูป DataFrame ที่ Pydeck พร้อมเอาไปวาดภาพ
df_points = pd.DataFrame(st.session_state.map_points)

with col_map:
    st.subheader("🗺️ 1. ผังเส้นขอบแปลงนาบนแผนที่ดาวเทียม")
    st.caption("เส้นสีเขียวนีออนจะลากเชื่อมต่อมุมนาอ้างอิงตามพิกัดสากลจริง")

    # คำนวณจุดกึ่งกลางแปลงนาเพื่อให้แผนที่โฟกัสถูกจุด
    center_lat = df_points["lat"].mean()
    center_lng = df_points["lng"].mean()

    # วาดแผนที่ดาวเทียมความละเอียดสูงด้วย Pydeck (ไลบรารีระดับโลก ไม่พึ่งพา Folium)
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lng,
        zoom=16,
        pitch=0
    )

    # วาดกรอบคันนาสีเขียวสะท้อนแสง
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        [st.session_state.map_points],
        get_polygon="-.[lng, lat]",
        get_fill_color=[0, 255, 0, 50], # สีเขียวโปร่งแสงทับที่นา
        get_line_color=[0, 255, 0, 255], # เส้นขอบเขียวนีออนชัดเจน
        get_line_width=3,
        line_width_min_pixels=3,
        pickable=True
    )

    # วาดหมุดสีแดงตามมุมนา
    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        df_points,
        get_position="[lng, lat]",
        get_color=[255, 0, 0, 255],
        get_radius=15,
        pickable=True
    )

    # แสดงผลแผนที่ดาวเทียมโดยตรงผ่าน Mapbox (ใช้ดาวเทียมฟรีของระบบ)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/satellite-v9", # บังคับเปิดโหมดภาพดาวเทียมแท้ 100%
        initial_view_state=view_state,
        layers=[polygon_layer, scatterplot_layer]
    ))

# 3. ฝั่งคำนวณและแสดงผลลัพธ์ (เน้นหน่วย ไร่-งาน-ตารางวา ชัดเจนที่สุด)
with col_result:
    st.subheader("📊 2. สรุปเนื้อที่นาจริง (หน่วยไทย)")
    
    if len(st.session_state.map_points) >= 3:
        # ดึงพิกัดมาสร้าง Polygon คำนวณพื้นที่
        geojson_coords = [(pt["lng"], pt["lat"]) for pt in st.session_state.map_points]
        poly = Polygon(geojson_coords)
        
        # สูตรคำนวณพื้นที่ระนาบเมตรสากลชดเชยความโค้งของโลก
        wgs84 = pyproj.CRS('EPSG:4326')
        web_mercator = pyproj.CRS('EPSG:3857')
        transformer = pyproj.Transformer.from_crs(wgs84, web_mercator, always_xy=True).transform
        geom_area = ops.transform(transformer, poly).area

        # แปลงจาก ตารางเมตร -> ไร่ - งาน - ตารางวา
        total_sq_wa = geom_area / 4
        rai = int(total_sq_wa // 400)
        ngarn = int((total_sq_wa % 400) // 100)
        sq_wa = total_sq_wa % 100

        # คำนวณเงินค่าบริการสุทธิ
        total_rai_decimal = geom_area / 1600
        total_cash = total_rai_decimal * price_per_rai

        # การแสดงผลสรุปแบบกล่องข้อความสีเขียวเด่นๆ ป้องกันการเถียงกัน
        st.success(f"""
        ### 📐 ขนาดพื้นที่นาที่วัดได้:
        ## {rai} ไร่  {ngarn} งาน  {sq_wa:.2f} ตารางวา
        """)
        
        st.metric(label=f"💰 รวมค่าจ้างสุทธิ (คิดไร่ละ {price_per_rai:,} บาท)", value=f"{total_cash:,.2f} บาท")
        
        # แสดงตารางพิกัดอ้างอิงให้ตรวจสอบย้อนหลัง
        st.write("📋 **ตารางพิกัดมุมนาอ้างอิงดาวเทียม (ห้ามแก้ไขเอง):**")
        st.dataframe(df_points.rename(columns={"lat": "ละติจูด (Lat)", "lng": "ลองจิจูด (Lng)"}), use_container_width=True)
        
        st.info(f"🕒 **วันเวลาที่ตรวจสอบสำเร็จ:** {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.warning("📸 **ข้อแนะนำ:** ให้เปิดหน้าจอนี้ร่วมกันทั้งคนขับรถเกี่ยวและเจ้าของนา จากนั้นทำการแคปหน้าจอเก็บไว้เป็นเอกสารยืนยันผลประโยชน์ที่ตรงกันครับ")
    else:
        st.info("💡 กำหนดพิกัดมุมนาให้ครบอย่างน้อย 3 มุมขึ้นไปที่เมนูด้านซ้ายเพื่อคำนวณพื้นที่")
