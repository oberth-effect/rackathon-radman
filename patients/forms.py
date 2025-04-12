from django import forms
from .models import Patient

from radman.forms import StyledModelForm

class PatientForm(StyledModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'surname', 'id_number', 'weight']
