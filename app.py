import streamlit as st
import requests

# ---------------------------------------------------------
# ฟังก์ชันดึงรหัสความหมายสากล (QID) จาก Wikidata API แบบเรียลไทม์
# ---------------------------------------------------------
def get_wikidata_id(search_text, lang_code="th"):
    """ค้นหารหัสตัวเลขความหมายกลาง (QID) จากคำศัพท์ทุกคำในโลก"""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": lang_code,
        "search": search_text,
        "limit": 1
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("search"):
            entity = data["search"][0]
            return {
                "qid": entity["id"],                          # รหัสตัวเลขกลาง (เช่น Q1020)
                "label": entity.get("label", search_text),     # คำศัพท์
                "description": entity.get("description", "") # คำอธิบายความหมาย
            }
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
    return None

def get_translation_from_qid(qid, target_lang_code="en"):
    """ดึงคำแปลในภาษาปลายทางจากรหัสตัวเลขกลาง (QID)"""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": qid,
        "props": "labels|descriptions",
        "languages": target_lang_code
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        entities = data.get("entities", {})
        if qid in entities:
            labels = entities[qid].get("labels", {})
            if target_lang_code in labels:
                return labels[target_lang_code]["value"]
    except Exception:
        pass
    return "ไม่พบคำแปลในภาษานี้"

# ---------------------------------------------------------
# รายชื่อภาษาที่รองรับ
# ---------------------------------------------------------
LANGUAGES = {
    "th": "🇹🇭 ภาษาไทย (Thai)",
    "en": "🇺🇸 ภาษาอังกฤษ (English)",
    "ja": "🇯🇵 ภาษาญี่ปุ่น (Japanese)",
    "zh": "🇨🇳 ภาษาจีน (Chinese)",
    "fr": "🇫🇷 ภาษาฝรั่งเศส (French)",
    "es": "🇪🇸 ภาษาสเปน (Spanish)",
    "de": "🇩🇪 ภาษาเยอรมัน (German)",
    "ko": "🇰🇷 ภาษาเกาหลี (Korean)",
    "ru": "🇷🇺 ภาษารัสเซีย (Russian)",
    "ar": "🇦🇪 ภาษาอาหรับ (Arabic)"
}

# ---------------------------------------------------------
# หน้าตาแอป Streamlit
# ---------------------------------------------------------
st.set_page_config(page_title="Universal Live Translator", page_icon="🌐", layout="wide")

st.title("🌐 Universal Language Code Translator (Live Wikidata)")
st.caption("แปลง **ทุกคำศัพท์ในโลก** ให้กลายเป็น **'รหัสตัวเลขความหมายเดียวกัน (QID)'** ผ่านระบบ Wikidata สากล")

st.divider()

col1, col2 = st.columns(2)
with col1:
    src_lang = st.selectbox("1. ภาษาต้นทาง (Input)", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0)

with col2:
    tgt_lang = st.selectbox("2. ภาษาปลายทาง (Output)", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=1)

user_input = st.text_input("พิมพ์คำศัพท์ / ข้อความอะไรก็ได้ในโลก (เช่น สับปะรด / คอมพิวเตอร์ / ความสุข / รถไฟ):", value="สับปะรด")

if st.button("🚀 ค้นหารหัสความหมายกลางและแปลภาษา", type="primary", use_container_width=True):
    if user_input:
        with st.spinner("กำลังค้นหารหัสตัวเลขความหมายสากล..."):
            result = get_wikidata_id(user_input, src_lang)
            
            if result:
                qid = result["qid"]
                description = result["description"]
                
                # ดึงคำแปลปลายทาง
                translated_text = get_translation_from_qid(qid, tgt_lang)
                
                st.success("✅ แปลงภาษาด้วยรหัสตัวเลขสากลสำเร็จ!")
                
                c1, c2, c3 = st.columns([1, 1.2, 1])
                
                with c1:
                    st.info("📤 **ภาษาต้นทาง**")
                    st.metric("คำที่พิมพ์", user_input)
                    st.caption(f"คำอธิบาย: {description if description else '-'}")
                    
                with c2:
                    st.warning("⚡ **รหัสตัวเลขสากล (Universal ID)**")
                    st.metric("Wikidata QID", f"[{qid}]")
                    st.caption("รหัสตัวเลขนี้หมายถึงสิ่งนี้เหมือนกันทั่วโลก")
                    
                with c3:
                    st.success("📥 **ภาษาปลายทาง**")
                    st.metric("คำแปลปลายทาง", translated_text)
                    
                st.divider()
                st.write(f"💡 **หลักการ:** ไม่ว่าจะพิมพ์ภาษาไหนก็ตาม ระบบจะค้นหาว่าสิ่งนี้คือรหัสตัวเลข **{qid}** แล้วนำรหัส **{qid}** ไปดึงคำว่า **'{translated_text}'** ในภาษาปลายทางมาแสดงทันทีโดยไม่ผ่านการเดาความหมาย!")
            else:
                st.error("❌ ไม่พบรหัสความหมายของคำนี้ กรุณาลองใช้คำอื่นหรือตรวจสอบคำผิด")
