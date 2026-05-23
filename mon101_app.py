import streamlit as st
import streamlit.components.v1 as components
import json
import math

# ตั้งค่าหน้าเว็บ Streamlit
st.set_page_config(page_title="GPS วัดพื้นที่ (ไร่-งาน-วา)", layout="fullscreen")

st.title("🗺️ แอปวัดพื้นที่ด้วย GPS")
st.caption("ปักหมุดรอบ ๆ แปลงที่ดินเพื่อคำนวณพื้นที่เป็นหน่วย ไร่ - งาน - ตารางวา")

# คลังเก็บสถานะพิกัดหมุด (Session State)
if "markers" not in st.session_state:
    st.session_state.markers = []

# ฟังก์ชันคำนวณพื้นที่รูปหลายเหลี่ยมตามความโค้งของโลก (ตารางเมตร)
def calculate_area(coords):
    if len(coords) < 3:
        return 0.0
    total = 0.0
    R = 6378137.0  # รัศมีโลก (เมตร)
    
    for i in range(len(coords)):
        p1 = coords[i]
        p2 = coords[(i + 1) % len(coords)]
        # คำนวณแบบ Spherical Polygon Area
        total += (p2["lng"] - p1["lng"]) * math.pi / 180.0 * (2.0 + math.sin(p1["lat"] * math.pi / 180.0) + math.sin(p2["lat"] * math.pi / 180.0))
        
    return abs(total * R * R / 2.0)

# ฟังก์ชันแปลง ตารางเมตร -> ไร่ งาน วา
def format_thai_area(sq_meters):
    if sq_meters == 0:
        return "0 ไร่ 0 งาน 0 ตารางวา"
    
    total_sq_wah = sq_meters / 4.0
    rai = math.floor(total_sq_wah / 400)
    remain = total_sq_wah % 400
    ngan = math.floor(remain / 100)
    sq_wah = remain % 100
    
    return f"{rai} ไร่ {ngan} งาน {sq_wah:.1f} ตารางวา"

# ฝั่งควบคุมปุ่มใน Streamlit
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ ล้างหมุดทั้งหมด", use_container_width=True):
        st.session_state.markers = []
        st.rerun()

# รับข้อมูลพิกัดหมุดที่ส่งกลับมาจากแผนที่ HTML/JS ด้านล่าง
# (สตรีมลิตจะอ่านข้อมูลนี้ผ่านกลไกการสื่อสารของไอเฟรม)
query_params = st.query_params
if "new_markers" in query_params:
    try:
        st.session_state.markers = json.loads(query_params["new_markers"])
    except:
        pass

# คำนวณและแสดงผลลัพธ์
area_sm = calculate_area(st.session_state.markers)
thai_text = format_thai_area(area_sm)

st.markdown(f"""
<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
    <h3 style="margin: 0; color: #1f77b4;">พื้นที่คำนวณได้</h3>
    <h2 style="margin: 5px 0; color: #0f172a;">{thai_text}</h2>
    <small style="color: #64748b;">({area_sm:,.2f} ตารางเมตร)</small>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------
# ส่วนของแผนที่โต้ตอบ (HTML + Leaflet.js) แทรกลงใน Streamlit
# รองรับการดึง GPS ของมือถืออย่างถูกต้องผ่าน Browser HTTPS Security
# -----------------------------------------------------------------
markers_json = json.dumps(st.session_state.markers)

map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin:0; padding:0; }}
        #map {{ height: 450px; width: 100%; }}
        .gps-btn {{
            position: absolute; top: 10px; right: 10px; z-index: 1000;
            background: #2563eb; color: white; border: none; padding: 10px 15px;
            border-radius: 5px; font-weight: bold; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <button class="gps-btn" onclick="getLocation()">📍 ปักพิกัดปัจจุบัน (GPS)</button>
    <div id="map"></div>

    <script>
        // ดึงค่าหมุดเดิมจาก Python
        let currentMarkers = {markers_json};
        
        let map = L.map('map').setView([13.736, 100.523], 6);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}.png', {{
            maxZoom: 19
        }}).addTo(map);

        let markerLayers = [];
        let polygonLayer = null;

        // วาดหมุดเก่าที่มีอยู่
        if (currentMarkers.length > 0) {{
            currentMarkers.forEach(pt => addMarkerToMap(pt, false));
            updatePolygon();
            // ซูมไปที่กลุ่มหมุดล่าสุด
            let bounds = L.latLngBounds(currentMarkers.map(p => [p.lat, p.lng]));
            map.fitBounds(bounds);
        }}

        map.on('click', function(e) {{
            let pt = {{lat: e.latlng.lat, lng: e.latlng.lng}};
            currentMarkers.push(pt);
            addMarkerToMap(pt, true);
        }});

        function addMarkerToMap(pt, triggerUpdate) {{
            let marker = L.marker([pt.lat, pt.lng], {{draggable: true}}).addTo(map);
            markerLayers.push(marker);
            
            marker.on('dragend', function(e) {{
                let index = markerLayers.indexOf(marker);
                currentMarkers[index] = {{lat: e.target.getLatLng().lat, lng: e.target.getLatLng().lng}};
                updatePolygon();
                sendToPython();
            }});

            if (triggerUpdate) {{
                updatePolygon();
                sendToPython();
            }}
        }}

        function updatePolygon() {{
            if (polygonLayer) map.removeLayer(polygonLayer);
            let latlngs = currentMarkers.map(p => [p.lat, p.lng]);
            if (latlngs.length >= 3) {{
                polygonLayer = L.polygon(latlngs, {{color: '#2563eb', fillColor: '#3b82f6', fillOpacity: 0.4}}).addTo(map);
            }} else if (latlngs.length === 2) {{
                polygonLayer = L.polyline(latlngs, {{color: '#2563eb'}}).addTo(map);
            }}
        }}

        function getLocation() {{
            if (navigator.geolocation) {{
                navigator.geolocation.getCurrentPosition(function(position) {{
                    let pt = {{lat: position.coords.latitude, lng: position.coords.longitude}};
                    map.setView([pt.lat, pt.lng], 18);
                    currentMarkers.push(pt);
                    addMarkerToMap(pt, true);
                }}, function() {{
                    alert("กรุณาเปิดสิทธิ์แชร์ตำแหน่ง (GPS) บนเบราว์เซอร์ของคุณ");
                }}, {{enableHighAccuracy: true}});
            }}
        }}

        function sendToPython() {{
            // ส่งค่ากลับไปยัง Streamlit ผ่าน URL Parameter
            const url = new URL(window.parent.location.href);
            url.searchParams.set('new_markers', JSON.stringify(currentMarkers));
            window.parent.location.href = url.toString();
        }}
    </script>
</body>
</html>
"""

# แสดงผลส่วนแผนที่บนหน้าแอป Streamlit
components.html(map_html, height=470)
