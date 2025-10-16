# .backend/core/models.py
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.contrib.postgres.fields import ArrayField



class Graduate(models.Model):
    """
    User - Each Graduate will be mapped to a Django created user
    Status - Each Graduate will either be an undergraduate or postgraduate student
    Recommendation_Tags - A graduate picks a list of things they are interested and it is stored as a PostgreSQL arrayfield. 
                            Example ["Artificial Intelligence","Web development", "Finance", ...]

    Tag_Scores - A graduate picks a list of things they are interested and it is stored as a PostgreSQL arrayfiled. This array is appended 
                 When a graduate interacts with a job that has their respectiv tags


    Job recommendation system - The application uses 2 arrays, one for tags and one for tag scores.
    When a Graduate interacts with a job that has their respective tag interest, the tag_score for that recommendation tag goes up
    
    example - recommendation_tags = [AI, Cybersecurity, Dev OPs] tag_scores = [0,1,4]
    
    when interacting with a job with the AI tag, the tags_scores array should change to [1,1,4] as the AI tag_score has now been incremented by one
    
    Furthermore, jobs should be displayed by which tag is the most popular and descending. So on the home page, this graduate should see "Dev OPs jobs more frequently as they have a score of 4
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    GRADUATE_LEVELS = (
       ("UG", "Undergraduate"),
       ("PG", "Postgraudate")
     
   )
    status = models.CharField(max_length=13, choices=GRADUATE_LEVELS, default="UG")
    recommendation_tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    tag_scores = ArrayField(models.IntegerField(), blank=True, default=list)  
    degree = models.CharField(max_length=128, blank=False)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def add_tag(self, tag):
        if tag not in self.recommendation_tags:
            self.recommendation_tags.append(tag)
            self.tag_scores.append(0)

        self.save()


    def increment_tag_score(self, tag):
        """
         If the tag is "Carbon Neutral" or "Diverse Workplace", increment by 2 as a way to promote more environmentally friednly jobs as
         well as jobs that promote diversity of the workplace. This is a way to comply with the Sustainable Development Goals within the 
         problem statement, and help users from various backgrounds be directed to jobs that suit them
        
        """
        if tag in self.recommendation_tags:
            if tag == "Carbon Neutral" or tag == "Diverse Workplace":
                
                index = self.recommendation_tags.index(tag)
                self.tag_scores[index] += 2
            else:
                index = self.recommendation_tags.index(tag)
                self.tag_scores[index] += 1
        
        self.save()

 
class Employer(models.Model):
    """
    Employers can create jobs, and edit and delete only their job listings.
    They can view all job applications and events
    They can accept, offer interviews, or reject job applications
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    biography = models.TextField(max_length=512)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)


class Mentor(models.Model):
    """
    Mentors are professors who can help Graduates build up skills or provide advice to them
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    mentor_degree = models.CharField(max_length=256, blank=False)

    mentees = models.ManyToManyField(Graduate, blank=True) 

    biography = models.TextField(max_length=512, blank=True)

    
class Job(models.Model):
    """
    Job objects are created by employers, viewed by everyone, edited and deleted by their respective employers
    Title - Name of the Job position
    Salary - How much the job pays annualy
    description - contains details about the tasks performed by employees in this position
    company - a many to one relationship between jobs and the employer, many jobs can belong to one employer
    requirements - The skills needed by the employees
    tags - Used to categorise the job types and recommend said types to graduates who are interested in those tags. For example a job tagged AI will be more likely to be recommended to graduates with the AI recommendation tag
    longitude and latitude - Used to show the location of the job on a map, for routes API
    Jobs can be edited and deleted by only their respective employers
    Graduates can apply to jobs

    """
    title = models.CharField(max_length=256)
    salary = models.FloatField()
    description = models.TextField(max_length=256)
    location = models.TextField(max_length=128)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    expiration = models.DateField()
    company = models.ForeignKey(Employer, on_delete=models.CASCADE)
    requirements = models.TextField(max_length=256)
    tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    JOB_TYPES=(
        ("PT", "Part-time"),
        ("FT", "Full-time")
    )

    job_type = models.CharField(choices=JOB_TYPES, default="Full-time")
    class Meta:
        permissions = [
            ("can_create_graduate", "Can create graduate profile"),
            ("can_edit_graduate", "Can edit graduate profile"),
            ("can_delete_graduate", "Can delete graduate profile"),
        ]
    

 
class JobApplication(models.Model):
    """
        This model is by graduates to apply for jobs and employers can access it to view their applications
        and update the status of their appliation. When completed by a graduate the application is saved as an
        object that is accessible the employer as well. The employer can edit the status of the application.

        Additionally, when saving the application the tag_scores are increased by their respective tag scores
        (Currently 1 for each tage except for "Carbon Neutral" and "Diverse Workplace" which are 2)
    """
    graduate = models.ForeignKey(Graduate, related_name='applications', on_delete=models.CASCADE)
    job = models.ForeignKey(Job, related_name='applications', on_delete=models.CASCADE)
    cover_letter = models.FileField(upload_to='applications/cover_letters/', default='applications/cover_letter/default_cover_letter.pdf')  # Provide a default value
    cv = models.FileField(upload_to='applications/cvs/', default='applications/cvs/default_cv.pdf')
    
    
    APPLICATION_STATUS = (
        ("APPLIED", "Applied"),
        ("INTERVIEW", "Interview"),
        ("OFFER", "Offer"),
        ("REJECTED", "Rejected"),
    )
    
    status = models.CharField(max_length=10, choices=APPLICATION_STATUS, default="APPLIED")
    date_applied = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only increment scores for new applications
            for tag in self.job.tags:
                self.graduate.increment_tag_score(tag)
        super().save(*args, **kwargs)

    
class Event(models.Model):
    """
    Events are created by mentors and can be viewed by everyone
    These events can be for networking or for educational purposes like building job skills
    """
    host = models.ForeignKey(Employer, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=False)
    description = models.CharField(max_length=512)
    date = models.DateTimeField()
    location = models.TextField(max_length=128) 

class Resources(models.Model):
    """
    Resources are created by mentors and can be viewed by all graduates
    """
    author = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    title = models.TextField(max_length=128) 
    desciption = models.TextField(max_length=512)
    url = models.TextField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)

class Bookmark(models.Model):
    gradID = models.ForeignKey(Graduate, on_delete=models.CASCADE)
    jobID = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    APPLICATION_STATUS = (
       ("INCOMPLETE", "Incomplete"),
       ("COMPLETE", "complete"),
       ("EXPIRED","expired")
   )
    
    status = models.CharField(max_length=10, choices=APPLICATION_STATUS, default="INCOMPLETE")
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only increment scores for new bookmarks
            for tag in self.jobID.tags:
                self.gradID.increment_tag_score(tag)
        super().save(*args, **kwargs)


