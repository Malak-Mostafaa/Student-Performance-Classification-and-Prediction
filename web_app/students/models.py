from django.db import models
from django.contrib.auth.models import User

# model to store student prediction history
class PredictionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # relation between prediction and user
    prediction = models.CharField(max_length=50)   # high low risk
    probability = models.FloatField()  #prediction probability score 
    created_at = models.DateTimeField(auto_now_add=True)  #prediction date and time 
    
    # input features used for prediction
    assessments_submitted = models.FloatField(default=0)
    total_weight = models.FloatField(default=0)
    active_days = models.FloatField(default=0)
    avg_score = models.FloatField(default=0)
    min_score = models.FloatField(default=0)
    total_clicks = models.FloatField(default=0)
    max_score = models.FloatField(default=0)
    studied_credits = models.FloatField(default=0)
    num_of_prev_attempts = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.prediction}"
