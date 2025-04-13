from sympy.utilities.iterables import multiset_permutations
import numpy as np
import math

from .models import Schedule, Order, MilkingTimes
from procedures.models import Procedure
from radiopharma.models import Compound, DeliveryTimes
from patients.models import Patient
from datetime import time, datetime, timedelta


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

def is_double_procedure(p: Procedure) -> bool:
    if p.measuring_time2 is not None:
        return True

EMPTY = -1
COMPANION = -100

STEP = 5
DAY_LEN_HRS = 8 * 60
DAY_LEN = DAY_LEN_HRS // STEP
DAY_START = time(6, 0)
DAY_START_MIN = DAY_START.hour * 60 + DAY_START.minute
TIMETABLE = np.array([EMPTY] * DAY_LEN)
A_GE_0 = 1.85 * 10**3
lambda_GE = 0.00256 / 24 / 60
lambda_GA = 0.0102
COOLDOWN = 6*60



def solve(timetable, schedule, order, milking, solutions, procedures_dict):
    if len(order) == 0:
        solutions.append((schedule, milking))
        return

    proc_id = order[0]
    procedure = procedures_dict[proc_id]

    proposals = ([], [])

    if is_double_procedure(procedure):
        acc_time_1 = procedure.accumulation_time
        acc_time_2 = procedure.accumulation_time2
        measure_time_1 = procedure.measuring_time
        measure_time_2 = procedure.measuring_time2
        delivery_times = [t.time for t in procedure.compound.deliverytimes_set.all()]

        for t_d in delivery_times:
            wait = 0
            s_d = (time2min(t_d) - DAY_START_MIN) // STEP
            if s_d < 0:
                raise Exception

            while True:
                s_m1s = s_d + wait + acc_time_1 // STEP
                s_m1e = s_m1s + measure_time_1 // STEP
                s_m2s = s_m1e + acc_time_2 // STEP
                s_m2e = s_m2s + measure_time_2 // STEP
                if s_m1e > len(timetable) or s_m2e > len(timetable):
                    break

                colisions_1 = timetable[max(0, s_m1s - 1): s_m1e] != EMPTY
                colisions_2 = timetable[s_m2s - 1: s_m2e] != EMPTY
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
            new_timetable[s_m1s:s_m1e] = proc_id
            new_timetable[s_m2s:s_m2e] = proc_id
            new_schedule = schedule.copy()
            new_schedule.append(
                (min2time(DAY_START_MIN + s_m1s * STEP), proc_id),
            )
            new_schedule.append(
                (min2time(DAY_START_MIN + s_m2s * STEP), COMPANION),
            )
            solve(new_timetable, new_schedule, order[1:], milking, solutions, procedures_dict)

    elif procedure.measuring_time2 is None:
        acc_time = procedure.accumulation_time
        measure_time = procedure.measuring_time

        delivery_times = [t.time for t in procedure.compound.deliverytimes_set.all()]
        include_all = False
        if procedure.compound.milkable:
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

                colisions = timetable[max(0, s_ms - 1): s_me] != EMPTY
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
            new_timetable[s_ms:s_me] = proc_id
            t_ms = min2time(DAY_START_MIN + s_ms * STEP)
            new_schedule = schedule.copy()
            new_schedule.append((t_ms, proc_id))
            if include_all and milking is None:
                s_m1 = DAY_START_MIN + s_ms * STEP - acc_time
                s_m2 = s_m1 + COOLDOWN
                solve(new_timetable, new_schedule, order[1:], (min2time(s_m1), min2time(s_m2)), solutions, procedures_dict)
            else:
                solve(new_timetable, new_schedule, order[1:], milking, solutions, procedures_dict)


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


def reorder_schedules_by_activity(
    schedules: list[Schedule], mins_since_last_del_list: list[int]
) -> list[Schedule]:
    schedules_sorted = sorted(
        schedules,
        key=lambda p: p.desired_activity(),
        reverse=True,
    )
    mins_indices_sorted_by_value = sorted(
        range(len(mins_since_last_del_list)), key=lambda i: mins_since_last_del_list[i]
    )
    result = [None] * len(mins_since_last_del_list)

    for idx, patient in zip(mins_indices_sorted_by_value, schedules_sorted):
        result[idx] = patient

    return result

def get_patient_order_for_procedure_order(
    ts_and_procedures: list[tuple[datetime.time, int]],
    schedules: list[Schedule],
    milking_times: tuple[datetime.time, datetime.time] | None,
    procedures: dict[int, Procedure],
) -> list[tuple[datetime.time, tuple[Procedure, Schedule]]] | None:
    # get optimal schedule of patients from schedule of procedures
    result = []  # order patient per interval_type according to their activities
    proc_id = list({ts_and_proc[1] for ts_and_proc in ts_and_procedures})

    if COMPANION in proc_id:
        proc_id.remove(COMPANION)

    for scheme in proc_id:  # iterate over unique procedures
        # get all patients with this procedure
        procedure = procedures[scheme]
        schedules_proc = [
            schedule for schedule in schedules if schedule.procedure.pk == scheme
        ]
        delivery_times = [t.time for t in procedure.compound.deliverytimes_set.all()]

        if procedure.compound.milkable:
            delivery_times = list(milking_times)

        acc_time = procedure.accumulation_time

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

        patients_ordered = reorder_schedules_by_activity(
            schedules_proc, mins_since_last_del
        )

        if procedure.compound.milkable:
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
                    * float(pat_somakit.desired_activity())
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
    compound_dict: dict[int, Compound] = None,
) -> (dict[Compound, dict[time, float]], float):
    compounds_to_be_ordered = [
        cmp
        for cmp in compound_dict
        if not compound_dict[cmp].milkable
    ]
    # initialize doses_to_order
    doses_to_order = {
        comp_name: {t: 0 for t in compound_dict[comp_name].delivery_times}
        for comp_name in compounds_to_be_ordered
    }

    for start_time, (procedure, patient) in schedule:
        if not procedure.compound.milkable:
            cmp = procedure.compound.pk # radiopharm/compound
            a = patient.desired_activity()  # activity
            delivery_time = get_last_delivery_time(
                start_time, procedure.compound.delivery_times
            )
            ssd = diff(start_time, delivery_time) * 60  # seconds since delivery

            activity_to_add = (
                math.exp(math.log(2) / (float(procedure.compound.half_life) * 60) * ssd) * float(a)
            )
            doses_to_order[cmp][delivery_time] += activity_to_add

    cost = 0
    for cmp, cmp_dose_dict in doses_to_order.items():
        price = compound_dict[cmp].cost
        cost += sum(cmp_dose_dict.values()) * float(price)

    # extract only the first part of the tuple
    return doses_to_order, cost


def calculate_schedule(schedules: list[Schedule]):
    procedure_ids = [s.procedure.pk for s in schedules]
    perms = multiset_permutations(procedure_ids)
    procedures = Procedure.objects.all()
    procedures_dict = {p.pk: p for p in procedures}

    compounds = Compound.objects.all()
    compound_dict = {c.pk: c for c in compounds}
    solutions = []

    for perm in perms:
        perm_solutions = []
        solve(TIMETABLE, [], perm, None, perm_solutions, procedures_dict)
        solutions += perm_solutions

    cost_best = None
    patient_order_best = None
    doses_to_order_best = None
    milking_times_theoretical = []

    for procedure_perm, milking_times in solutions:
        patient_order = get_patient_order_for_procedure_order(
            procedure_perm, schedules, milking_times, procedures_dict
        )
        if patient_order is not None:
            doses_to_order, cost = get_doses_to_order_and_cost_for_schedule(
                patient_order, milking_times, compound_dict
            )

            if (cost_best is None) or (cost < cost_best):
                patient_order_best = patient_order
                doses_to_order_best = doses_to_order
                cost_best = cost
                milking_times_theoretical = [] if not milking_times else list(milking_times)

    for t, (procedure, schedule) in patient_order_best:
        schedule.start_time = t
        schedule.calculated = True
        schedule.save()

    for cmp, (t_dict) in doses_to_order_best.items():
        comp = Compound.objects.get(pk=cmp)
        for t, dose in t_dict.items():
            slot = DeliveryTimes.objects.get(compound=comp, time=t)
            order = Order(
                compound=comp,
                activity=dose,
                time_slot=slot,
                qa_activity=0,
            )
            order.save()

    milking_patients_times = [
        t
        for t, val in patient_order_best
        if val[0].compound.milkable
    ]

    milking_times_best = list(
        set(milking_patients_times) & set(milking_times_theoretical)
    )

    for t in milking_times_best:
        miking_time = MilkingTimes(time=t)
        miking_time.save()