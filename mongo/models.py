from django.db import models

# Create your models here.
class SensorTag(models.Model):
    tag_id = models.IntegerField()
    #timestamp = models.DateTimeField()
    date = models.CharField(max_length=30)
    value = models.FloatField()

