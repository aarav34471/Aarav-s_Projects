
from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Graduate
from django.urls import reverse

class GraduateViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("grad", "grad@test.com", "pass123")
        self.client.login(username="grad", password="pass123")

    def test_create_graduate_view(self):
        response = self.client.get(reverse("sign_up"))
        self.assertEqual(response.status_code, 200)
