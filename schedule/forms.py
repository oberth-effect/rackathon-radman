from radman.forms import StyledModelForm
from schedule.models import Schedule


class ScheduleForm(StyledModelForm):
    class Meta:
        model = Schedule
        fields =  ['patient', 'procedure']
