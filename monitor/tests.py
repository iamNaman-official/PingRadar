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

    def test_latest_check_returns_latest_status_check(self):
        check1 = StatusCheck.objects.create(
            website=self.website,
            is_up=True
        )
        check2 = StatusCheck.objects.create(
            website=self.website,
            is_up=False
        )
        check3 = StatusCheck.objects.create(
            website=self.website,
            is_up=True
        )
        latest_check = self.website.latest_check()
        self.assertEqual(
            latest_check,
            check3
        )
        self.assertNotEqual(
            latest_check,
            check1
        )
        self.assertNotEqual(
            latest_check,
            check2
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
        self.assertTrue(
            check.is_up
        )
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

    def test_user_cannot_view_other_users_website(self):
        other_website = Website.objects.create(
            name="Other Website",
            url="http://other.com",
            owner=self.other_user
        )
        self.client.login(
            username="testuser",
            password="password"
        )
        response = self.client.get(
            reverse(
                "website_detail",
                args=[other_website.id]
            )
        )
        self.assertEqual(
            response.status_code,
            404
        )


class AuthenticationTestCase(TestCase):
    """Tests for authentication views."""
    def test_signup_page_loads(self):
        response = self.client.get(
            reverse("signup")
        )
        self.assertEqual(
            response.status_code,
            200
        )

    def test_signup_success(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "strongpassword123",
                "password2": "strongpassword123",
            }
        )
        self.assertEqual(
            response.status_code,
            302
        )
        self.assertTrue(
            User.objects.filter(
                username="newuser"
            ).exists()
        )


class WebsiteViewTestCase(TestCase):
    """Tests for website views."""
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password"
        )
        self.website = Website.objects.create(
            owner=self.user,
            name="Test Website",
            url="https://example.com"
        )
        self.client.login(
            username="testuser",
            password="password"
        )

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("dashboard")
        )
        self.assertEqual(
            response.status_code,
            302
        )
        self.assertIn(
            "/login/",
            response.url
        )

    def test_dashboard_loads_for_authenticated_user(self):
        response = self.client.get(
            reverse("dashboard")
        )
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertContains(
            response,
            "Test Website"
        )
    def test_dashboard_only_shows_owned_websites(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="password"
        )
        Website.objects.create(
            owner=other_user,
            name="Other Website",
            url="https://other.com"
        )
        response = self.client.get(
            reverse("dashboard")
        )
        self.assertContains(
            response,
            "Test Website"
        )
        self.assertNotContains(
            response,
            "Other Website"
        )

    def test_website_detail_page_loads(self):
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
        self.assertContains(
            response,
            "Test Website"
        )

    def test_user_can_add_website(self):
        response = self.client.post(
            reverse("add_website"),
            {
                "name": "New Website",
                "url": "newexample.com",
                "timer": "10",
            }
        )
        self.assertEqual(
            response.status_code,
            302
        )
        website = Website.objects.get(
            name="New Website"
        )
        self.assertEqual(
            website.owner,
            self.user
        )
        self.assertEqual(
            website.url,
            "https://newexample.com"
        )
        self.assertEqual(
            website.timer,
            10
        )

    def test_invalid_url_is_rejected(self):
        response = self.client.post(
            reverse("add_website"),
            {
                "name": "Invalid Website",
                "url": "not-a-valid-url",
                "timer": "10",
            }
        )
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertContains(
            response,
            "Please enter a valid URL."
        )
        self.assertFalse(
            Website.objects.filter(
                name="Invalid Website"
            ).exists()
        )

    def test_duplicate_website_is_rejected(self):
        response = self.client.post(
            reverse("add_website"),
            {
                "name": "Duplicate Website",
                "url": "https://example.com",
                "timer": "10",
            }
        )
        self.assertEqual(
            response.status_code,
            200
        )
        self.assertContains(
            response,
            "You already have a website with this URL."
        )

    def test_user_can_delete_website(self):
        website_id = self.website.id
        response = self.client.post(
            reverse(
                "delete_website",
                args=[website_id]
            )
        )
        self.assertEqual(
            response.status_code,
            302
        )
        self.assertFalse(
            Website.objects.filter(
                id=website_id
            ).exists()
        )

    def test_user_can_toggle_pause_website(self):
        self.assertFalse(
            self.website.is_paused
        )
        response = self.client.post(
            reverse(
                "toggle_pause",
                args=[self.website.id]
            )
        )
        self.assertEqual(
            response.status_code,
            302
        )
        self.website.refresh_from_db()
        self.assertTrue(
        self.website.is_paused
        )