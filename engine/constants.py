"""
############################################################
#
# SYNAPSE ENGINE
#
# constants.py
#
# System Constants (Math, Astronomy, UI & System Colors)
# For Educational & Entertainment Purposes
#
############################################################
"""

import math

# ==========================================================
# MATHEMATICAL & SACRED GEOMETRY CONSTANTS
# ==========================================================
# ค่าคงที่ทางคณิตศาสตร์และสัดส่วนธรรมชาติ
GOLDEN_RATIO = 1.618033988749895  # φ (Phi)
PHI = (1 + math.sqrt(5)) / 2
PHI_SQUARED = PHI ** 2
SQRT_PHI = math.sqrt(PHI)
PI = 3.141592653589793           # π
E = math.e

# ลำดับฟีโบนัชชีสำหรับใช้ในสัดส่วน UI หรือการคำนวณความถี่ (Hz)
FIBONACCI_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]


# ==========================================================
# ASTRONOMICAL & CALENDAR CONSTANTS
# ==========================================================
# รอบโคจรของดวงจันทร์ (วัน) - สำหรับคำนวณดิถีดวงจันทร์เชิงดาราศาสตร์
SYNODIC_MONTH = 29.530588
MOON_CYCLE_DAYS = 29.53059

# คาบการโคจรของดาวเคราะห์โดยประมาณ (ปีโลก)
PLANET_ORBITS = {
    "Mercury": 0.2408,
    "Venus": 0.6152,
    "Earth": 1.0,
    "Mars": 1.8808,
    "Jupiter": 11.8626,
    "Saturn": 29.4475,
    "Uranus": 84.0168,
    "Neptune": 164.7913
}

# รายชื่อวันในสัปดาห์ (สำหรับ UI และการแมปปิ้งภาษาไทย)
WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]

WEEKDAYS_TH = {
    "อาทิตย์": 1,
    "จันทร์": 2,
    "อังคาร": 3,
    "พุธ": 4,
    "พฤหัสบดี": 5,
    "ศุกร์": 6,
    "เสาร์": 7,
}

# เดือน
MONTHS = {
    "มกราคม": 1,
    "กุมภาพันธ์": 2,
    "มีนาคม": 3,
    "เมษายน": 4,
    "พฤษภาคม": 5,
    "มิถุนายน": 6,
    "กรกฎาคม": 7,
    "สิงหาคม": 8,
    "กันยายน": 9,
    "ตุลาคม": 10,
    "พฤศจิกายน": 11,
    "ธันวาคม": 12,
}

# ปีนักษัตร
ZODIAC = {
    "ชวด": 1,
    "ฉลู": 2,
    "ขาล": 3,
    "เถาะ": 4,
    "มะโรง": 5,
    "มะเส็ง": 6,
    "มะเมีย": 7,
    "มะแม": 8,
    "วอก": 9,
    "ระกา": 10,
    "จอ": 11,
    "กุน": 12,
}

# กลุ่มกลุ่มดาวจักรราศี (ตามช่วงวันที่สากล)
ZODIAC_SIGNS = [
    {"name": "Capricorn", "start": (12, 22), "end": (1, 19), "element": "Earth"},
    {"name": "Aquarius", "start": (1, 20), "end": (2, 18), "element": "Air"},
    {"name": "Pisces", "start": (2, 19), "end": (3, 20), "element": "Water"},
    {"name": "Aries", "start": (3, 21), "end": (4, 19), "element": "Fire"},
    {"name": "Taurus", "start": (4, 20), "end": (5, 20), "element": "Earth"},
    {"name": "Gemini", "start": (5, 21), "end": (6, 20), "element": "Air"},
    {"name": "Cancer", "start": (6, 21), "end": (7, 22), "element": "Water"},
    {"name": "Leo", "start": (7, 23), "end": (8, 22), "element": "Fire"},
    {"name": "Virgo", "start": (8, 23), "end": (9, 22), "element": "Earth"},
    {"name": "Libra", "start": (9, 23), "end": (10, 22), "element": "Air"},
    {"name": "Scorpio", "start": (10, 23), "end": (11, 21), "element": "Water"},
    {"name": "Sagittarius", "start": (11, 22), "end": (12, 21), "element": "Fire"}
]


# ==========================================================
# SOUND & FREQUENCY CONSTANTS (Hz)
# ==========================================================
BASE_FREQUENCY = 432.0
MAX_ENERGY = 100.0

# คลื่นเสียงอ้างอิงเพื่อความผ่อนคลาย (Solfeggio Frequencies ที่นิยมใช้ในสปา/แอปสมาธิ)
THERAPY_FREQUENCIES = {
    "UT": 396.0,  # Liberation / Liberating Guilt and Fear
    "RE": 417.0,  # Facilitating Change / Undoing Situations
    "MI": 528.0,  # Transformation and Miracles / DNA Repair (Reference)
    "FA": 639.0,  # Connecting / Relationships
    "SOL": 741.0, # Awakening Intuition / Expressions
    "LA": 852.0   # Returning to Spiritual Order
}


# ==========================================================
# SYSTEM THEME & VISUAL COLORS
# ==========================================================
# โค้ดสีนีออนและธีมของแอปพลิเคชัน SYNAPSE (Hex Codes)
COLOR_PALETTE = {
    "PRIMARY": "#00ccff",      # Cyan Neon
    "SECONDARY": "#00ff99",    # Green Neon
    "ACCENT": "#ffee00",       # Yellow Neon
    "WARNING": "#ffaa00",      # Orange Neon
    "DANGER": "#ff3333",       # Red Neon
    "BACKGROUND": "#0e1117",   # Dark Mode Base
    "SURFACE": "#1a1c23",      # Component Background
    "TEXT_LIGHT": "#ffffff",   # Main Text
    "TEXT_DARK": "#888888"     # Muted Text
}

COLORS = {
    "low": "#ff3333",
    "normal": "#ffaa00",
    "good": "#ffee00",
    "high": "#00ff99",
    "max": "#00ccff",
}


# ==========================================================
# UI & ANIMATION CONFIGURATION
# ==========================================================
# ค่ากำหนดสำหรับการเรนเดอร์ UI บนหน้าจอ
UI_CONFIG = {
    "APP_TITLE": "SYNAPSE - Sound & Visual Therapy",
    "VERSION": "1.0.0",
    "DEFAULT_VOLUME": 50,
    "MAX_VOLUME": 100,
    "ANIMATION_SPEED_MS": 300,
    "REFRESH_RATE_HZ": 60
}

# ข้อความกำกับความปลอดภัยตามข้อตกลงความเป็นส่วนตัวและการใช้งาน
ENTERTAINMENT_DISCLAIMER = (
    "⚠️ หมายเหตุ: แอปพลิเคชันนี้และผลลัพธ์การคำนวณ จัดทำขึ้นเพื่อความบันเทิง "
    "การศึกษาเชิงวัฒนธรรม และการสำรวจข้อมูลคณิตศาสตร์/ดาราศาสตร์เท่านั้น "
    "ไม่ใช่คำแนะนำทางการแพทย์ การรักษาโรค การเงิน หรือข้อเท็จจริงทางวิทยาศาสตร์ "
    "โปรดใช้วิจารณญาณในการใช้งาน"
)
