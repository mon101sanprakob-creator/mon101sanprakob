import math

PHI = 1.61803398875
MOON_CYCLE = 29.530588

DAY = {
    "อาทิตย์":1,
    "จันทร์":2,
    "อังคาร":3,
    "พุธ":4,
    "พฤหัส":5,
    "ศุกร์":6,
    "เสาร์":7
}

MONTH = {
    "มกราคม":1,
    "กุมภาพันธ์":2,
    "มีนาคม":3,
    "เมษายน":4,
    "พฤษภาคม":5,
    "มิถุนายน":6,
    "กรกฎาคม":7,
    "สิงหาคม":8,
    "กันยายน":9,
    "ตุลาคม":10,
    "พฤศจิกายน":11,
    "ธันวาคม":12
}

ZODIAC = {
    "ชวด":1,
    "ฉลู":2,
    "ขาล":3,
    "เถาะ":4,
    "มะโรง":5,
    "มะเส็ง":6,
    "มะเมีย":7,
    "มะแม":8,
    "วอก":9,
    "ระกา":10,
    "จอ":11,
    "กุน":12
}


def lunar_value(side, day):

    if side == "ขึ้น":
        return day

    return day + 15


def digital_root(value):

    value = str(abs(int(value)))

    while len(value) > 1:
        total = sum(int(x) for x in value)
        value = str(total)

    return int(value)


def calculate(day_name,
              month_name,
              zodiac_name,
              moon_side,
              moon_day):

    d = DAY[day_name]

    m = MONTH[month_name]

    z = ZODIAC[zodiac_name]

    l = lunar_value(moon_side, moon_day)

    day_part = d * PHI

    month_part = m * MOON_CYCLE

    zodiac_part = z * (PHI ** 2)

    lunar_part = l * math.sqrt(PHI)

    total = day_part + month_part + zodiac_part + lunar_part

    energy = total % 100

    root = digital_root(total)

    return {

        "day":day_part,

        "month":month_part,

        "zodiac":zodiac_part,

        "lunar":lunar_part,

        "total":round(total,6),

        "energy":round(energy,2),

        "root":root

}
