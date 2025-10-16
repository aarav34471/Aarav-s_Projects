
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from core.models import Graduate
from rest_framework import status

class GraduateAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='graduser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_graduate(self):
        data = {
            "user": self.user.id,
            "status": "UG",
            "recommendation_tags": [["AI", "Machine Learning"]],
            "degree": "BSc CS",
            "email": "grad@example.com",
            "preference": []
        }
        response = self.client.post("/api/graduates/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
