from core.models import User, Graduate, Employer, Mentor, Job
from django.core.management.base import BaseCommand

#Seed.py is for templates and testing that the frontend can fetch from the Django API
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Clear existing data (optional, for a clean slate)
        User.objects.all().delete()
        Graduate.objects.all().delete()
        Employer.objects.all().delete()
        Mentor.objects.all().delete()
        Job.objects.all().delete()

      
        # Create Employers
        employer1_user = User.objects.create_user(username="employer1", password="password123", email="employer1@example.com")

        employer1 = Employer.objects.create(
            user=employer1_user,
            address="Employer 1 Address",
            biography="Biography for Employer 1",
            latitude=51.51279, 
            longitude=-0.09184
        )

        employer2_user = User.objects.create_user(username="employer2", password="password123", email="employer2@example.com")
        employer2 = Employer.objects.create(
            user=employer2_user,
            address="Employer 2 Address",
            biography="Biography for Employer 2",
            latitude=52.48142, 
            longitude=-1.89983
        )

        Job.objects.create(
            title="Systems Analyst", 
            salary=31000, description="Test the security of our systems", 
            location="Birmingham, UK", 
            latitude=53.41058,
            longitude=-2.97794,
            expiration="2025-12-31", 
            requirements="Degree in computer science or relevant study", 
            tags=["AI", "Cyber Security", "Finance"], 
            company=employer1)
        
        Job.objects.create(
            title="Pharmacist", 
            salary=32000, 
            description="Provide prescriptions", 
            location="Liverpool, UK", 
            latitude=53.41058,
            longitude=-2.97794,
            expiration="2025-12-31", 
            requirements="Degree in chemistry ", 
            tags=["Medicine", "Diverse Workplace", "Chemistry"], 
            company=employer1)
        
        Job.objects.create(
            title="Data Scientist", 
            salary=33000, 
            description="Analyse trends in the market", 
            location="Leeds, UK", 
            latitude=53.79648,
            longitude=-1.54785,
            expiration="2025-12-31", 
            requirements="", 
            tags=["Physics", "Maths", "Carbon Neutral"], 
            company=employer1)
        
        Job.objects.create(
            title="AI trainer", 
            salary=34000, 
            description="AI in therapy", 
            location="Sheffield, UK", 
            latitude=53.38297,
            longitude=-1.4659,
            expiration="2025-12-31", 
            requirements="Requirements for Job 4", 
            tags=["Psychology", "Maths", "AI"], 
            company=employer1)

        Job.objects.create(
            title="Business Analytics", 
            salary=31000, 
            description="Analyse trends in the market", 
            location="Bristol, UK", expiration="2025-12-31",
            latitude=51.45523,
            longitude=-2.59665, 
            requirements="Experience in Economics", 
            tags=["AI", "Economics", "Finance"], 
            company=employer2)
        

        Job.objects.create(
            title="Lab Assistant",
            salary=32000,
            description="Assist with labwork", 
            location="Leicester, UK", 
            latitude=52.6386,
            longitude=-1.13169,
            expiration="2025-12-31", 
            requirements="Degree in biology", 
            tags=["Medicine", "Biology", "Diverse Workforce"], 
            company=employer2)
        
        Job.objects.create(
            title="University Professor", 
            salary=33000, 
            description="Teach undergraduates", 
            location="Edinburgh,UK", 
            expiration="2025-12-31", 
            requirements="Experience in Economics", 
            latitude=55.95206,
            longitude=-3.19648,
            tags=["Physics", "Maths", "Economics"], 
            company=employer2)
        

        Job.objects.create(
            title="Environmental Engineer", 
            salary=34000, 
            description="Contribute to a Carbon Neutral Envrionment", 
            location="Hull, UK", 
            expiration="2025-12-31", 
            latitude=53.7446,
            longitude=-0.33525,
            requirements="Degree in environmenal engineering", 
            tags=["Engineering", "Carbon Neutral", "Diverse Workplace"], 
            company=employer2)

        # Create Graduates
        graduate1_user = User.objects.create_user(username="Mike", password="password123", email="mike@example.com")

        graduate1 = Graduate.objects.create(
            user=graduate1_user, 
            status="UG", 
            degree="Computer Science", 
            recommendation_tags=["AI", "Cyber Security", "Finance", "Diverse Workplace"], 
            tag_scores=[0, 0, 0, 2],
            latitude=51.45625,
            longitude=-0.97113)  # Reading, UK

        graduate2_user = User.objects.create_user(username="Wendy", password="password123", email="wendy@example.com")

        graduate2 = Graduate.objects.create(
            user=graduate2_user, 
            status="PG", 
            degree="Physics", 
            recommendation_tags=["Biology", "Chemistry", "Physics", "Maths"], 
            tag_scores=[0, 0, 0, 0],
            latitude=52.92277,
            longitude=-1.47663) # Derby, UK

        graduate3_user = User.objects.create_user(username="Gloria", password="password123", email="gloria@example.com")

        graduate3 = Graduate.objects.create(
            user=graduate3_user, 
            status="UG", 
            degree="Economics", 
            recommendation_tags=["Economics", "Psychology", "Carbon Neutral", "AI"], 
            tag_scores=[0, 0, 2, 0],
            latitude=52.9536,
            longitude=-1.15047) # Nottingham

        graduate4_user = User.objects.create_user(username="Robert", password="password123", email="rober@example.com")

        graduate4 = Graduate.objects.create(
            user=graduate4_user, 
            status="PG", 
            degree="Biology", 
            recommendation_tags=["Cyber Security", "Finance", "Medicine", "Biology"], 
            tag_scores=[0, 0, 0, 0],
            latitude=51.87967,
            longitude=-0.41748 # Lutton
            )

print("Seed Successful!")


