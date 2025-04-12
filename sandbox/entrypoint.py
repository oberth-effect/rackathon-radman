from sandbox.classes_and_constants import (
    PROC,
    Timestamp,
    TIMETABLE,
)
from sandbox.functions import (
    get_patient_order_for_procedure_order,
    get_doses_to_order_and_cost_for_schedule,
    solve,
)

from sympy.utilities.iterables import multiset_permutations

from sandbox.classes_and_constants import (
    Patient,
)

if __name__ == "__main__":
    pat1 = Patient(id="a", weight=80, procedure=PROC[Timestamp.FDGB])
    pat2 = Patient(id="b", weight=75, procedure=PROC[Timestamp.FDGB])
    pat3 = Patient(id="c", weight=90, procedure=PROC[Timestamp.FDGB])
    pat1 = Patient(id="d", weight=80, procedure=PROC[Timestamp.FDGB])
    pat2 = Patient(id="e", weight=75, procedure=PROC[Timestamp.FDGB])
    pat3 = Patient(id="f", weight=90, procedure=PROC[Timestamp.FDGB])
    pat1 = Patient(id="g", weight=80, procedure=PROC[Timestamp.FDGO])
    pat2 = Patient(id="h", weight=75, procedure=PROC[Timestamp.FDGO])
    pat3 = Patient(id="i", weight=90, procedure=PROC[Timestamp.FDGO])
    pat1 = Patient(id="j", weight=80, procedure=PROC[Timestamp.FDGO])
    pat2 = Patient(id="k", weight=75, procedure=PROC[Timestamp.FDGO])
    pat3 = Patient(id="l", weight=90, procedure=PROC[Timestamp.FDGO])
    patients = [pat1, pat2, pat3]

    counts = [6, 6, 0, 0, 0, 0, 0]
    for cnt, sch in zip(counts, Timestamp.variants()):
        if sch == Timestamp.Empty or sch == Timestamp.Methionin_2:
            continue

    print(counts)

    multiset = []
    for count, elem in zip(counts, Timestamp.variants()):
        if elem == Timestamp.Empty or elem == Timestamp.Methionin_2:
            continue
        multiset.extend([elem] * count)

    perms = list(multiset_permutations(multiset))
    print(len(perms), perms[0])
    solutions = []
    solve(TIMETABLE, [], perms[0], solutions)

    cost_best = None
    patient_order_best = None
    doses_to_order_best = None

    for procedure_perm in solutions:
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
