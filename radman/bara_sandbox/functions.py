import math

from datetime import time, datetime


from radman.bara_sandbox.classes_and_constants import (
    Compound,
    Patient,
    Procedure,
    COMPOUNDS,
)


def diff(t1, t2):
    return (t1.hour * 60 + t1.minute) - (t2.hour * 60 + t2.minute)


def get_mins_since_last_delivery(
    proc_starts: list[time], delivery_times: list[time]
) -> list[int]:
    result = []
    for proc_start in proc_starts:
        delivery_times_before = [dt for dt in delivery_times if dt <= proc_start]
        result.append(
            diff(proc_start, max(delivery_times_before))
            if delivery_times_before
            else None
        )

    return result


def reorder_patients_by_activity(
    patients: list[Patient], mins_since_last_del_list: list[int]
) -> list[Patient]:
    patients_sorted = sorted(patients, key=lambda p: p.activity_absolute, reverse=True)
    mins_indices_sorted_by_value = sorted(
        range(len(mins_since_last_del_list)), key=lambda i: mins_since_last_del_list[i]
    )
    result = [None] * len(mins_since_last_del_list)

    for idx, patient in zip(mins_indices_sorted_by_value, patients_sorted):
        result[idx] = patient

    return result


def get_patient_order_for_procedure_order(
    ts_and_procedures: list[tuple[datetime.time, Procedure]],
    patients: list[Patient],
) -> dict[time, tuple[Procedure, Patient]] | None:
    # get optimal schedule of patients from schedule of procedures

    result = {}  # order patient per interval_type according to their activities
    procedures = [ts_and_proc[1] for ts_and_proc in ts_and_procedures]

    for procedure in list(set(procedures)):  # iterate over unique procedures
        # get all patients with this procedure
        patients_proc = [
            patient for patient in patients if patient.procedure == procedure
        ]
        delivery_times = procedure.compound.delivery_times
        procedure_starts = [
            ts_and_proc[0]
            for ts_and_proc in ts_and_procedures
            if ts_and_proc[1] == procedure
        ]

        mins_since_last_del = get_mins_since_last_delivery(
            procedure_starts, delivery_times
        )
        if None in mins_since_last_del:
            return None

        patients_ordered = reorder_patients_by_activity(
            patients_proc, mins_since_last_del
        )
        for proc_start, i in zip(procedure_starts, range(len(procedure_starts))):
            result[proc_start] = (procedure, patients_ordered[i])

    return result


def get_doses_to_order_and_profit_for_schedule(
    schedule,
) -> (dict[Compound, dict[time, float]], float):
    doses_to_order = {}

    # initialize doses_to_order
    for rp in COMPOUNDS:
        doses_to_order[rp] = {t: (0, []) for t in COMPOUNDS[rp]}

    for patient in schedule:
        rp = ...  # radiopharm/compound
        a = ...  # activity
        t = ...  # start of accumulation
        t_rp = ...  # closest rp delivery time
        msd = t - t_rp  # minutes since delivery

        doses_to_order[rp][t_rp][1].append(msd)
        doses_to_order[rp][t_rp][0] += (
            math.exp(rp.half_life * sum(doses_to_order[rp][t_rp][1])) * a
        )

    # extract only the first part of the tuple
    return {
        rp: {t: doses_to_order[rp][t][0] for t in doses_to_order[rp]}
        for rp in doses_to_order
    }
