from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class NavbarViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        # Create a user for login/logout tests
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123",
        )
        self.user.is_active = True
        self.user.save()

    def test_login_page_loads(self):
        """Login page should load with status 200"""
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "navbar/login.html")

    def test_login_with_valid_credentials(self):
        """Login should succeed with correct email & password"""
        response = self.client.post(reverse("login"), {
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        self.assertRedirects(response, reverse("home"))

    def test_login_with_invalid_credentials(self):
        """Invalid login should show error"""
        response = self.client.post(reverse("login"), {
            "email": "wrong@example.com",
            "password": "wrongpass"
        }, follow=True)
        self.assertContains(response, "Invalid email or password.")

    def test_register_user(self):
        """Register new user and check inactive"""
        # Match the form fields exactly with your RegistrationForm
        response = self.client.post(reverse("register"), {
            "name": "New User",
            "email": "new@example.com",
            "password": "newpass123",
            "city": "Pune"
        }, follow=True)

        # User should be created
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        user = User.objects.get(email="new@example.com")
        self.assertFalse(user.is_active)  # Should be inactive until email activation

    def test_account_activation(self):
        """Account activation should activate user"""
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="inactivepass"
        )
        inactive_user.is_active = False
        inactive_user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(inactive_user.pk))
        token = default_token_generator.make_token(inactive_user)

        response = self.client.get(reverse("activate", kwargs={
            "uidb64": uidb64,
            "token": token
        }), follow=True)

        inactive_user.refresh_from_db()
        self.assertTrue(inactive_user.is_active)
        self.assertContains(response, "Your account has been activated successfully!")

    def test_password_reset_page_loads(self):
        """Password reset page should load"""
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "navbar/password_reset.html")

    def test_logout_redirects(self):
        """Logout should redirect to home"""
        self.client.login(email="testuser@example.com", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("home"))
