import streamlit as st

# ---------------------------------------------------------
# 1. คลังรหัสความหมายสากล (Wikidata Universal QID Engine)
# เชื่อมโยง: รหัสกลาง (QID) <-> ภาษาพูด <-> คำอ่าน <-> ภาษามือ
# ---------------------------------------------------------
UNIVERSAL_DATABASE = {
    "Q1020": {
        "concept": "กาแฟ (Coffee / ☕)",
        "category": "อาหารและเครื่องดื่ม",
        "data": {
            "th": {"word": "กาแฟ", "pron": "กา-แฟ"},
            "en": {"word": "Coffee", "pron": "คอฟ-ฟี่"},
            "jp": {"word": "コーヒー", "pron": "โค-ฮี"},
            "cn": {"word": "咖啡", "pron": "คา-เฟย"},
            "sign_tsl": {"word": "🤟 ภาษามือไทย (TSL)", "instruction": "ทำมือกำหลวมๆ แล้วหมุนวนบริเวณข้างแก้มหรือหน้าอก (สัญลักษณ์การบดกาแฟ)"},
            "sign_asl": {"word": "🤟 ภาษามืออเมริกัน (ASL)", "instruction": "หมุนกำปั้นขวาบนกำปั้นซ้าย (Coffee Grinding Sign)"}
        }
    },
    "Q8686": {
        "concept": "การทักทาย (Greeting / 👋)",
        "category": "หมวดการสื่อสาร",
        "data": {
            "th": {"word": "สวัสดี", "pron": "สะ-วัด-ดี"},
            "en": {"word": "Hello", "pron": "เฮ็ล-โล"},
            "jp": {"word": "こんにちは", "pron": "คอน-นิ-จิวะ"},
            "cn": {"word": "你好", "pron": "หนี-ห่าว"},
            "sign_tsl": {"word": "🤟 ภาษามือไทย (TSL)", "instruction": "พนมมือไหว้ระดับอก พร้อมพยักหน้าเล็กน้อย"},
            "sign_asl": {"word": "🤟 ภาษามืออเมริกัน (ASL)", "instruction": "ยกมือขึ้นแตะหน้าผากแล้วโบกออกด้านข้าง (Salute Waving Sign)"}
        }
    },
    "Q539": {
        "concept": "การไป / การเดินทาง (Go / 🚶)",
        "category": "หมวดการกระทำ (Action)",
        "data": {
            "th": {"word": "ไป", "pron": "ไป"},
            "en": {"word": "Go", "pron": "โก"},
            "jp": {"word": "行く", "pron": "อิ-คุ"},
            "cn": {"word": "去", "pron": "ชวี่"},
            "sign_tsl": {"word": "🤟 ภาษามือไทย (TSL)", "instruction": "ชูนิ้วชี้ทั้งสองข้าง แล้วชี้พุ่งชี้ไปข้างหน้าพร้อมกัน"},
            "sign_asl": {"word": "🤟 ภาษามืออเมริกัน (ASL)", "instruction": "ชูนิ้วชี้สองข้างหมุนไปทิศทางที่จะไป (Point Forward)"}
        }
    },
    "Q102": {
        "concept": "ขอบคุณ (Thank you / 🙏)",
        "category": "หมวดมารยาท",
        "data": {
            "th": {"word": "ขอบคุณ", "pron": "ขอบ-คุณ"},
            "en": {"word": "Thank you", "pron": "แธงค์-ยู"},
            "jp": {"word": "ありがとう", "pron": "อะ-ริ-กา-โตะ"},
            "cn": {"word": "谢谢", "pron": "เซี่ย-เซี่ย"},
            "sign_tsl": {"word": "🤟 ภาษามือไทย (TSL)", "instruction": "แบมือแตะที่คางแล้วยื่นออกไปหาฝ่ายตรงข้าม"},
            "sign_asl": {"word": "🤟 ภาษามืออเมริกัน (ASL)", "instruction": "ใช้นิ้วมือแตะริมฝีปากล่างแล้วยื่นมือออกไปหาผู้รับ"}
        }
    }
}

LANGUAGES = {
    "th": "🇹🇭 ภาษาไทย (Thai)",
    "en": "🇺🇸 ภาษาอังกฤษ (English)",
    "jp": "🇯🇵 ภาษาญี่ปุ่น (Japanese)",
    "cn": "🇨🇳 ภาษาจีน (Chinese)",
    "sign_tsl": "🤟 ภาษามือไทย (Thai Sign Language)",
    "sign_asl": "🤟 ภาษามืออเมริกัน (ASL)"
}

# ---------------------------------------------------------
# 2. ฟังก์ชันแปลข้อมูลด้วย Universal ID
# ---------------------------------------------------------
def search_qid_by_input(text, src_lang):
    text_clean = text.strip().lower()
    for qid, item in UNIVERSAL_DATABASE.items():
        lang_data = item["data"].get(src_lang, {})
        word = lang_data.get("word", "").lower()
        if text_clean == word:
            return qid, item
    return None, None

# ---------------------------------------------------------
# 3. หน้าตาแอป Streamlit
# ---------------------------------------------------------
st.set_page_config(page_title="Universal Meaning Protocol", page_icon="🌐", layout="wide")

st.title("🌐 Universal Language & Sign Language Protocol")
st.caption("ระบบรหัสสื่อสารสากล: เชื่อมโยง **ภาษาพูด + ตัวอักษร + ภาษามือ** ด้วยรหัสความหมายเดียวกัน (QID)")

st.divider()

col1, col2 = st.columns(2)
with col1:
    src_lang = st.selectbox("1. ช่องทางส่งข้อมูล (Sender)", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=0)

with col2:
    tgt_lang = st.selectbox("2. ช่องทางรับข้อมูล (Receiver)", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x], index=4) # Default เป็นภาษามือไทย

user_text = st.text_input("พิมพ์คำพูด / ข้อความต้นทาง (ลองพิมพ์: สวัสดี / กาแฟ / ไป / ขอบคุณ):", value="สวัสดี" if src_lang=="th" else "Hello")

if st.button("🚀 ส่งรหัสความหมายข้ามระบบ", type="primary", use_container_width=True):
    qid, qdata = search_qid_by_input(user_text, src_lang)
    
    if qid:
        target_info = qdata["data"].get(tgt_lang, {})
        
        st.success(f"✅ แปลงเป็นรหัสความหมายสากลสำเร็จ!")
        
        # แสดงผลกระบวนการสื่อสาร 3 ขั้นตอน
        res_col1, res_col2, res_col3 = st.columns([1, 1.2, 1.5])
        
        with res_col1:
            st.info("📤 **1. ต้นทางส่งข้อมูล**")
            st.metric("คำที่ส่ง", user_text)
            st.write(f"หมวดหมู่: **{qdata['category']}**")
            
        with res_col2:
            st.warning("⚡ **2. รหัสกลางส่งข้ามระบบ**")
            st.metric("Universal QID", f"[{qid}]")
            st.caption(f"ความหมาย: {qdata['concept']}")
            
        with res_col3:
            st.success("📥 **3. ปลายทางรับข้อมูล**")
            target_word = target_info.get("word", "N/A")
            st.metric("ผลลัพธ์ปลายทาง", target_word)
            
            # ถ้าปลายทางเป็นภาษามือ ให้แสดงวิธีทำท่าทาง
            if "instruction" in target_info:
                st.markdown(f"**🖐️ วิธีทำท่าภาษามือ:** {target_info['instruction']}")
            else:
                st.markdown(f"🗣️ **คำอ่านออกเสียง:** {target_info.get('pron', '-')}")

    else:
        st.error("❌ ยังไม่มีคำนี้ในระบบต้นแบบ (ลองใช้คำว่า: สวัสดี, กาแฟ, ไป, ขอบคุณ)")

# ตารางแสดงคลังข้อมูลสากล
st.divider()
st.subheader("📊 คลังรหัสความหมายสากล (Universal Concept Registry)")

table_list = []
for qid, item in UNIVERSAL_DATABASE.items():
    table_list.append({
        "Universal ID": f"[{qid}]",
        "แนวคิดหลัก": item["concept"],
        "🇹🇭 ไทย": item["data"]["th"]["word"],
        "🇺🇸 อังกฤษ": item["data"]["en"]["word"],
        "🤟 ภาษามือไทย": item["data"]["sign_tsl"]["word"],
        "🤟 ภาษามือ ASL": item["data"]["sign_asl"]["word"]
    })

st.table(table_list)
