from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Website, StatusCheck


class UptimePercentageTestCase(TestCase):
    """
    Covers:
    - Uptime percentage math (zero checks, all up, all down, mixed)
    - Ownership security (one user cannot view/delete another user's website)
    - Delete actually removes the row from the database
    """

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        self.website = Website.objects.create(
            name='Test Website', url='http://testwebsite.com', owner=self.user
        )

    # --- Uptime percentage math ---

    def test_uptime_is_none_with_zero_checks(self):
        self.assertIsNone(self.website.uptime_percentage())

    def test_uptime_percentage_with_all_up_checks(self):
        StatusCheck.objects.create(website=self.website, is_up=True)
        StatusCheck.objects.create(website=self.website, is_up=True)
        self.assertEqual(self.website.uptime_percentage(), 100.0)

    def test_uptime_percentage_with_all_down_checks(self):
        StatusCheck.objects.create(website=self.website, is_up=False)
        StatusCheck.objects.create(website=self.website, is_up=False)
        self.assertEqual(self.website.uptime_percentage(), 0.0)

    def test_uptime_percentage_with_mixed_checks(self):
        # 3 up, 1 down -> 75.0%
        StatusCheck.objects.create(website=self.website, is_up=True, response_time_ms=100)
        StatusCheck.objects.create(website=self.website, is_up=True, response_time_ms=110)
        StatusCheck.objects.create(website=self.website, is_up=True, response_time_ms=120)
        StatusCheck.objects.create(website=self.website, is_up=False, response_time_ms=None)
        self.assertEqual(self.website.uptime_percentage(), 75.0)

    # --- Ownership security ---

    def test_other_user_cannot_view_someone_elses_website_detail(self):
        self.client.login(username='otheruser', password='otherpassword')
        response = self.client.get(reverse('website_detail', args=[self.website.id]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_view_own_website_detail(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('website_detail', args=[self.website.id]))
        self.assertEqual(response.status_code, 200)

    # --- Delete behavior ---

    def test_delete_actually_removes_website(self):
        self.client.login(username='testuser', password='testpassword')
        self.client.post(reverse('delete_website', args=[self.website.id]))
        self.assertFalse(Website.objects.filter(id=self.website.id).exists())