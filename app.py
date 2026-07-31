import streamlit as st

# ---------------------------------------------------------
# 1. คลังรหัสภาษากลาง (Universal Concept Dictionary)
# ทุกภาษาที่มีความหมายเดียวกัน จะถูกจับคู่กับ "ไอดีตัวเลข" เดียวกัน
# ---------------------------------------------------------
UNIVERSAL_DICT = {
    101: {
        "th": "สวัสดี",
        "en": "hello",
        "jp": "こんにちは",
        "fr": "bonjour",
        "cn": "你好",
        "es": "hola"
    },
    102: {
        "th": "ขอบคุณ",
        "en": "thank you",
        "jp": "ありがとう",
        "fr": "merci",
        "cn": "谢谢",
        "es": "gracias"
    },
    103: {
        "th": "กาแฟ",
        "en": "coffee",
        "jp": "コーヒー",
        "fr": "café",
        "cn": "咖啡",
        "es": "café"
    },
    104: {
        "th": "ลาก่อน",
        "en": "goodbye",
        "jp": "さようなら",
        "fr": "au revoir",
        "cn": "再见",
        "es": "adiós"
    },
    105: {
        "th": "ยินดีที่ได้รู้จัก",
        "en": "nice to meet you",
        "jp": "はじめまして",
        "fr": "enchanté",
        "cn": "很高兴认识你",
        "es": "mucho gusto"
    }
}

# รายชื่อภาษาที่รองรับ
LANGUAGES = {
    "th": "🇹🇭 ภาษาไทย (Thai)",
    "en": "🇺🇸 ภาษาอังกฤษ (English)",
    "jp": "🇯🇵 ภาษาญี่ปุ่น (Japanese)",
    "fr": "🇫🇷 ภาษาฝรั่งเศส (French)",
    "cn": "🇨🇳 ภาษาจีน (Chinese)",
    "es": "🇪🇸 ภาษาสเปน (Spanish)"
}

# ---------------------------------------------------------
# 2. ฟังก์ชันแปลงข้อมูล
# ---------------------------------------------------------
def text_to_code(text: str, lang_code: str):
    """แปลงคำพูดจากภาษาใดก็ได้ ให้กลายเป็นไอดีตัวเลขกลาง"""
    cleaned_text = text.strip().lower()
    for code, translations in UNIVERSAL_DICT.items():
        if translations.get(lang_code, "").lower() == cleaned_text:
            return code
    return None

def code_to_text(code: int, target_lang_code: str):
    """แปลงไอดีตัวเลขกลาง ออกมาเป็นคำในภาษาปลายทาง"""
    if code in UNIVERSAL_DICT:
        return UNIVERSAL_DICT[code].get(target_lang_code, "ไม่มีคำแปลในภาษานี้")
    return "ไม่พบรหัสตัวเลขนี้"

# ---------------------------------------------------------
# 3. ส่วนแสดงผลบน Streamlit
# ---------------------------------------------------------
st.set_page_config(page_title="Universal Number Translator", page_icon="🔢")

st.title("🔢 Universal Language Code Translator")
st.caption("แปลงข้อความทุกภาษาในโลกให้กลายเป็น 'ตัวเลขเดียวกัน' เพื่อการสื่อสารแบบไร้พรมแดน")

st.divider()

# เลือกภาษาต้นทาง และ ปลายทาง
col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("1. ภาษาต้นทาง (Input Language)", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0)

with col2:
    target_lang = st.selectbox("2. ภาษาปลายทาง (Output Language)", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=1)

# ช่องพิมพ์ข้อความ
input_text = st.text_input("พิมพ์คำที่ต้องการแปล (เช่น สวัสดี / hello / コーヒー):", value="สวัสดี")

if st.button("🚀 สื่อสารผ่านรหัสตัวเลข", type="primary"):
    if input_text:
        # Step A: แปลงเป็นตัวเลขกลาง
        universal_code = text_to_code(input_text, source_lang)
        
        if universal_code:
            # แสดงผลกระบวนการทำงาน
            st.success("✅ แปลงภาษาเป็นตัวเลขสำเร็จ!")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            
            with res_col1:
                st.metric(label="คำต้นทาง", value=input_text)
                
            with res_col2:
                # ตัวเลขกลางไฮไลท์เด่นๆ
                st.metric(label="🔢 Universal Code (รหัสกลาง)", value=f"#{universal_code}")
                
            with res_col3:
                # แปลงจากตัวเลขเป็นภาษาปลายทาง
                translated_text = code_to_text(universal_code, target_lang)
                st.metric(label="คำในภาษาปลายทาง", value=translated_text)
                
            st.info(f"💡 **หลักการทำงาน:** ข้อความ '{input_text}' ถูกแปลงเป็นรหัสตัวเลข **{universal_code}** ซึ่งเครื่องของปลายทางอ่านรหัส **{universal_code}** นี้แล้วแสดงผลเป็น '{translated_text}' ทันทีโดยไม่ต้องแปลตรงๆ")
        else:
            st.error("❌ ไม่พบคำนี้ในคลังรหัสตัวเลข (ลองคำว่า: สวัสดี, ขอบคุณ, กาแฟ, ลาก่อน, ยินดีที่ได้รู้จัก)")
