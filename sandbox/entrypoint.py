from sandbox.classes_and_constants import (
    PROC,
    Timestamp,
    TIMETABLE,
    COMPOUND_TO_NAME,
    COMPOUND_PRICES,
    Anytime,
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
        Patient(id="Alice", weight=66, procedure=PROC[Timestamp.FDGO]),
        Patient(id="Bob", weight=70, procedure=PROC[Timestamp.FDGO]),
        Patient(id="Cecil", weight=78, procedure=PROC[Timestamp.FDGO]),
        Patient(id="Daniel", weight=70, procedure=PROC[Timestamp.FDGO]),
        Patient(id="Jarmila", weight=86, procedure=PROC[Timestamp.FDGO]),
        Patient(id="Petr", weight=59, procedure=PROC[Timestamp.FDGO]),
        Patient(id="Lucie", weight=60, procedure=PROC[Timestamp.FDGO]),
        Patient(id="Simona", weight=88, procedure=PROC[Timestamp.FDGO]),
    ]

    counts = [8, 0, 0, 0, 0, 0]
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
        solve(TIMETABLE, [], perm, None, perm_solutions)
        solutions += perm_solutions

    cost_best = None
    patient_order_best = None
    doses_to_order_best = None
    milking_times_theoretical = []

    solutions_deduplicated = deduplicate(solutions)

    for procedure_perm, milking_times in solutions_deduplicated:
        patient_order = get_patient_order_for_procedure_order(
            procedure_perm, patients, milking_times
        )
        if patient_order is not None:
            doses_to_order, cost = get_doses_to_order_and_cost_for_schedule(
                patient_order, milking_times
            )

            if (cost_best is None) or (cost < cost_best):
                patient_order_best = patient_order
                doses_to_order_best = doses_to_order
                cost_best = cost
                milking_times_theoretical = [] if not milking_times else list(milking_times)

    # get total profit
    profit = 0
    for patient in patients:
        comp = patient.procedure.compound
        comp_name = COMPOUND_TO_NAME[id(comp)]
        price = COMPOUND_PRICES[comp_name]
        act = patients[0].desired_activity()
        profit += price * act

    milking_patients_times = [
        t
        for t, val in patient_order_best
        if isinstance(val[0].compound.delivery_times, Anytime)
    ]
    milking_times_best = list(
        set(milking_patients_times) & set(milking_times_theoretical)
    )

    print(f"SCHEDULE: {patient_order_best}")
    print(f"DOSE ORDERS: {doses_to_order_best}")
    print(f"MILKING TIMES: {milking_times_best}")
    print(f"COST: {cost_best}")
    print(f"FINAL PROFIT: {profit - cost_best}")
