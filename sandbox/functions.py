from datetime import time, datetime, timedelta

import math
import numpy as np

from sympy.utilities.iterables import multiset_permutations
import pickle

from sandbox.classes_and_constants import (
    Compound,
    Patient,
    Procedure,
    COMPOUNDS,
    PROC,
    STEP,
    DAY_START,
    DAY_START_MIN,
    TIMETABLE,
    Timestamp,
    Anytime,
    COMPOUND_TO_NAME,
    A_GE_0,
    lambda_GE,
    lambda_GA,
)


def min2time(m: int):
    return time(m // 60, m % 60)


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

    return np.any((s1 < e2) & (s2 < e1))


def place_priority(priority):
    if len(priority) == 0:
        return TIMETABLE, [], None

    timetable, schedule, milking = TIMETABLE, [], None
    s_me = 0
    for patient in priority:
        procedure = PROC[patient]
        s_ms = s_me + procedure.acc_time[0] // STEP
        s_me = s_ms + procedure.measure_time[0] // STEP
        if isinstance(procedure.delivery_times, Anytime):
            if milking is None:
                milking = (s_ms, add(s_ms, min2time(procedure.delivery_times.cooldown)))
        schedule.append(
            (min2time(DAY_START_MIN + s_ms * STEP), patient)
        )
        timetable[s_ms:s_me] = patient
        if len(procedure.acc_time) == 2:
            s_m2s = s_me + procedure.waiting_time // STEP
            s_m2e = s_m2s + procedure.measure_time[1] // STEP
            timetable[s_m2s:s_m2e] = patient
            schedule.append(
                (min2time(DAY_START_MIN + s_m2s * STEP), patient)
            )
            s_me = s_m2e
    return timetable, schedule, milking


def solve(timetable, schedule, order, milking, solutions):
    if len(order) == 0:
        solutions.append((schedule, milking))
        return

    proc_type = order[0]
    procedure = PROC[proc_type]

    proposals = ([], [])

    if proc_type == Timestamp.Methionin_1:
        acc_time_1 = procedure.acc_time[0]
        acc_time_2 = procedure.acc_time[1]
        measure_time_1 = procedure.measure_time[0]
        measure_time_2 = procedure.measure_time[1]

        for t_d in procedure.compound.delivery_times:
            wait = 0
            s_d = (time2min(t_d) - DAY_START_MIN) // STEP
            if s_d < 0:
                raise Exception

            while True:
                s_m1s = s_d + wait + acc_time_1 // STEP
                s_m1e = s_m1s + measure_time_1 // STEP
                s_m2s = s_m1e + procedure.waiting_time // STEP
                s_m2e = s_m2s + measure_time_2 // STEP
                if s_m1e > len(timetable) or s_m2e > len(timetable):
                    break

                colisions_1 = timetable[max(0, s_m1s - 1) : s_m1e] != Timestamp.Empty
                colisions_2 = timetable[s_m2s - 1 : s_m2e] != Timestamp.Empty
                if np.any(colisions_1) or np.any(colisions_2):
                    max_1 = np.max(np.where(colisions_1)) if np.any(colisions_1) else 0
                    max_2 = np.max(np.where(colisions_2)) if np.any(colisions_2) else 0
                    wait += max(max_1, max_2) + 1
                    continue

                proposals[0].append(((s_m1s, s_m1e), (s_m2s, s_m2e)))
                proposals[1].append(wait)
                break

        if len(proposals[1]) == 0:
            return

        for idx in np.where(proposals[1] == np.min(proposals[1]))[0].tolist():
            (s_m1s, s_m1e), (s_m2s, s_m2e) = proposals[0][idx]
            new_timetable = timetable.copy()
            new_timetable[s_m1s:s_m1e] = Timestamp.Methionin_1
            new_timetable[s_m2s:s_m2e] = Timestamp.Methionin_2
            new_schedule = schedule.copy()
            new_schedule.append(
                (min2time(DAY_START_MIN + s_m1s * STEP), Timestamp.Methionin_1)
            )
            new_schedule.append(
                (min2time(DAY_START_MIN + s_m2s * STEP), Timestamp.Methionin_2)
            )
            solve(new_timetable, new_schedule, order[1:], milking, solutions)

    elif len(procedure.measure_time) == 1:
        acc_time = procedure.acc_time[0]
        measure_time = procedure.measure_time[0]

        delivery_times = procedure.compound.delivery_times
        include_all = False
        if isinstance(delivery_times, Anytime):
            include_all = True
            delivery_times = milking if milking else [DAY_START]

        for t_d in delivery_times:
            wait = 0
            s_d = (time2min(t_d) - DAY_START_MIN) // STEP
            if s_d < 0:
                raise Exception

            while True:
                s_ms = s_d + wait + acc_time // STEP
                s_me = s_ms + measure_time // STEP
                if s_me > len(timetable):
                    break

                colisions = timetable[max(0, s_ms - 1) : s_me] != Timestamp.Empty
                if np.any(colisions):
                    wait += np.max(np.where(colisions)) + 1
                    continue

                proposals[0].append((s_ms, s_me))
                proposals[1].append(wait if not include_all else 0)
                break

        if len(proposals[1]) == 0:
            return

        for idx in np.where(proposals[1] == np.min(proposals[1]))[0].tolist():
            s_ms, s_me = proposals[0][idx]
            new_timetable = timetable.copy()
            new_timetable[s_ms:s_me] = proc_type
            t_ms = min2time(DAY_START_MIN + s_ms * STEP)
            new_schedule = schedule.copy()
            new_schedule.append((t_ms, proc_type))
            if include_all and milking is None:
                s_m1 = DAY_START_MIN + s_ms * STEP - acc_time
                s_m2 = s_m1 + procedure.compound.delivery_times.cooldown
                solve(
                    new_timetable,
                    new_schedule,
                    order[1:],
                    (min2time(s_m1), min2time(s_m2)),
                    solutions,
                )
            else:
                solve(new_timetable, new_schedule, order[1:], milking, solutions)


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
    ts_and_procedures: list[tuple[datetime.time, Timestamp]],
    patients: list[Patient],
    milking_times: tuple[datetime.time, datetime.time] | None,
) -> list[tuple[datetime.time, tuple[Procedure, Patient]]] | None:
    # get optimal schedule of patients from schedule of procedures
    result = []  # order patient per interval_type according to their activities
    schemes = list({ts_and_proc[1] for ts_and_proc in ts_and_procedures})

    if Timestamp.Methionin_2 in schemes:
        schemes.remove(Timestamp.Methionin_2)

    for scheme in schemes:  # iterate over unique procedures
        # get all patients with this procedure
        procedure = PROC[scheme]
        patients_proc = [
            patient for patient in patients if patient.procedure == procedure
        ]
        delivery_times = procedure.compound.delivery_times

        if isinstance(procedure.compound.delivery_times, Anytime):
            delivery_times = list(milking_times)

        acc_time = procedure.acc_time[0]

        def get_proc_start(t, mins):
            datetime_obj = datetime.combine(datetime.today(), t)
            new_datetime = datetime_obj - timedelta(minutes=mins)
            new_time = new_datetime.time()
            return new_time

        procedure_starts = [
            get_proc_start(ts_and_proc[0], acc_time)
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

        if isinstance(procedure.compound.delivery_times, Anytime):
            # return None if there is not enough activity left for SomaKit/PSMA patients from milking
            remaining_act = {}
            remaining_act[milking_times[0]] = A_GE_0 * math.exp(
                -lambda_GE * diff(milking_times[0], time(0, 0))
            )
            remaining_act[milking_times[1]] = A_GE_0 * math.exp(
                -lambda_GE * diff(milking_times[1], time(0, 0))
            )
            for pat_somakit, p_start in zip(patients_ordered, procedure_starts):
                milk_time = get_last_delivery_time(p_start, delivery_times)
                act_to_deduct = (
                    math.exp(lambda_GA * diff(p_start, milk_time))
                    * pat_somakit.desired_activity()
                )
                remaining_act[milk_time] = remaining_act[milk_time] - act_to_deduct
                if remaining_act[milk_time] < 0:
                    return None

        for proc_start, i in zip(procedure_starts, range(len(procedure_starts))):
            result.append((proc_start, (procedure, patients_ordered[i])))

    return result


def get_doses_to_order_and_cost_for_schedule(
    schedule: list[tuple[datetime.time, tuple[Procedure, Patient]]],
    milking_times: tuple[datetime.time, datetime.time] | None,
) -> (dict[Compound, dict[time, float]], float):
    compounds_to_be_ordered = [
        cmp
        for cmp in COMPOUNDS
        if not isinstance(COMPOUNDS[cmp].delivery_times, Anytime)
    ]
    # initialize doses_to_order
    doses_to_order = {
        comp_name: {t: 0 for t in COMPOUNDS[comp_name].delivery_times}
        for comp_name in compounds_to_be_ordered
    }

    for start_time, (procedure, patient) in schedule:
        if not isinstance(procedure.compound.delivery_times, Anytime):
            cmp = COMPOUND_TO_NAME.get(id(procedure.compound))  # radiopharm/compound
            a = patient.desired_activity()  # activity
            delivery_time = get_last_delivery_time(
                start_time, procedure.compound.delivery_times
            )
            ssd = diff(start_time, delivery_time) * 60  # seconds since delivery

            activity_to_add = (
                math.exp(math.log(2) / (procedure.compound.half_life * 60) * ssd) * a
            )
            doses_to_order[cmp][delivery_time] += activity_to_add

    cost = 0
    for cmp, cmp_dose_dict in doses_to_order.items():
        price = COMPOUNDS[cmp].cost
        cost += sum(cmp_dose_dict.values()) * price

    # extract only the first part of the tuple
    return doses_to_order, cost


def main():
    counts = [1, 2, 0, 1, 0, 1, 0]
    for cnt, sch in zip(counts, Timestamp.variants()):
        if sch == Timestamp.Empty or sch == Timestamp.Methionin_2:
            continue

    multiset = []
    for count, elem in zip(counts, Timestamp.variants()):
        if elem == Timestamp.Empty or elem == Timestamp.Methionin_2:
            continue
        multiset.extend([elem] * count)

    perms = list(multiset_permutations(multiset))
    solutions = []

    for i, perm in enumerate(perms):
        if i % 10 == 0:
            print(f"Perm {i}/{len(perms)}")
        perm_solutions = []
        solve(TIMETABLE, [], perm, None, perm_solutions)
        solutions += perm_solutions

    with open("timetables.pickle", "wb") as handle:
        pickle.dump(solutions, handle)

    # with open("timetables.pickle", "rb") as handle:
    #     solutions = pickle.load(handle)

    print(len(solutions))


def deduplicate(big_list: list[list[tuple]]) -> list[list[tuple]]:
    seen = set()
    result = []

    for small in big_list:
        key = frozenset(small[0])  # unordered & hashable
        if key not in seen:
            seen.add(key)
            result.append(small)

    return result


if __name__ == "__main__":
    main()
