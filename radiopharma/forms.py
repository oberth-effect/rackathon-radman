from radiopharma.models import Compound, Batch, UsedDose, DeliveryTimes
from django import forms
from radman.forms import StyledModelForm


class CompoundForm(StyledModelForm):
    class Meta:
        model = Compound
        fields = ['name', 'half_life', 'price']


class BatchForm(StyledModelForm):
    class Meta:
        model = Batch
        fields = ['batch_name', 'compound', 'delivered_activity', 'delivery_time']
        widgets = {
            'delivery_time': forms.TimeInput(attrs={'type': 'time', 'class': 'border border-gray-300 rounded p-2'}),
        }


class UsedDoseForm(StyledModelForm):
    class Meta:
        model = UsedDose
        fields = ['batch', 'used_activity', 'use_time', 'notes']
        widgets = {
            'use_time': forms.TimeInput(attrs={'type': 'time', 'class': 'border border-gray-300 rounded p-2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['batch'].queryset = Batch.objects.filter(discarded=False)

class DeliveryTimesForm(StyledModelForm):
    class Meta:
        model = DeliveryTimes
        fields = ['compound', 'time']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'border border-gray-300 rounded p-2'}),
        }
