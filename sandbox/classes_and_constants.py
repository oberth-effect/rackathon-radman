from dataclasses import dataclass, field
from datetime import time
from enum import Enum


class Anytime:
    pass


@dataclass
class Compound:
    half_life: float
    cost: float
    delivery_times: list[time] | Anytime


@dataclass
class Procedure:
    compound: Compound
    acc_time: list[int]
    measure_time: list[int]
    required_specific_dose: float | None = None
    required_fixed_dose: float | None = None
    waiting_time: int | None = None

    def required_activity(self, mass: float):
        if self.required_fixed_dose is not None:
            return self.required_fixed_dose
        if self.required_specific_dose is not None:
            return self.required_specific_dose * mass
        raise ValueError("No required dose defined")


COMPOUNDS = {
    "18F-FDG": Compound(
        110, 8900, delivery_times=[time(6, 30), time(10, 30), time(13, 0)]
    ),
    "11C-MET": Compound(20.4, 25000, delivery_times=[time(11, 0)]),
    "18F-Viza": Compound(110, 75000, delivery_times=[time(10, 0)]),
    "68Ga-SomaKit": Compound(68, 75000, delivery_times=Anytime),
    "68Ga-PSMA": Compound(68, 75000, delivery_times=Anytime),
}

COMPOUND_TO_NAME = {id(v): k for k, v in COMPOUNDS.items()}

PROCEDURES = {
    "18F-FDG (onko)": Procedure(COMPOUNDS["18F-FDG"], [60], [25], 2.5),
    "18F-FDG (neuro)": Procedure(COMPOUNDS["18F-FDG"], [0], [60], None, 150),
    "18F-viza": Procedure(COMPOUNDS["18F-Viza"], [90], [20], None, 185),
    "68Ga-SomaKit": Procedure(COMPOUNDS["68Ga-SomaKit"], [60], [30], 1.85),
    "68Ga-PSMA": Procedure(COMPOUNDS["68Ga-PSMA"], [60], [30], 2),
    "11C-MET": Procedure(COMPOUNDS["11C-MET"], [0, 0], [20, 20], 4.5, waiting_time=90),
}


class Scheme(Enum):
    FDGO = 0
    FDGB = 1
    Vizamyl = 2
    SomaKit = 3
    PSMA = 4
    Methionin_1 = 5
    Methionin_2 = 6
    Break = 7

    @classmethod
    def variants(cls):
        return tuple(cls)


PROC = {
    Scheme.FDGO: PROCEDURES["18F-FDG (onko)"],
    Scheme.FDGB: PROCEDURES["18F-FDG (neuro)"],
    Scheme.Vizamyl: PROCEDURES["18F-viza"],
    Scheme.SomaKit: PROCEDURES["68Ga-SomaKit"],
    Scheme.PSMA: PROCEDURES["68Ga-PSMA"],
    Scheme.Methionin_1: PROCEDURES["11C-MET"],
}

DAY_LEN_HRS = 8 * 60
DAY_START = time(6, 0)
STEP = 5
DAY_LEN = DAY_LEN_HRS // STEP


@dataclass
class Patient:
    id: str
    procedure: Procedure
    weight: float

    @property
    def baseline_cost(self):
        return (
            self.procedure.required_activity(self.weight) * self.procedure.compound.cost
        )

    def desired_activity(self):
        return (
            self.procedure.required_fixed_dose
            or self.weight * self.procedure.required_specific_dose
        )
