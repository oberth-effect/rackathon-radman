from sandbox.classes_and_constants import (
    PROC,
    Timestamp,
    TIMETABLE,
)
from sandbox.functions import (
    get_patient_order_for_procedure_order,
    get_doses_to_order_and_cost_for_schedule,
    solve,
    deduplicate,
)

from sympy.utilities.iterables import multiset_permutations

from sandbox.classes_and_constants import (
    Patient,
)

if __name__ == "__main__":
    patients = [
        Patient(id="a", weight=80, procedure=PROC[Timestamp.FDGB]),
        Patient(id="b", weight=100, procedure=PROC[Timestamp.FDGB]),
        Patient(id="c", weight=90, procedure=PROC[Timestamp.FDGB]),
        Patient(id="g", weight=80, procedure=PROC[Timestamp.FDGO]),
        Patient(id="h", weight=75, procedure=PROC[Timestamp.FDGO]),
        Patient(id="i", weight=90, procedure=PROC[Timestamp.FDGO]),
    ]

    counts = [3, 3, 0, 0, 0, 0, 0]
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

    for i, perm in enumerate(perms):
        if i % 10 == 0:
            print(f"Perm {i}/{len(perms)}")
        perm_solutions = []
        solve(TIMETABLE, [], perm, perm_solutions)
        solutions += perm_solutions

    cost_best = None
    patient_order_best = None
    doses_to_order_best = None

    solutions_deduplicated = deduplicate(solutions)

    for procedure_perm in solutions_deduplicated:
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
    print(f"COST: {cost_best}")
