from django.db import models

class Defect(models.Model):
    line_number = models.CharField(max_length=20)
    structure_id = models.CharField(max_length=20)
    inspection_status = models.CharField(max_length=20)
    file = models.CharField(max_length=100)
    feature = models.CharField(max_length=50)
    defect = models.TextField()  # To store the array as a string
    description = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=10)
    position = models.IntegerField()

   
