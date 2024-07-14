from django.db import models


# Create your models here.
class DailyRevenue(models.Model):
    revenue_id = models.AutoField(primary_key=True)
    date_time = models.DateTimeField()
    revenue = models.FloatField()
