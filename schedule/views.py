from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView
from django.views import View
from django.http import HttpResponseRedirect

from radiopharma.models import Compound
from .forms import ScheduleForm
from .models import Schedule, Order, MilkingTimes  # Import the Schedule model
from .calculate import calculate_schedule
from procedures.models import Procedure

import json

def _cmpound_to_dict(compound: Compound):
    return {
        'half_life': float(compound.half_life),
        'cost': float(compound.cost),
        'delivery_times': [t.strftime("%H:%M") for t in compound.delivery_times],
    }

def _proc_to_dict(p: Procedure):
    return {
        'acc_time': [p.accumulation_time],
        'measure_time': [t for t in [p.measuring_time, p.measuring_time2] if t is not None],
        'required_specific_dose': float(p.required_specific_dose) if p.required_specific_dose else None,
        'required_fixed_dose': float(p.required_fixed_dose) if p.required_fixed_dose else None,
        'compound': _cmpound_to_dict(p.compound),
    }

def _schedule_to_dict(s: Schedule):
    return {
        'id': s.patient.id_number,
        'weight': float(s.patient.weight),
        'procedure': _proc_to_dict(s.procedure),
    }
class ScheduleListView(ListView):
    model = Schedule
    template_name = 'schedule/schedule_list.html'  # Specify the template
    context_object_name = 'schedules'
    ordering = ['start_time']  # Order by start_time

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_calculated = not Schedule.objects.filter(calculated=False).exists()
        is_empty = not Schedule.objects.exists()
        doses_to_order = {}
        patient_order = {}
        if all_calculated and not is_empty:
            orders = Order.objects.all()
            doses_raw = {o.compound.name: {} for o in orders}
            for o in orders:
                doses_raw[o.compound.name].update({o.time_slot.time.strftime("%H:%M"): float(o.activity)})

            doses_to_order = doses_raw
            schedules = Schedule.objects.all()
            raw_schedules = [(s.start_time.strftime("%H:%M"), [_proc_to_dict(s.procedure), _schedule_to_dict(s)]) for s in schedules]
            # schedule_dict = {t: [] for t,_ in raw_schedules}
            # for t, s in raw_schedules:
            #     schedule_dict[t].append(s)
            # patient_order = [[k,] for k, v in schedule_dict.items()]
            patient_order = raw_schedules
        context['schedule_status'] = {
            'all_calculated': all_calculated,
            'is_empty': is_empty,
            'message': "Add items and calculate Schedule" if is_empty else ("Schedule Calculated" if all_calculated else "Schedule needs calculation"),
            'status_color': "gray" if is_empty else ("green" if all_calculated else "orange"),
        }
        context['doses_to_order'] = json.dumps(doses_to_order)
        context['patient_order'] = json.dumps(patient_order)
        context['order_times'] = Order.objects.all()
        context['milking_times'] = MilkingTimes.objects.all()
        context['milking_times_list'] = [t.time.strftime("%H:%M") for t in MilkingTimes.objects.all()]
        return context


class ScheduleCreateView(CreateView):
    model = Schedule
    template_name = 'schedule/schedule_form.html'
    form_class = ScheduleForm
    success_url = reverse_lazy('schedule_list')


class ClearScheduleView(View):
    def post(self, request, *args, **kwargs):
        Schedule.objects.all().delete()
        Order.objects.all().delete()
        MilkingTimes.objects.all().delete()
        return HttpResponseRedirect(reverse('schedule_list'))


class CalculateScheduleView(View):
    def post(self, request, *args, **kwargs):
        schedules = Schedule.objects.all()
        Order.objects.all().delete()
        MilkingTimes.objects.all().delete()

        calculate_schedule(list(schedules))

        return HttpResponseRedirect(reverse('schedule_list'))


