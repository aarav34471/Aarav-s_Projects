
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Graduate, Job, Employer, Bookmark
from datetime import datetime, timedelta

class GraduateModelTest(TestCase):
    def test_create_graduate(self):
        user = User.objects.create_user("testuser", password="testpass")
        grad = Graduate.objects.create(
            user=user,
            status="UG",
            recommendation_tags=[["AI", "ML"]],
            degree="CS",
            email="test@test.com"
        )
        self.assertEqual(grad.status, "UG")
        self.assertEqual(grad.degree, "CS")

class BookmarkModelTest(TestCase):
    def test_status_default(self):
        user = User.objects.create_user("jobber", password="123")
        employer = Employer.objects.create(user=user, address="Here", email="emp@test.com")
        job = Job.objects.create(
            title="Job",
            salary=50000,
            description="Desc",
            location="Loc",
            expiration=datetime.now() + timedelta(days=30),
            comapany=employer,
            requirements="None",
            tags="Tech",
            job_type="FT"
        )
        grad = Graduate.objects.create(user=user, status="UG", recommendation_tags=[["AI", "ML"]], degree="CS", email="g@e.com")
        bookmark = Bookmark.objects.create(gradID=grad, jobID=job)
        self.assertEqual(bookmark.status, "INCOMPLETE")
