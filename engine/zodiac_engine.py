"""
SYNAPSE ENGINE - Zodiac Engine
"""

from .constants import ZODIAC


class ZodiacEngine:
    _animals = list(ZODIAC.keys())

    def from_year(self, year_ce: int):
        """
        รับปี ค.ศ. แล้วคืนค่า (ชื่อปีนักษัตร, ดัชนี 1-12)
        ใช้ปี 2020 (ชวด) เป็นปีอ้างอิง
        """
        idx = (year_ce - 2020) % 12
        name = self._animals[idx]
        return name, ZODIAC[name]

    def from_buddhist_year(self, year_be: int):
        return self.from_year(year_be - 543)
