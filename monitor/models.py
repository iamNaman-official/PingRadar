from __future__ import annotations

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Website(models.Model):
    """Model representing a website to be monitored."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='websites')
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paused = models.BooleanField(default=False)
    timer = models.PositiveBigIntegerField(default=60, help_text="Time interval in seconds between checks.")

    def __str__(self) -> str:
        return self.name

    def uptime_percentage(self) -> float | None:
        """Calculates the uptime percentage based on the status checks."""
        total_checks = self.checks.count()
        if total_checks == 0:
            return None
        up_checks = self.checks.filter(is_up=True).count()
        return round(((up_checks / total_checks) * 100), 2)

    def latest_check(self) -> StatusCheck | None:
        """Returns the latest status check for the website."""
        return self.checks.first()

    def response_time_history(self, limit: int = 20) -> dict[str, list]:
        """Returns response time history for charts."""
        checks = list(self.checks.all()[:limit])
        checks.reverse()

        return {
            "labels": [
                check.timestamp.strftime("%H:%M:%S")
                for check in checks
            ],
            "response_times": [
                check.response_time_ms
                for check in checks
            ],
        }

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['owner', 'url'], name='unique_website_per_user')
    ]


class StatusCheck(models.Model):
    """Model representing a status check for a website."""
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name='checks')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_up = models.BooleanField()
    response_time_ms = models.IntegerField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['website', '-timestamp']),
        ]

    def __str__(self) -> str:
        """Returns a string representation of the status check."""
        return f"{self.website.name} - {'UP' if self.is_up else 'DOWN'} at {self.timestamp}"