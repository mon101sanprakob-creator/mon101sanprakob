import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="SYNAPSE",
    page_icon="🧠",
    layout="wide"
)

image = Image.open("logo1.png")

st.image(image, width=300)

st.markdown(
"""
<h1 style='text-align:center;color:#FFD700;'>
SYNAPSE
</h1>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<h4 style='text-align:center;color:white;'>
SOUND & VISUAL THERAPY
</h4>
""",
unsafe_allow_html=True
)

st.markdown(
"""
<h3 style='text-align:center;color:#00E5FF;'>
อยู่นิ้งๆไม่เจ็บตัว
</h3>
""",
unsafe_allow_html=True
)

st.divider()

day = st.selectbox(
"วัน",
[
"อาทิตย์",
"จันทร์",
"อังคาร",
"พุธ",
"พฤหัส",
"ศุกร์",
"เสาร์"
])

month = st.selectbox(
"เดือน",
[
"มกราคม",
"กุมภาพันธ์",
"มีนาคม",
"เมษายน",
"พฤษภาคม",
"มิถุนายน",
"กรกฎาคม",
"สิงหาคม",
"กันยายน",
"ตุลาคม",
"พฤศจิกายน",
"ธันวาคม"
])

zodiac = st.selectbox(
"ปีนักษัตร",
[
"ชวด",
"ฉลู",
"ขาล",
"เถาะ",
"มะโรง",
"มะเส็ง",
"มะเมีย",
"มะแม",
"วอก",
"ระกา",
"จอ",
"กุน"
])

moon = st.radio(
"ข้าง",
[
"ขึ้น",
"แรม"
])

lunar_day = st.slider(
"ค่ำ",
1,
15,
1
)
fig = go.Figure(go.Indicator(

    mode="gauge+number",

    value=result["energy"],

    title={"text":"SYNAPSE ENERGY"},

    gauge={

        "axis":{"range":[0,100]},

        "bar":{"color":"gold"},

        "steps":[

            {"range":[0,30],"color":"#440000"},

            {"range":[30,70],"color":"#222244"},

            {"range":[70,100],"color":"#003300"}

        ]

    }

))

st.plotly_chart(fig,use_container_width=True)
if st.button("🚀 CALCULATE"):

    st.success("เวอร์ชันแรกกำลังคำนวณ...")
