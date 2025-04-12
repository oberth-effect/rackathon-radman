from radman.bara_sandbox.classes_and_constants import Patient, Procedure, COMPOUNDS
from radman.bara_sandbox.functions import (
    get_patient_order_for_procedure_order,
    get_doses_to_order_and_profit_for_schedule,
)

if __name__ == "__main__":
    procedure1 = Procedure(
        compound=COMPOUNDS["18F-FDG"],
        acc_time=[60],
        measure_time=[25],
        required_specific_dose=2.5,
    )
    procedure2 = Procedure(
        compound=COMPOUNDS["18F-FDG"],
        acc_time=[0],
        measure_time=[60],
        required_fixed_dose=125,
    )
    procedure3 = Procedure(
        compound=COMPOUNDS["18F-FDG"],
        acc_time=[90],
        measure_time=[20],
        required_fixed_dose=185,
    )

    procedures = [procedure1, procedure2, procedure3]

    pat1 = Patient(id="a", weight=80, procedure=procedure1)
    pat2 = Patient(id="b", weight=75, procedure=procedure1)
    pat3 = Patient(id="c", weight=90, procedure=procedure2)
    pat4 = Patient(id="d", weight=85, procedure=procedure2)
    pat5 = Patient(id="e", weight=64, procedure=procedure3)
    patients = [pat1, pat2, pat3, pat4, pat5]

    procedure_permutations = ...  # tbd by Tomas

    profit_best = 0
    patient_order_best = None
    doses_to_order_best = None

    for procedure_perm in procedure_permutations:
        patient_order = get_patient_order_for_procedure_order(procedure_perm, patients)
        doses_to_order, profit = get_doses_to_order_and_profit_for_schedule(
            patient_order
        )
        if profit > profit_best:
            patient_order_best = patient_order
            doses_to_order_best = doses_to_order
