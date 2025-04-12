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
    DAY_START,
    PROC,
    STEP,
    DAY_LEN_HRS,
    DAY_START_MIN,
    TIMETABLE,
    Anytime,
    Timestamp,
    Anytime,
    COMPOUND_TO_NAME,
)


def min2time(min: int):
    return time(min // 60, min % 60)


def time2min(t: time):
    return t.hour * 60 + t.minute


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
        if sch != Timestamp.Empty:
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
                timetable.append((m1_s, Timestamp.Methionin_1))
                timetable.append((m2_s, Timestamp.Methionin_2))
            else:
                raise Exception
            t = add(t, min2time(measure_time[0]))
        t = add(t, min2time(STEP))
    return timetable


def effective_cost(compound, t):
    return compound.cost * math.exp(compound.half_life * t * 60)


def dist_to_closest(compound, t):
    if compound.delivery_times == Anytime:
        return 0
    t_min = time2min(t)
    delivery_times = [time2min(d) for d in compound.delivery_times]
    delivery_times = [t_min - d for d in delivery_times if d <= t_min]
    if len(delivery_times) == 0:
        return np.inf
    return min(delivery_times)


def solve(timetable, schedule, order, solutions):
    if len(order) == 0:
        solutions.append(schedule)
        return

    proc_type = order[0]
    procedure = PROC[proc_type]
    measure_slots = [t_m // STEP for t_m in procedure.measure_time]

    acc_time = procedure.acc_time[0]
    measure_time = procedure.measure_time[0]

    if procedure.compound.delivery_times == Anytime:
        pass

    for t_d in procedure.compound.delivery_times:
        wait = 0
        s_d = (time2min(t_d) - DAY_START_MIN) // STEP
        if s_d < 0:
            raise Exception

        proposals = ([], [])
        while True:
            s_ms = s_d + wait + acc_time // STEP
            s_me = s_ms + measure_time // STEP
            if np.any(timetable[max(0, s_ms - 1) : s_me + 1] != Timestamp.Empty):
                wait += 1
                continue
            proposals[0].append((s_ms, s_me))
            proposals[1].append(wait)
            break

        for idx in np.where(proposals[1] == np.min(proposals[1]))[0].tolist():
            new_timetable = timetable.copy()
            new_timetable[s_ms : s_me + 1] = proc_type
            new_schedule = schedule.copy()
            new_schedule.append((min2time(DAY_START_MIN + s_ms * STEP), proc_type))
            solve(new_timetable, new_schedule, order[1:], solutions)


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


def get_last_delivery_time(proc_start: time, delivery_times: list[time]) -> time:
    delivery_times_before = [dt for dt in delivery_times if dt <= proc_start]

    assert delivery_times_before, "No delivery time before start of procedure."

    return max(delivery_times_before)


def reorder_patients_by_activity(
    patients: list[Patient], mins_since_last_del_list: list[int]
) -> list[Patient]:
    patients_sorted = sorted(
        patients,
        key=lambda p: p.desired_activity(),
        reverse=True,
    )
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
    schemes = [ts_and_proc[1] for ts_and_proc in ts_and_procedures]

    for scheme in list(set(schemes)):  # iterate over unique procedures
        # get all patients with this procedure
        procedure = PROC[scheme]
        patients_proc = [
            patient for patient in patients if patient.procedure == procedure
        ]
        delivery_times = procedure.compound.delivery_times
        procedure_starts = [
            ts_and_proc[0]
            for ts_and_proc in ts_and_procedures
            if ts_and_proc[1] == scheme
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


def get_doses_to_order_and_cost_for_schedule(
    schedule,
) -> (dict[Compound, dict[time, float]], float):
    compounds_to_be_ordered = [
        cmp for cmp in COMPOUNDS if COMPOUNDS[cmp].delivery_times != Anytime
    ]
    # initialize doses_to_order
    doses_to_order = {
        comp_name: {t: (0, []) for t in COMPOUNDS[comp_name].delivery_times}
        for comp_name in compounds_to_be_ordered
    }

    for start_time, (procedure, patient) in schedule.items():
        cmp = COMPOUND_TO_NAME.get(id(procedure.compound))  # radiopharm/compound
        a = patient.desired_activity()  # activity
        delivery_time = get_last_delivery_time(
            start_time, procedure.compound.delivery_times
        )
        ssd = diff(start_time, delivery_time) * 60  # seconds since delivery

        activity_to_add = (
            math.exp(
                math.log(2)
                / (procedure.compound.half_life * 60)
                * sum(doses_to_order[cmp][delivery_time][1])
            )
            * a
        )
        doses_to_order[cmp][delivery_time] = (
            doses_to_order[cmp][delivery_time][0] + activity_to_add,
            doses_to_order[cmp][delivery_time][1] + [ssd],
        )

    cost = 0
    for cmp, cmp_dose_dict in doses_to_order.items():
        price = COMPOUNDS[cmp].cost
        cost += sum(value[0] for value in cmp_dose_dict.values()) * price

    # extract only the first part of the tuple
    return {
        rp: {t: doses_to_order[rp][t][0] for t in doses_to_order[rp]}
        for rp in doses_to_order
    }, cost


def main():
    counts = [3, 2, 1, 0, 0, 0, 0]
    for cnt, sch in zip(counts, Timestamp.variants()):
        if sch == Timestamp.Empty or sch == Timestamp.Methionin_2:
            continue

    # for cnt, sch in zip(counts, Timestamp.variants()):
    #     if sch == Timestamp.Empty or sch == Timestamp.Methionin_2:
    #         continue
    #
    #     T_meas = PROC[sch].measure_time
    #     if len(T_meas) == 1:
    #         meas_len += cnt * (T_meas[0] // 5 + 1)
    #     elif len(T_meas) == 2:
    #         meas_len += cnt * ((T_meas[0] + T_meas[1]) // 5 + 2)
    #     else:
    #         raise Exception
    # counts.append(DAY_LEN - meas_len)
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

    print(solutions)

    with open("timetables.pickle", "wb") as handle:
        pickle.dump(solutions, handle)


if __name__ == "__main__":
    main()
