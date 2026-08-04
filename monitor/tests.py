from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import StatusCheck, Website


class WebsiteTestCase(TestCase):
    """Test cases for the Website model."""
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )
        self.website = Website.objects.create(
            name="Test Website",
            url="http://testwebsite.com",
            owner=self.user
        )

    def test_uptime_is_none_with_zero_checks(self):
        self.assertIsNone(
            self.website.uptime_percentage()
        )

    def test_uptime_percentage_with_all_up_checks(self):
        StatusCheck.objects.create(
            website=self.website,
            is_up=True
        )
        StatusCheck.objects.create(
            website=self.website,
            is_up=True
        )
        self.assertEqual(
            self.website.uptime_percentage(),
            100.0
        )

    def test_uptime_percentage_with_mixed_checks(self):
        StatusCheck.objects.create(
            website=self.website,
            is_up=True
        )
        StatusCheck.objects.create(
            website=self.website,
            is_up=False
        )
        self.assertEqual(
            self.website.uptime_percentage(),
            50.0
        )

class StatusCheckModelTestCase(TestCase):
    """Test cases for the StatusCheck model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password"
        )

        self.website = Website.objects.create(
            name="Test Website",
            url="http://test.com",
            owner=self.user
        )

    def test_status_check_creation(self):
        check = StatusCheck.objects.create(
            website=self.website,
            is_up=True,
            status_code=200,
            response_time_ms=120
        )
        self.assertEqual(
            check.website,
            self.website
        )
        self.assertTrue(check.is_up)
        self.assertEqual(
            check.status_code,
            200
        )
        self.assertEqual(
            check.response_time_ms,
            120
        )

class WebsiteSecurityTestCase(TestCase):
    """Test cases for website access security."""
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="password"
        )

        self.website = Website.objects.create(
            name="Private Website",
            url="http://test.com",
            owner=self.user
        )

    def test_other_user_cannot_view_website(self):
        self.client.login(
            username="otheruser",
            password="password"
        )
        response = self.client.get(
            reverse(
                "website_detail",
                args=[self.website.id]
            )
        )
        self.assertEqual(
            response.status_code,
            404
        )

    def test_owner_can_view_own_website(self):
        self.client.login(
            username="testuser",
            password="password"
        )
        response = self.client.get(
            reverse(
                "website_detail",
                args=[self.website.id]
            )
        )
        self.assertEqual(
            response.status_code,
            200
        )