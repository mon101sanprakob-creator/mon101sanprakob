import streamlit as st
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

# =========================================================
# ตั้งค่าหน้าแอป
# =========================================================
st.set_page_config(
    page_title="เครื่องมือวัดพื้นที่นา",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# ราคาค่าบริการ
# =========================================================
PLOW_PRICE = 250       # ไถนา บาท/ไร่
ROTARY_PRICE = 350     # ปั่นดิน บาท/ไร่

# =========================================================
# CSS สำหรับมือถือ
# =========================================================
st.markdown("""
<style>
    .main {
        padding-top: 10px;
    }

    .title {
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 20px;
    }

    .result-box {
        padding: 18px;
        border-radius: 15px;
        background: #f5f7f8;
        border: 1px solid #ddd;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .big-number {
        font-size: 30px;
        font-weight: bold;
        text-align: center;
    }

    .money {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
    }

    div.stButton > button {
        width: 100%;
        min-height: 48px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
    }

    @media (max-width: 768px) {
        .title {
            font-size: 25px;
        }

        .big-number {
            font-size: 25px;
        }

        .money {
            font-size: 24px;
        }
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# Session State
# =========================================================
if "points" not in st.session_state:
    st.session_state.points = []

if "measuring" not in st.session_state:
    st.session_state.measuring = False

if "map_center" not in st.session_state:
    st.session_state.map_center = [16.0538, 103.6520]


# =========================================================
# ฟังก์ชันคำนวณระยะทางบนโลก
# =========================================================
def distance_m(lat1, lon1, lat2, lon2):
    """
    ระยะทางระหว่างจุด GPS หน่วยเมตร
    Haversine formula
    """
    R = 6371000

    lat1 = radians(lat1)
    lat2 = radians(lat2)

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# =========================================================
# คำนวณพื้นที่ Polygon
# =========================================================
def polygon_area_m2(points):
    """
    คำนวณพื้นที่รูปหลายเหลี่ยมบนโลก
    ใช้พิกัดละติจูด/ลองจิจูดประมาณการเป็นพื้นที่ m²
    """

    if len(points) < 3:
        return 0

    # หาค่าเฉลี่ย latitude
    avg_lat = sum(p[0] for p in points) / len(points)

    # แปลงพิกัดเป็นเมตรโดยประมาณ
    lat_meter = 111320
    lon_meter = 111320 * cos(radians(avg_lat))

    xy = []

    for lat, lon in points:
        x = lon * lon_meter
        y = lat * lat_meter
        xy.append((x, y))

    area = 0

    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % len(xy)]

        area += (x1 * y2) - (x2 * y1)

    return abs(area) / 2


# =========================================================
# แปลง m² → ไร่ งาน ตารางวา
# =========================================================
def convert_area(area_m2):

    # 1 ไร่ = 1600 ตารางเมตร
    # 1 งาน = 400 ตารางเมตร
    # 1 ตารางวา = 4 ตารางเมตร

    total_square_wah = area_m2 / 4

    rai = int(total_square_wah // 400)

    remaining_wah = total_square_wah - (rai * 400)

    ngan = int(remaining_wah // 100)

    square_wah = remaining_wah - (ngan * 100)

    rai_decimal = area_m2 / 1600

    return rai, ngan, square_wah, rai_decimal


# =========================================================
# คำนวณราคา
# =========================================================
def calculate_price(rai_decimal, service):

    if service == "ไถนา":
        return rai_decimal * PLOW_PRICE

    if service == "ปั่นดิน":
        return rai_decimal * ROTARY_PRICE

    if service == "ไถนา + ปั่นดิน":
        return rai_decimal * (PLOW_PRICE + ROTARY_PRICE)

    return 0


# =========================================================
# หัวข้อ
# =========================================================
st.markdown(
    '<div class="title">🚜 เครื่องมือวัดพื้นที่นา</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">วัดแปลงนา • คำนวณไร่/งาน/ตารางวา • คิดค่าจ้าง</div>',
    unsafe_allow_html=True
)


# =========================================================
# ปุ่มควบคุม
# =========================================================
col1, col2 = st.columns(2)

with col1:
    if st.button(
        "📍 เริ่มวัดแปลง",
        use_container_width=True
    ):
        st.session_state.measuring = True
        st.session_state.points = []
        st.rerun()

with col2:
    if st.button(
        "🗑️ ล้างจุด / เริ่มใหม่",
        use_container_width=True
    ):
        st.session_state.points = []
        st.session_state.measuring = False
        st.rerun()


# =========================================================
# คำแนะนำ
# =========================================================
if st.session_state.measuring:
    st.info(
        "👆 แตะบนแผนที่ตามมุมแปลงนา "
        "อย่างน้อย 3 จุด แล้วกดปุ่มหยุดวัด"
    )


# =========================================================
# สร้างแผนที่
# =========================================================
m = folium.Map(
    location=st.session_state.map_center,
    zoom_start=16,
    control_scale=True,
    tiles=None
)

# แผนที่ถนน
folium.TileLayer(
    tiles="OpenStreetMap",
    name="แผนที่ถนน",
    control=True
).add_to(m)

# ภาพดาวเทียม Esri
folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/"
        "ArcGIS/rest/services/World_Imagery/"
        "MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri",
    name="🛰️ ภาพดาวเทียม",
    overlay=False,
    control=True
).add_to(m)

folium.LayerControl().add_to(m)


# =========================================================
# แสดงจุดที่ผู้ใช้เลือก
# =========================================================
for i, point in enumerate(st.session_state.points):

    folium.Marker(
        location=point,
        popup=f"จุดที่ {i + 1}",
        tooltip=f"จุด {i + 1}",
        icon=folium.DivIcon(
            html=f"""
            <div style="
                font-size:14px;
                font-weight:bold;
                color:white;
                background:#d32f2f;
                border-radius:50%;
                width:28px;
                height:28px;
                text-align:center;
                line-height:28px;
                border:2px solid white;
            ">
            {i + 1}
            </div>
            """
        )
    ).add_to(m)


# =========================================================
# วาดเส้นเชื่อม
# =========================================================
if len(st.session_state.points) >= 2:

    folium.PolyLine(
        st.session_state.points,
        color="red",
        weight=4,
        opacity=0.9
    ).add_to(m)


# =========================================================
# วาดพื้นที่
# =========================================================
if len(st.session_state.points) >= 3:

    folium.Polygon(
        locations=st.session_state.points,
        color="red",
        weight=3,
        fill=True,
        fill_color="red",
        fill_opacity=0.25
    ).add_to(m)


# =========================================================
# แสดงแผนที่
# =========================================================
map_data = st_folium(
    m,
    width=None,
    height=600,
    use_container_width=True,
    returned_objects=[
        "last_clicked"
    ]
)


# =========================================================
# รับจุดจากการคลิก
# =========================================================
if st.session_state.measuring:

    clicked = map_data.get("last_clicked")

    if clicked:

        lat = clicked.get("lat")
        lon = clicked.get("lng")

        if lat is not None and lon is not None:

            new_point = (lat, lon)

            # ป้องกันการคลิกจุดเดิมซ้ำ
            is_duplicate = False

            for p in st.session_state.points:

                if (
                    abs(p[0] - lat) < 0.000001
                    and
                    abs(p[1] - lon) < 0.000001
                ):
                    is_duplicate = True
                    break

            if not is_duplicate:

                st.session_state.points.append(new_point)

                st.rerun()


# =========================================================
# ปุ่มหยุดวัด
# =========================================================
if st.session_state.measuring:

    if len(st.session_state.points) >= 3:

        if st.button(
            "✅ หยุดวัดและคำนวณพื้นที่",
            use_container_width=True
        ):
            st.session_state.measuring = False
            st.rerun()


# =========================================================
# ผลการวัด
# =========================================================
if len(st.session_state.points) >= 3:

    area_m2 = polygon_area_m2(
        st.session_state.points
    )

    rai, ngan, square_wah, rai_decimal = convert_area(
        area_m2
    )

    st.markdown("---")

    st.subheader("📐 ผลการวัดแปลงนา")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "พื้นที่",
            f"{area_m2:,.2f} ตร.ม."
        )

    with col2:
        st.metric(
            "พื้นที่ไทย",
            f"{rai} ไร่ {ngan} งาน"
        )

    with col3:
        st.metric(
            "ตารางวา",
            f"{square_wah:,.2f}"
        )

    st.markdown(
        f"""
        <div class="result-box">
            <div style="text-align:center;">
                <div>🌾 พื้นที่แปลงนี้</div>
                <div class="big-number">
                    {rai} ไร่ {ngan} งาน {square_wah:,.2f} ตารางวา
                </div>
                <div>
                    เท่ากับ {rai_decimal:,.4f} ไร่
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # เลือกประเภทงาน
    # =====================================================
    st.subheader("🚜 คิดค่าจ้าง")

    service = st.radio(
        "เลือกงาน",
        [
            "ไถนา",
            "ปั่นดิน",
            "ไถนา + ปั่นดิน"
        ],
        horizontal=False
    )

    price = calculate_price(
        rai_decimal,
        service
    )

    # =====================================================
    # แสดงราคา
    # =====================================================
    if service == "ไถนา":
        rate_text = "250 บาท / ไร่"

    elif service == "ปั่นดิน":
        rate_text = "350 บาท / ไร่"

    else:
        rate_text = "600 บาท / ไร่"


    st.markdown(
        f"""
        <div class="result-box">
            <div style="text-align:center;">
                <div>🚜 งานที่เลือก</div>
                <h2>{service}</h2>

                <div>
                    อัตราค่าบริการ {rate_text}
                </div>

                <hr>

                <div>💰 ยอดเงินที่ต้องจ่าย</div>

                <div class="money">
                    {price:,.2f} บาท
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # รายละเอียดการคิดเงิน
    # =====================================================
    st.subheader("🧾 รายละเอียด")

    st.write(
        f"พื้นที่ = **{rai_decimal:,.4f} ไร่**"
    )

    if service == "ไถนา":

        st.write(
            f"ค่าจ้าง = {rai_decimal:,.4f} × 250"
        )

    elif service == "ปั่นดิน":

        st.write(
            f"ค่าจ้าง = {rai_decimal:,.4f} × 350"
        )

    else:

        st.write(
            f"ค่าจ้าง = {rai_decimal:,.4f} × (250 + 350)"
        )

    st.success(
        f"💵 ลูกค้าต้องจ่าย **{price:,.2f} บาท**"
    )


# =========================================================
# ยังไม่มีพื้นที่
# =========================================================
else:

    st.markdown("---")

    st.info(
        "📍 กด **เริ่มวัดแปลง** แล้วแตะตามมุมที่ดินบนแผนที่ "
        "อย่างน้อย 3 จุด"
    )

    st.markdown(
        """
        ### 💰 ราคาที่ตั้งไว้

        | งาน | ราคา |
        |---|---:|
        | 🚜 ไถนา | **250 บาท/ไร่** |
        | 🔄 ปั่นดิน | **350 บาท/ไร่** |
        | 🚜🔄 ไถ + ปั่น | **600 บาท/ไร่** |

        **หน่วยพื้นที่**
        
        - 1 ไร่ = 4 งาน
        - 1 งาน = 100 ตารางวา
        - 1 ไร่ = 400 ตารางวา
        - 1 ไร่ = 1,600 ตารางเมตร
        """
    )


# =========================================================
# ส่วนท้าย
# =========================================================
st.markdown("---")

st.caption(
    "🚜 เครื่องมือวัดพื้นที่นา | "
    "ใช้สำหรับประมาณพื้นที่และคำนวณค่าบริการ"
)
