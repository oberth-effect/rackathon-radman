from django.db import models

class Procedure(models.Model):
    name = models.CharField(max_length=255)
    compound = models.ForeignKey('radiopharma.Compound', on_delete=models.CASCADE)
    required_specific_dose = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    required_fixed_dose = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    accumulation_time = models.IntegerField()
    measuring_time = models.IntegerField()
    accumulation_time2 = models.IntegerField(null=True, blank=True)
    measuring_time2 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.compound} - {self.name}"
