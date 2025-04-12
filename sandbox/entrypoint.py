from sandbox.classes_and_constants import (
    Patient,
    Procedure,
    COMPOUNDS,
    Scheme,
    DAY_LEN,
    PROC,
)
from sandbox.functions import (
    get_patient_order_for_procedure_order,
    get_doses_to_order_and_cost_for_schedule,
    process,
)
from enum import Enum
from datetime import time, datetime

import math
import numpy as np

from sympy.utilities.iterables import multiset_permutations
import pickle

from sandbox.classes_and_constants import (
    Compound,
    Patient,
    Procedure,
    PROCEDURES,
    COMPOUNDS,
)

if __name__ == "__main__":
    pat1 = Patient(id="a", weight=80, procedure=PROC[Scheme.FDGB])
    pat2 = Patient(id="b", weight=75, procedure=PROC[Scheme.FDGB])
    pat3 = Patient(id="c", weight=90, procedure=PROC[Scheme.FDGO])
    patients = [pat1, pat2, pat3]

    counts = [1, 2, 0, 0, 0, 0, 0]
    meas_len = 0
    for cnt, sch in zip(counts, Scheme.variants()):
        if sch == Scheme.Break or sch == Scheme.Methionin_2:
            continue

        T_meas = PROC[sch].measure_time
        if len(T_meas) == 1:
            meas_len += cnt * (T_meas[0] // 5 + 1)
        elif len(T_meas) == 2:
            meas_len += cnt * ((T_meas[0] + T_meas[1]) // 5 + 2)
        else:
            raise Exception

    counts.append(DAY_LEN - meas_len)
    print(counts)
    multiset = []
    for count, elem in zip(counts, Scheme.variants()):
        multiset.extend([elem] * count)
    print(multiset)
    perms = multiset_permutations(multiset)

    procedure_permutations = [x for x in map(process, perms) if x is not None]

    cost_best = None
    patient_order_best = None
    doses_to_order_best = None

    for procedure_perm in procedure_permutations:
        patient_order = get_patient_order_for_procedure_order(procedure_perm, patients)
        if patient_order is not None:
            doses_to_order, cost = get_doses_to_order_and_cost_for_schedule(
                patient_order
            )

            if (cost_best is None) or (cost < cost_best):
                patient_order_best = patient_order
                doses_to_order_best = doses_to_order
                cost_best = cost

    print(f"SCHEDULE: {patient_order_best}")
    print(f"DOSE ORDERS: {doses_to_order_best}")
