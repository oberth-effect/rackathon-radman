from django.db import models
import math
import datetime

def timediff(time1, time2):
    """Calculate the difference between two time objects."""
    t1 = datetime.datetime.combine(datetime.date.today(), time1)
    t2 = datetime.datetime.combine(datetime.date.today(), time2)
    return abs((t2 - t1).total_seconds())

class Compound(models.Model):
    name = models.CharField(max_length=255)
    half_life = models.DecimalField(decimal_places=2, max_digits=10)
    price = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return self.name

    @property
    def decay_constant(self):
        half_life_s = self.half_life * 60
        return math.log(2) / float(half_life_s)


class Batch(models.Model):
    batch_name = models.CharField(max_length=255)
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    delivered_activity = models.DecimalField(decimal_places=2, max_digits=10)
    delivery_time = models.TimeField()
    discarded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.batch_name} ({self.compound})"

    def activity_in_time(self, time: datetime.time):
        if time < self.delivery_time:
            return 0.0
        decay_constant = self.compound.decay_constant
        uses = (u for u in self.useddose_set.filter(batch=self) if u.use_time <= time)
        eff_use = sum(float(u.used_activity) * math.exp(self.compound.decay_constant * timediff(u.use_time, self.delivery_time)) for u in uses)
        return (float(self.delivered_activity) - eff_use) * math.exp(-decay_constant * timediff(time, self.delivery_time))


class UsedDose(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    used_activity = models.DecimalField(decimal_places=2, max_digits=10)
    use_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)

class DeliveryTimes(models.Model):
    compound = models.ForeignKey(Compound, on_delete=models.CASCADE)
    time = models.TimeField()

    def __str__(self):
        return f"{self.time} for {self.compound.name}"

