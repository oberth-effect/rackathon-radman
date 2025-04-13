from django.db import models

from radiopharma.models import Compound, DeliveryTimes

from patients.models import Patient

from procedures.models import Procedure

class Schedule(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
    start_time = models.TimeField(blank=True, null=True)
    calculated = models.BooleanField(default=False)

    def desired_activity(self):
        if self.procedure.required_fixed_dose:
            return self.procedure.required_fixed_dose
        else:
            return self.procedure.required_specific_dose * self.patient.weight


class Order(models.Model):
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    activity = models.DecimalField(max_digits=10, decimal_places=2)
    time_slot = models.ForeignKey(DeliveryTimes, on_delete=models.CASCADE)
    qa_activity = models.DecimalField(max_digits=10, decimal_places=2)

class ScheduleSettings(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

class MilkingTimes(models.Model):
    time = models.TimeField()