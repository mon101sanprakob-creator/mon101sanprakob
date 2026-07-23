import streamlit as st
import datetime
import calendar

st.set_page_config(page_title="Date Pattern Matcher", page_icon="📅")

st.title("📅 แอปค้นหาวันที่มีค่าเดียวกัน (Past & Future 50 Years)")
st.write("กรอกวันเดือนปี แล้วแอปจะคำนวณหาว่ามีวันไหนบ้างที่ตรงกับคุณสมบัตินี้ ในช่วง 50 ปีย้อนหลัง และ 50 ปีข้างหน้า")

# 1. ส่วนรับอินพุตวันเดือนปี
col1, col2, col3 = st.columns(3)
with col1:
    day = st.number_input("วัน (Day)", min_value=1, max_value=31, value=datetime.date.today().day)
with col2:
    month = st.number_input("เดือน (Month)", min_value=1, max_value=12, value=datetime.date.today().month)
with col3:
    year = st.number_input("ปี ค.ศ. (Year)", min_value=1900, max_value=2100, value=datetime.date.today().year)

if st.button("🔍 คำนวณและแสดงผลลัพธ์"):
    try:
        # สร้างวัตถุวันที่จากอินพุต
        target_date = datetime.date(year, month, day)
        
        # คำนวณค่าต่างๆ ของวันที่ใส่เข้ามา
        day_name_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][target_date.weekday()]
        day_of_year = target_date.timetuple().tm_yday
        is_leap = calendar.isleap(year)
        
        st.success(f"📍 **วันที่คุณเลือก:** {target_date.strftime('%d/%m/%Y')} (ตรงกับ **วัน{day_name_th}**)")
        st.info(f"• เป็นวันที่ **{day_of_year}** ของปี | • ปีอธิกสุรทิน (29 ก.พ.): **{'ใช่' if is_leap else 'ไม่ใช่'}**")
        
        st.markdown("---")
        st.subheader("🎯 ผลการค้นหาวันที่มีค่าเดียวกันเป๊ะ (ย้อนหลัง 50 ปี - ล่วงหน้า 50 ปี)")
        
        start_year = year - 50
        end_year = year + 50
        
        matching_dates = []
        
        # ลูปคำนวณทีละปีตั้งแต่ -50 ถึง +50
        for y in range(start_year, end_year + 1):
            if y == year:
                continue # ข้ามปีปัจจุบันที่กรอก
            try:
                check_date = datetime.date(y, month, day)
                # เงื่อนไข: วันในสัปดาห์ตรงกัน (เช่น วันพฤหัสเหมือนกัน)
                if check_date.weekday() == target_date.weekday():
                    diff_years = y - year
                    time_status = f"ล่วงหน้า {diff_years} ปี" if diff_years > 0 else f"ย้อนหลัง {abs(diff_years)} ปี"
                    matching_dates.append({
                        "ปี ค.ศ.": y,
                        "ปี พ.ศ.": y + 543,
                        "วันที่": check_date.strftime("%d/%m/%Y"),
                        "ระยะเวลา": time_status
                    })
            except ValueError:
                # กรณีใส่วันที่ 29 ก.พ. แล้วปีนั้นไม่มี 29 ก.พ.
                continue
                
        # แสดงผลลัพธ์
        st.write(f"พบวันที่มีค่าเดียวกันรวมทั้งหมด **{len(matching_dates)} วัน** ในรอบ 100 ปี:")
        st.dataframe(matching_dates, use_container_width=True)
        
    except ValueError:
        st.error("❌ วันที่ที่คุณกรอกไม่ถูกต้อง (เช่น ไม่มีวันที่ 31 ในเดือนนั้น หรือไม่ใช่ปีที่มี 29 ก.พ.)")
