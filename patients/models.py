from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    id_number = models.CharField(max_length=255)
    weight = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.surname}, {self.name} ({self.id_number})"




