from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from procedures.models import Procedure
from procedures.forms import ProcedureForm

class ProcedureListView(ListView):
    model = Procedure
    template_name = 'procedures/procedure_list.html'
    context_object_name = 'procedures'

class ProcedureCreateView(CreateView):
    model = Procedure
    form_class = ProcedureForm
    template_name = 'procedures/procedure_form.html'
    success_url = reverse_lazy('procedure_list')

class ProcedureUpdateView(UpdateView):
    model = Procedure
    form_class = ProcedureForm
    template_name = 'procedures/procedure_form.html'
    success_url = reverse_lazy('procedure_list')