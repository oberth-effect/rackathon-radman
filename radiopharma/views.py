from django.views.generic import ListView
from django.views.generic.edit import CreateView, FormView
from django.views.generic import UpdateView, DeleteView, View
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, render

from radiopharma.forms import CompoundForm, BatchForm, UsedDoseForm, DeliveryTimesForm
from radiopharma.models import Compound, Batch, UsedDose, DeliveryTimes
from datetime import datetime, time, timedelta


class CompoundListView(ListView):
    model = Compound

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('deliverytimes_set')


class CompoundCreateView(CreateView):
    model = Compound
    form_class = CompoundForm
    template_name = 'radiopharma/compound_form.html'
    success_url = reverse_lazy('compound_list')


class CompoundUpdateView(UpdateView):
    model = Compound
    form_class = CompoundForm
    template_name = 'radiopharma/compound_form.html'
    success_url = reverse_lazy('compound_list')


class BatchListView(ListView):
    model = Batch
    template_name = 'radiopharma/batch_list.html'
    context_object_name = 'batches'

    def get_queryset(self):
        show_discarded = self.request.GET.get('show_discarded', 'false') == 'true'
        if show_discarded:
            return Batch.objects.all()
        return Batch.objects.filter(discarded=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_discarded'] = self.request.GET.get('show_discarded', 'false') == 'true'
        now = datetime.now().time()
        start_time = time(6, 30)
        end_time = time(18, 30)
        interval = timedelta(minutes=5)
        current_time = datetime.combine(datetime.today(), start_time)
        end_datetime = datetime.combine(datetime.today(), end_time)
        time_list = []

        while current_time <= end_datetime:
            time_list.append(current_time.time())
            current_time += interval

        graph_data = {
            'times': [int(datetime.combine(datetime.today(), t).timestamp() * 1000) for t in time_list],
            'batches': []
        }

        for batch in context['batches']:
            batch.remaining_activity = batch.activity_in_time(now)
            if not batch.discarded:
                activities = [
                    batch.activity_in_time(t) for t in time_list
                ]
                graph_data['batches'].append({
                    'batch_name': batch.batch_name,
                    'activities': activities,
                })

        context['graph_data'] = graph_data

        used_doses = UsedDose.objects.filter(batch__in=context['batches'])
        context['used_doses'] = [
            {
                'batch_name': dose.batch.batch_name,
                'use_time': datetime.combine(datetime.today(), dose.use_time).timestamp() * 1000,
                'used_activity': float(dose.used_activity)
            }
            for dose in used_doses
        ]

        return context


class BatchCreateView(CreateView):
    model = Batch
    form_class = BatchForm
    template_name = 'radiopharma/batch_form.html'
    success_url = reverse_lazy('batch_list')


class BatchDiscardView(UpdateView):
    model = Batch

    def post(self, request, *args, **kwargs):
        batch = self.get_object()
        batch.discarded = True
        batch.save()
        return HttpResponseRedirect(reverse('batch_list'))


class UsedDoseCreateView(CreateView):
    model = UsedDose
    form_class = UsedDoseForm
    template_name = 'radiopharma/useddose_form.html'
    success_url = reverse_lazy('batch_list')


class DeliveryTimesListView(ListView):
    model = DeliveryTimes
    template_name = 'radiopharma/delivery_times_list.html'
    context_object_name = 'delivery_times'


class DeliveryTimesCreateView(CreateView):
    model = DeliveryTimes
    form_class = DeliveryTimesForm
    template_name = 'radiopharma/delivery_times_form.html'
    success_url = reverse_lazy('delivery_times_list')


class DeliveryTimesDeleteView(DeleteView):
    model = DeliveryTimes
    success_url = reverse_lazy('delivery_times_list')


