from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Patient
from .forms import PatientForm

class PatientListView(ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'procedures'

class AddPatientView(CreateView):
    template_name = 'patients/patient_form.html'
    form_class = PatientForm
    success_url = reverse_lazy('patient_list')

class EditPatientView(UpdateView):
    model = Patient
    template_name = 'patients/patient_form.html'
    form_class = PatientForm
    success_url = reverse_lazy('patient_list')

class DeletePatientView(DeleteView):
    model = Patient
    success_url = reverse_lazy('patient_list')
