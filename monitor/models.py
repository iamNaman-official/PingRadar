from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Websites(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StatusCheck(models.Model):
    website = models.ForeignKey(Websites, on_delete=models.CASCADE, related_name='checks')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_up = models.BooleanField()
    response_time_ms = models.IntegerField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

        def __str__(self):
            return f"{self.website.name} - {'UP' if self.is_up else 'DOWN'} at {self.timestamp}"