"""
SYNAPSE ENGINE - Main Orchestrator
"""

from .math_engine import MathEngine


class SynapseEngine:
    def __init__(self):
        self.math = MathEngine()

    def calculate(self, weekday, month, zodiac, lunar):
        return self.math.synapse_formula(
            weekday=weekday,
            month=month,
            zodiac=zodiac,
            lunar=lunar,
        )
