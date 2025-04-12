from django import forms
from procedures.models import Procedure
from radman.forms import StyledModelForm

class ProcedureForm(StyledModelForm):
    class Meta:
        model = Procedure
        fields = [
            'name',
            'compound',
            'required_specific_dose',
            'required_fixed_dose',
            'accumulation_time',
            'measuring_time',
            'accumulation_time2',
            'measuring_time2'
        ]
        widgets = {
            'accumulation_time': forms.NumberInput(attrs={'class': 'border border-gray-300 rounded p-2'}),
            'measuring_time': forms.NumberInput(attrs={'class': 'border border-gray-300 rounded p-2'}),
            'accumulation_time2': forms.NumberInput(attrs={'class': 'border border-gray-300 rounded p-2'}),
            'measuring_time2': forms.NumberInput(attrs={'class': 'border border-gray-300 rounded p-2'}),
        }
