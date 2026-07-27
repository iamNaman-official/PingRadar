from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Website(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def uptime_percentage(self):
        total_checks = self.checks.count()
        if total_checks == 0:
            return 0
        up_checks = self.checks.filter(is_up=True).count()
        return (up_checks / total_checks) * 100

    def latest_status(self):
        return self.checks.first()

    def response_time_history(self, limit=20):
        checks = self.checks.all()[:limit][::-1]  # Get the latest 20 checks and reverse the order
        return {
            'labels': [c.timestamp.strftime('%H:%M:%S') for c in checks],
            'response_times': [c.response_time_ms for c in checks],
        }


class StatusCheck(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='checks')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_up = models.BooleanField()
    response_time_ms = models.IntegerField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

        def __str__(self):
            return f"{self.website.name} - {'UP' if self.is_up else 'DOWN'} at {self.timestamp}"