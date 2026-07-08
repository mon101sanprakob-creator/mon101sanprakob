"""
SYNAPSE ENGINE - Lunar Engine
จัดการข้างขึ้น ข้างแรม และอายุดวงจันทร์
"""

import math

try:
    from .constants import SYNODIC_MONTH as MOON_CYCLE, SQRT_PHI
except ImportError:
    # เผื่อชื่อค่าคงที่ใน constants.py ไม่ตรงกันทั้งหมด
    from .constants import MOON_CYCLE, SQRT_PHI


class LunarEngine:
    def __init__(self):
        self.moon_cycle = MOON_CYCLE
        self.sqrt_phi = SQRT_PHI

    def age(self, moon_side: str, lunar_day: int) -> float:
        """
        คืนค่าอายุดวงจันทร์แบบง่าย
        ขึ้น 1-15  -> 1-15
        แรม 1-15   -> 16-30
        """
        lunar_day = max(1, min(int(lunar_day), 15))

        if moon_side == "ขึ้น":
            return float(lunar_day)
        return float(lunar_day + 15)

    def phase_name(self, moon_side: str, lunar_day: int) -> str:
        age = self.age(moon_side, lunar_day)

        if age == 0:
            return "New Moon"
        elif age < 7.4:
            return "Waxing Crescent"
        elif age < 8.4:
            return "First Quarter"
        elif age < 14.8:
            return "Waxing Gibbous"
        elif age < 15.8:
            return "Full Moon"
        elif age < 22.1:
            return "Waning Gibbous"
        elif age < 23.1:
            return "Last Quarter"
        else:
            return "Waning Crescent"

    def illumination(self, moon_side: str, lunar_day: int) -> float:
        """
        ค่าแสงสว่างแบบประมาณการ 0-100
        """
        age = self.age(moon_side, lunar_day)
        x = (age / self.moon_cycle) * math.pi
        value = (1 - math.cos(x)) / 2
        return round(value * 100, 2)

    def lunar_weight(self, moon_side: str, lunar_day: int) -> float:
        """
        ค่าน้ำหนักสำหรับเอาไปใช้ในสูตร SYNAPSE
        """
        age = self.age(moon_side, lunar_day)
        return age * self.sqrt_phi

    def summary(self, moon_side: str, lunar_day: int) -> dict:
        age = self.age(moon_side, lunar_day)
        return {
            "side": moon_side,
            "day": int(lunar_day),
            "age": round(age, 2),
            "phase": self.phase_name(moon_side, lunar_day),
            "illumination": self.illumination(moon_side, lunar_day),
            "weight": round(self.lunar_weight(moon_side, lunar_day), 6),
  }
