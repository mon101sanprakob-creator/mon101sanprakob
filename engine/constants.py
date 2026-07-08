"""
SYNAPSE ENGINE - Constants
"""

import math

# Mathematical constants
PHI = (1 + math.sqrt(5)) / 2
PHI_SQUARED = PHI ** 2
SQRT_PHI = math.sqrt(PHI)
PI = math.pi
E = math.e

# Astronomical constants
SYNODIC_MONTH = 29.530588  # วัน

# Frequency constants
BASE_FREQUENCY = 432.0
MAX_ENERGY = 100.0

# Weekdays
WEEKDAYS = {
    "อาทิตย์": 1,
    "จันทร์": 2,
    "อังคาร": 3,
    "พุธ": 4,
    "พฤหัสบดี": 5,
    "ศุกร์": 6,
    "เสาร์": 7,
}

# Months
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

# Zodiac years
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

# UI colors
COLORS = {
    "low": "#ff3333",
    "normal": "#ffaa00",
    "good": "#ffee00",
    "high": "#00ff99",
    "max": "#00ccff",
}
