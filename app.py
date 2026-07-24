import streamlit as st

st.set_page_config(page_title="Neon Sidebar Menu", layout="wide")

# ใส่ CSS ปรับแต่งความงดงามเรืองแสง
st.markdown("""
    <style>
    /* พื้นหลังฝั่ง Sidebar ให้เป็นโทนเข้มเข้ากัน */
    [data-testid="stSidebar"] {
        background-color: #0a0a10 !important;
    }
    
    /* ปรับแต่งปุ่มใน Sidebar ด้านซ้าย */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        padding: 14px 20px !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        background: linear-gradient(135deg, #7A00FF, #FF0055) !important;
        border: 2px solid #00F0FF !important;
        border-radius: 14px !important;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.7), 0 0 25px rgba(255, 0, 85, 0.5) !important;
        text-shadow: 0 0 8px #000000 !important;
        transition: all 0.3s ease-in-out !important;
        margin-bottom: 12px !important;
    }

    /* เอฟเฟกต์ตอนกด/แตะปุ่ม */
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: scale(1.03) !important;
        background: linear-gradient(135deg, #FF0055, #00F0FF) !important;
        color: #FFFF00 !important;
        border-color: #00FF66 !important;
        box-shadow: 0 0 25px #00FF66, 0 0 40px #00F0FF !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------- เมนูด้านซ้าย (Sidebar) -----------------
st.sidebar.title("📌 เมนูความสามารถ")
st.sidebar.write("---")

# สร้างปุ่มใหญ่ๆ เรืองแสงใน Sidebar
btn1 = st.sidebar.button("🔮 1. ถอดรหัสดวงชะตา")
btn2 = st.sidebar.button("📊 2. วิเคราะห์กราฟชีวิต")
btn3 = st.sidebar.button("📱 3. ตรวจเบอร์มงคล")
btn4 = st.sidebar.button("🏠 กลับหน้าหลัก")

# ----------------- ส่วนแสดงผลหน้าหลัก -----------------
st.title("🌟 หน้าต่างแสดงผลหลัก")
st.write("ลองกดปุ่มเมนูด้านซ้ายมือดูครับ ปุ่มจะใหญ่ สว่างเรืองแสง และเห็นตัวหนังสือชัดเจนมากๆ!")
