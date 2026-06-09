from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from courses.models import Enrollment


class Assessment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
