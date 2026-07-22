import streamlit as st
from moviepy.editor import ImageClip, AudioFileClip
import tempfile
import os

st.title("🎵 แอปสร้างวิดีโอประกอบเพลง (Free & No API)")
st.write("อัปโหลดรูปภาพและเพลงของคุณ เพื่อสร้างเป็นไฟล์วิดีโอ MP4")

# 1. ส่วนอัปโหลดไฟล์
uploaded_image = st.file_uploader("เลือกรูปภาพ (.jpg, .png)", type=["jpg", "jpeg", "png"])
uploaded_audio = st.file_uploader("เลือกไฟล์เพลง (.mp3, .wav)", type=["mp3", "wav"])

if uploaded_image and uploaded_audio:
    if st.button("🎬 สร้างวิดีโอเลย"):
        with st.spinner("กำลังประมวลผลวิดีโอ... กรุณารอสักครู่"):
            # สร้างไฟล์ชั่วคราวเพื่อบันทึกรูปและเพลง
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_file:
                img_file.write(uploaded_image.read())
                img_path = img_file.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                audio_file.write(uploaded_audio.read())
                audio_path = audio_file.name

            output_video_path = "output_video.mp4"

            try:
                # โหลดไฟล์เพลงเพื่อหาความยาว (วินาที)
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration

                # สร้างวิดีโอจากรูปภาพให้ยาวเท่ากับเพลง
                image_clip = ImageClip(img_path).set_duration(duration)
                video_clip = image_clip.set_audio(audio_clip)

                # บันทึกเป็นไฟล์วิดีโอ MP4
                video_clip.write_videofile(
                    output_video_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac"
                )

                # แสดงผลวิดีโอในหน้าเว็บ
                st.success("สร้างวิดีโอสำเร็จแล้ว!")
                st.video(output_video_path)

                # ปุ่มดาวน์โหลดวิดีโอ
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="⬇️ ดาวน์โหลดวิดีโอ MP4",
                        data=file,
                        import streamlit as st
from moviepy.editor import ImageClip, AudioFileClip
import tempfile
import os

st.title("🎵 แอปสร้างวิดีโอประกอบเพลง (Free & No API)")
st.write("อัปโหลดรูปภาพและเพลงของคุณ เพื่อสร้างเป็นไฟล์วิดีโอ MP4")

# 1. ส่วนอัปโหลดไฟล์
uploaded_image = st.file_uploader("เลือกรูปภาพ (.jpg, .png)", type=["jpg", "jpeg", "png"])
uploaded_audio = st.file_uploader("เลือกไฟล์เพลง (.mp3, .wav)", type=["mp3", "wav"])

if uploaded_image and uploaded_audio:
    if st.button("🎬 สร้างวิดีโอเลย"):
        with st.spinner("กำลังประมวลผลวิดีโอ... กรุณารอสักครู่"):
            # สร้างไฟล์ชั่วคราวเพื่อบันทึกรูปและเพลง
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_file:
                img_file.write(uploaded_image.read())
                img_path = img_file.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                audio_file.write(uploaded_audio.read())
                audio_path = audio_file.name

            output_video_path = "output_video.mp4"

            try:
                # โหลดไฟล์เพลงเพื่อหาความยาว (วินาที)
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration

                # สร้างวิดีโอจากรูปภาพให้ยาวเท่ากับเพลง
                image_clip = ImageClip(img_path).set_duration(duration)
                video_clip = image_clip.set_audio(audio_clip)

                # บันทึกเป็นไฟล์วิดีโอ MP4
                video_clip.write_videofile(
                    output_video_path, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac"
                )

                # แสดงผลวิดีโอในหน้าเว็บ
                st.success("สร้างวิดีโอสำเร็จแล้ว!")
                st.video(output_video_path)

                # ปุ่มดาวน์โหลดวิดีโอ
                with open(output_video_path, "rb") as file:
                    st.download_button(
                        label="⬇️ ดาวน์โหลดวิดีโอ MP4",
                        data=file,
                        file_name="my_music_video.mp4",
                        mime="video/mp4"
                    )

                # ลบไฟล์ชั่วคราวออก
                audio_clip.close()
                video_clip.close()
                os.remove(img_path)
                os.remove(audio_path)

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")="my_music_video.mp4",
                        mime="video/mp4"
                    )

                # ลบไฟล์ชั่วคราวออก
                audio_clip.close()
                video_clip.close()
                os.remove(img_path)
                os.remove(audio_path)

            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")
