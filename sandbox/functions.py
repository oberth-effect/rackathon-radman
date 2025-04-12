from datetime import time, datetime

import math
import numpy as np

from sympy.utilities.iterables import multiset_permutations
import pickle

from sandbox.classes_and_constants import (
    Compound,
    Patient,
    Procedure,
    COMPOUNDS,
    DAY_START,
    Scheme,
    PROC,
    STEP,
    DAY_LEN,
)


def min2time(min: int):
    return time(min // 60, min % 60)


def add(t1, t2):
    m1 = t1.hour * 60 + t1.minute
    m2 = t2.hour * 60 + t2.minute
    return min2time(m1 + m2)


def diff(t1, t2):
    return (t1.hour * 60 + t1.minute) - (t2.hour * 60 + t2.minute)


def any_overlap(blocks_to_add, blocked_blocks):
    blocks_to_add = np.array(blocks_to_add)
    blocked_blocks = np.array(blocked_blocks)

    s1 = blocks_to_add[:, 0][:, np.newaxis]
    e1 = blocks_to_add[:, 1][:, np.newaxis]
    s2 = blocked_blocks[:, 0][np.newaxis, :]
    e2 = blocked_blocks[:, 1][np.newaxis, :]

    overlaps = (s1 < e2) & (s2 < e1)

    return np.any(overlaps)


def process(permutation):
    t = DAY_START
    timetable = []
    blocked_times = []
    for sch in permutation:
        if sch != Scheme.Break:
            measure_time = PROC[sch].measure_time
            if len(measure_time) == 1:
                proposed = [[t, add(t, min2time(measure_time[0]))]]
                if len(blocked_times) != 0 and any_overlap(proposed, blocked_times):
                    return None
                timetable.append((t, sch))
            elif len(measure_time) == 2:
                m1_s, m2_s = t, add(t, min2time(PROC[sch].waiting_time))
                m1_e, m2_e = (
                    add(m1_s, min2time(measure_time[0])),
                    add(m2_s, min2time(measure_time[1])),
                )
                proposed = [[m1_s, m1_e], [m2_s, m2_e]]
                if len(blocked_times) != 0 and any_overlap(proposed, blocked_times):
                    return None
                blocked_times.append((m2_s, m2_e))
                timetable.append((m1_s, Scheme.Methionin_1))
                timetable.append((m2_s, Scheme.Methionin_2))
            else:
                raise Exception
            t = add(t, min2time(measure_time[0]))
        t = add(t, min2time(STEP))
    return timetable


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


def main():
    counts = [1, 1, 0, 0, 0, 0, 0]
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

    timetables = [x for x in map(process, perms) if x is not None]

    with open("timetables.pickle", "wb") as handle:
        pickle.dump(timetables, handle)
