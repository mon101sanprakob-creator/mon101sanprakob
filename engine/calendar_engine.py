"""
###############################################################
#
# SYNAPSE ENERGY ENGINE
#
# VERSION 1.0
#
###############################################################
"""

from .math_engine import MathEngine


class EnergyEngine:

    def __init__(self):

        self.math = MathEngine()

    # =======================================

    def calculate(
        self,
        weekday,
        month,
        zodiac,
        lunar
    ):

        result = self.math.synapse_formula(

            weekday,
            month,
            zodiac,
            lunar

        )

        total = result["total"]

        energy = result["energy"]

        root = result["root"]

        frequency = result["frequency"]

        level = self.energy_level(energy)

        color = self.energy_color(energy)

        state = self.energy_state(energy)

        result["level"] = level

        result["color"] = color

        result["state"] = state

        return result

    # =======================================

    def energy_level(self, energy):

        if energy < 20:
            return 1

        elif energy < 40:
            return 2

        elif energy < 60:
            return 3

        elif energy < 80:
            return 4

        return 5

    # =======================================

    def energy_color(self, energy):

        if energy < 20:
            return "#aa0000"

        elif energy < 40:
            return "#ff8800"

        elif energy < 60:
            return "#ffee00"

        elif energy < 80:
            return "#00ff88"

        return "#00ccff"

    # =======================================

    def energy_state(self, energy):

        if energy < 20:

            return "LOW"

        elif energy < 40:

            return "NORMAL"

        elif energy < 60:

            return "GOOD"

        elif energy < 80:

            return "HIGH"

        return "MAXIMUM"

    # =======================================

    def summary(self, result):

        return {

            "Synapse Value": round(result["total"],6),

            "Energy": round(result["energy"],2),

            "Frequency": round(result["frequency"],2),

            "Digital Root": result["root"],

            "Level": result["level"],

            "Color": result["color"],

            "State": result["state"]

      }
