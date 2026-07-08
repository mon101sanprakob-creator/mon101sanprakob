import streamlit as st
from engine import SynapseEngine
from engine.constants import WEEKDAYS, MONTHS, ZODIAC

st.title("SYNAPSE")

weekday = st.selectbox("วัน", list(WEEKDAYS))
month = st.selectbox("เดือน", list(MONTHS))
zodiac = st.selectbox("ปีนักษัตร", list(ZODIAC))
lunar = st.slider("ค่ำจันทรคติ", 1, 30, 1)

if st.button("คำนวณ"):
    engine = SynapseEngine()
    result = engine.calculate(
        WEEKDAYS[weekday],
        MONTHS[month],
        ZODIAC[zodiac],
        lunar,
    )

    st.write("ผลลัพธ์")
    st.json(result)
