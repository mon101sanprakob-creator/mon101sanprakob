"""
############################################################
#
# SYNAPSE ENGINE
#
# helper.py
#
# Utility Functions
#
############################################################
"""

from datetime import datetime
import math


# ==========================================================
# DATE & TIME
# ==========================================================

def timestamp():
    """เวลาปัจจุบัน"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today():
    """วันที่ปัจจุบัน"""
    return datetime.now().strftime("%d/%m/%Y")


# ==========================================================
# NUMBER
# ==========================================================

def round6(value):
    """ปัดเศษ 6 ตำแหน่ง"""
    return round(value, 6)


def clamp(value, minimum, maximum):
    """จำกัดค่าให้อยู่ในช่วง"""
    return max(minimum, min(value, maximum))


def percentage(value, maximum):
    """แปลงเป็นเปอร์เซ็นต์"""
    if maximum == 0:
        return 0
    return (value / maximum) * 100


# ==========================================================
# DIGITAL ROOT
# ==========================================================

def digital_root(number):

    number = abs(int(number))

    while number >= 10:
        number = sum(int(i) for i in str(number))

    return number


# ==========================================================
# NORMALIZE
# ==========================================================

def normalize(value, min_value, max_value):

    if max_value == min_value:
        return 0

    return (value - min_value) / (max_value - min_value)


# ==========================================================
# MATH
# ==========================================================

def square(value):
    return value ** 2


def cube(value):
    return value ** 3


def root(value):
    return math.sqrt(value)


def average(values):

    if len(values) == 0:
        return 0

    return sum(values) / len(values)


# ==========================================================
# ENERGY
# ==========================================================

def energy_level(value):

    if value < 20:
        return "LOW"

    elif value < 40:
        return "NORMAL"

    elif value < 60:
        return "GOOD"

    elif value < 80:
        return "HIGH"

    return "MAXIMUM"


def energy_star(value):

    if value < 20:
        return "★"

    elif value < 40:
        return "★★"

    elif value < 60:
        return "★★★"

    elif value < 80:
        return "★★★★"

    return "★★★★★"


def energy_color(value):

    if value < 20:
        return "#ff3333"

    elif value < 40:
        return "#ffaa00"

    elif value < 60:
        return "#ffee00"

    elif value < 80:
        return "#00ff99"

    return "#00ccff"


# ==========================================================
# STRING
# ==========================================================

def line():

    return "-" * 60


def title(text):

    return f"\n{line()}\n{text}\n{line()}"


def banner():

    return f"""

====================================================

                 SYNAPSE

         Sound & Visual Therapy

          อยู่นิ้งๆไม่เจ็บตัว

====================================================

"""


# ==========================================================
# DEBUG
# ==========================================================

def debug(name, value):

    print(f"[DEBUG] {name} : {value}")
