from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView
from django.views import View
from django.http import HttpResponseRedirect

from .forms import ScheduleForm
from .models import Schedule  # Import the Schedule model

class ScheduleListView(ListView):
    model = Schedule
    template_name = 'schedule/schedule_list.html'  # Specify the template
    context_object_name = 'schedules'
    ordering = ['start_time']  # Order by start_time

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_calculated = not Schedule.objects.filter(calculated=False).exists()
        is_empty = not Schedule.objects.exists()
        context['schedule_status'] = {
            'all_calculated': all_calculated,
            'message': "Add items and calculate Schedule" if is_empty else ("Schedule Calculated" if all_calculated else "Schedule needs calculation"),
            'status_color': "gray" if is_empty else ("green" if all_calculated else "orange")
        }
        return context


class ScheduleCreateView(CreateView):
    model = Schedule
    template_name = 'schedule/schedule_form.html'
    form_class = ScheduleForm
    success_url = reverse_lazy('schedule_list')


class ClearScheduleView(View):
    def post(self, request, *args, **kwargs):
        Schedule.objects.all().delete()
        return HttpResponseRedirect(reverse('schedule_list'))


class CalculateScheduleView(View):
    def post(self, request, *args, **kwargs):
        # Placeholder logic for assigning times to Schedule elements
        for schedule in Schedule.objects.all():
            schedule.start_time = "09:00:00"
            schedule.calculated  = True
            schedule.save()
        return HttpResponseRedirect(reverse('schedule_list'))


