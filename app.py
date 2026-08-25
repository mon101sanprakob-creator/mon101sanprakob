import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="🚜 เครื่องมือวัดพื้นที่นา",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# ราคาค่าบริการ
# =========================================================
PLOW_PRICE = 250
ROTARY_PRICE = 350

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: sans-serif;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1200px;
    margin: auto;
}

.title {
    text-align: center;
    font-size: 30px;
    font-weight: 800;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 15px;
}

.info-box {
    background: #f4f7f8;
    border-radius: 14px;
    padding: 15px;
    margin-top: 10px;
}

.money-box {
    background: #eef8ee;
    border: 2px solid #55a655;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}

.money {
    font-size: 32px;
    font-weight: 800;
}

@media (max-width: 700px) {
    .title {
        font-size: 24px;
    }

    .money {
        font-size: 26px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# หัวข้อ
# =========================================================
st.markdown(
    '<div class="title">🚜 เครื่องมือวัดพื้นที่นา</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">GPS • ภาพดาวเทียม • วัดไร่/งาน/ตารางวา • คิดค่าจ้าง</div>',
    unsafe_allow_html=True
)


# =========================================================
# JavaScript + Leaflet
# =========================================================
html_code = f"""
<!DOCTYPE html>
<html>
<head>

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<link rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

<link rel="stylesheet"
      href="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.18.0/dist/leaflet-geoman.css"/>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script src="https://unpkg.com/@geoman-io/leaflet-geoman-free@2.18.0/dist/leaflet-geoman.min.js"></script>

<style>

html, body {{
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
}}

#map {{
    width: 100%;
    height: 650px;
    border-radius: 15px;
}}

.gps-box {{
    position: absolute;
    z-index: 9999;
    top: 10px;
    left: 50px;
    background: white;
    padding: 10px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,.25);
    font-size: 13px;
}}

</style>

</head>

<body>

<div id="map"></div>

<div class="gps-box">
    📍 <b>ตำแหน่งปัจจุบัน</b>
    <div id="gps">กำลังค้นหาตำแหน่ง...</div>
</div>

<script>

let map;
let currentMarker = null;
let accuracyCircle = null;

let farmLayer = null;


// ========================================================
// เริ่มแผนที่
// ========================================================

map = L.map('map', {{
    zoomControl: true
}}).setView([16.0538, 103.6520], 15);


// ========================================================
// ภาพดาวเทียม
// ========================================================

L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
    {{
        maxZoom: 20,
        attribution: 'Tiles © Esri'
    }}
).addTo(map);


// ========================================================
// แผนที่ถนน
// ========================================================

let roadLayer = L.tileLayer(
    'https://{{s}}.tile.openstreetmap.org/{{z}}/{{y}}/{{x}}.png',
    {{
        maxZoom: 20,
        attribution: '© OpenStreetMap'
    }}
);


// ========================================================
// Layer Control
// ========================================================

let satellite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
    {{
        maxZoom: 20
    }}
);

let baseMaps = {{
    "🛰️ ดาวเทียม": satellite,
    "🗺️ แผนที่ถนน": roadLayer
}};

L.control.layers(baseMaps).addTo(map);


// ========================================================
// GPS
// ========================================================

function startGPS() {{

    if (!navigator.geolocation) {{

        document.getElementById("gps").innerHTML =
            "โทรศัพท์/เบราว์เซอร์ไม่รองรับ GPS";

        return;
    }}

    navigator.geolocation.watchPosition(

        function(position) {{

            let lat = position.coords.latitude;
            let lon = position.coords.longitude;

            let accuracy = position.coords.accuracy;

            document.getElementById("gps").innerHTML =
                "Lat: " + lat.toFixed(7) +
                "<br>Lng: " + lon.toFixed(7) +
                "<br>ความแม่นยำ ±" +
                accuracy.toFixed(1) + " ม.";

            if (currentMarker) {{

                currentMarker.setLatLng([lat, lon]);

            }} else {{

                currentMarker = L.marker(
                    [lat, lon],
                    {{
                        title: "ตำแหน่งของฉัน"
                    }}
                ).addTo(map);

                currentMarker.bindPopup(
                    "<b>📍 ตำแหน่งของฉัน</b><br>" +
                    "Lat: " + lat.toFixed(7) +
                    "<br>Lng: " + lon.toFixed(7) +
                    "<br>Accuracy ±" +
                    accuracy.toFixed(1) + " m"
                );

                map.setView(
                    [lat, lon],
                    18
                );
            }}


            if (accuracyCircle) {{

                accuracyCircle.setLatLng(
                    [lat, lon]
                );

                accuracyCircle.setRadius(
                    accuracy
                );

            }} else {{

                accuracyCircle =
                    L.circle(
                        [lat, lon],
                        {{
                            radius: accuracy,
                            color: "#0066ff",
                            fillColor: "#3388ff",
                            fillOpacity: 0.12
                        }}
                    ).addTo(map);

            }}

        },

        function(error) {{

            let message = "";

            if (error.code === 1) {{
                message =
                    "ไม่ได้อนุญาตให้ใช้ตำแหน่ง";
            }}

            else if (error.code === 2) {{
                message =
                    "ไม่สามารถหาตำแหน่งได้";
            }}

            else if (error.code === 3) {{
                message =
                    "GPS ใช้เวลานานเกินไป";
            }}

            document.getElementById("gps").innerHTML =
                message;

        }},

        {{
            enableHighAccuracy: true,
            maximumAge: 1000,
            timeout: 10000
        }}

    );

}}


startGPS();


// ========================================================
// Geoman
// ========================================================

map.pm.addControls({{

    position: 'topleft',

    drawMarker: false,
    drawCircle: false,
    drawCircleMarker: false,
    drawPolyline: false,
    drawRectangle: false,

    drawPolygon: true,

    editMode: true,
    dragMode: false,
    cutPolygon: false,
    removalMode: true

}});


// ========================================================
// เมื่อสร้างพื้นที่
// ========================================================

map.on(
    'pm:create',
    function(e) {{

        if (farmLayer) {{
            map.removeLayer(farmLayer);
        }}

        farmLayer = e.layer;

        farmLayer.setStyle({{
            color: '#ff0000',
            weight: 4,
            fillColor: '#ff0000',
            fillOpacity: 0.20
        }});

        calculateArea();

        farmLayer.on(
            'pm:edit',
            function() {{
                calculateArea();
            }}
        );

    }}
);


// ========================================================
// คำนวณพื้นที่
// ========================================================

function calculateArea() {{

    if (!farmLayer) return;

    let latlngs =
        farmLayer.getLatLngs()[0];

    if (latlngs.length < 3) return;


    // ====================================================
    // แปลง lat/lng เป็นเมตรโดยประมาณ
    // ====================================================

    let avgLat = 0;

    latlngs.forEach(function(p) {{
        avgLat += p.lat;
    }});

    avgLat =
        avgLat / latlngs.length;


    let latMeter = 111320;

    let lonMeter =
        111320 *
        Math.cos(
            avgLat *
            Math.PI / 180
        );


    let xy = [];

    latlngs.forEach(function(p) {{

        xy.push({{
            x: p.lng * lonMeter,
            y: p.lat * latMeter
        }});

    }});


    let area = 0;

    for (
        let i = 0;
        i < xy.length;
        i++
    ) {{

        let j =
            (i + 1) %
            xy.length;

        area +=
            xy[i].x *
            xy[j].y -
            xy[j].x *
            xy[i].y;

    }}


    area =
        Math.abs(area) / 2;


    // ====================================================
    // แปลงหน่วย
    // ====================================================

    let squareWah =
        area / 4;

    let rai =
        Math.floor(
            squareWah / 400
        );

    let remain =
        squareWah -
        (rai * 400);

    let ngan =
        Math.floor(
            remain / 100
        );

    let wah =
        remain -
        (ngan * 100);

    let raiDecimal =
        area / 1600;


    // ====================================================
    // ส่งข้อมูลออก
    // ====================================================

    document.getElementById(
        "area-result"
    ).innerHTML =

        "<b>📐 พื้นที่แปลง</b><br>" +

        area.toFixed(2) +
        " ตารางเมตร<br><br>" +

        "<b>" +

        rai +
        " ไร่ " +

        ngan +
        " งาน " +

        wah.toFixed(2) +
        " ตารางวา" +

        "</b><br><br>" +

        "เท่ากับ " +

        raiDecimal.toFixed(4) +

        " ไร่";


    document.getElementById(
        "price-plow"
    ).innerHTML =

        (
            raiDecimal *
            {PLOW_PRICE}
        ).toFixed(2) +
        " บาท";


    document.getElementById(
        "price-rotary"
    ).innerHTML =

        (
            raiDecimal *
            {ROTARY_PRICE}
        ).toFixed(2) +
        " บาท";


    document.getElementById(
        "price-total"
    ).innerHTML =

        (
            raiDecimal *
            ({PLOW_PRICE} + {ROTARY_PRICE})
        ).toFixed(2) +
        " บาท";

}}


</script>


<div style="
    padding:12px;
    margin-top:10px;
    background:#f5f5f5;
    border-radius:12px;
">

<div id="area-result">
    📐 ยังไม่ได้วัดพื้นที่
</div>

<hr>

<div>
    🚜 ไถนา {PLOW_PRICE} บาท/ไร่ :
    <b id="price-plow">0.00 บาท</b>
</div>

<div>
    🔄 ปั่นดิน {ROTARY_PRICE} บาท/ไร่ :
    <b id="price-rotary">0.00 บาท</b>
</div>

<hr>

<div style="
    font-size:20px;
    font-weight:bold;
">

🚜🔄 ไถ + ปั่น :
<span id="price-total">
0.00 บาท
</span>

</div>

</div>

</body>
</html>
"""

components.html(
    html_code,
    height=850,
    scrolling=False
)


# =========================================================
# ราคาค่าบริการ
# =========================================================

st.markdown("---")

st.subheader("💰 อัตราค่าบริการ")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🚜 ไถนา",
        "250 บาท / ไร่"
    )

with col2:
    st.metric(
        "🔄 ปั่นดิน",
        "350 บาท / ไร่"
    )

with col3:
    st.metric(
        "🚜🔄 ไถ + ปั่น",
        "600 บาท / ไร่"
    )


# =========================================================
# วิธีใช้
# =========================================================

with st.expander("📖 วิธีใช้"):

    st.markdown("""
### 1️⃣ เปิด GPS

เมื่อเปิดแอป โทรศัพท์จะถามว่า

**อนุญาตให้เว็บไซต์เข้าถึงตำแหน่งหรือไม่**

ให้กด **อนุญาต**

จุด GPS สีน้ำเงินจะแสดงตำแหน่งของคุณ

---

### 2️⃣ เลือกภาพดาวเทียม

กดปุ่ม Layer ที่มุมแผนที่ แล้วเลือก

**🛰️ ดาวเทียม**

เพื่อดูแปลงนา

---

### 3️⃣ วาดแปลงนา

กดเครื่องมือ **รูปหลายเหลี่ยม (Polygon)**

แล้วแตะตามมุมแปลงนา

เมื่อกลับมาที่จุดแรก จะได้พื้นที่แปลง

---

### 4️⃣ แก้แนวเขต

ใช้เครื่องมือ **Edit**

แล้วลากจุดแต่ละจุดไปยังตำแหน่งที่ต้องการ

พื้นที่จะถูกคำนวณใหม่

---

### 5️⃣ ดูเงินค่าจ้าง

ระบบจะคำนวณให้ทันที

**ไถ = 250 บาท/ไร่**

**ปั่น = 350 บาท/ไร่**

**ไถ + ปั่น = 600 บาท/ไร่**

---

### 📏 หน่วยพื้นที่ไทย

**1 ไร่ = 4 งาน**

**1 งาน = 100 ตารางวา**

**1 ไร่ = 400 ตารางวา**

**1 ไร่ = 1,600 ตารางเมตร**
""")


st.caption(
    "🚜 เครื่องมือวัดพื้นที่นา | "
    "ใช้สำหรับประมาณพื้นที่และคำนวณค่าบริการ"
)
