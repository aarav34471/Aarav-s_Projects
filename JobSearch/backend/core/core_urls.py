# .backend/core/core_urls.py
from django.contrib import admin
from django.urls import path, include
from core.model_views.graduate_views import *
from core.model_views.employer_views import *
from core.model_views.job_views import *
from core.model_views.mentor_views import *
from rest_framework.routers import DefaultRouter
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="home.html"), name="home"),

    
    path('view_graduate/<int:pk>', GraduateDetailView.as_view(), name='view_graduate'),
    path('update_graduate/<int:pk>', UpdateGraduateView.as_view(), name='update_graduate'),
    path('delete_graduate/<int:pk>', DeleteGraduateView.as_view(), name='delete_graduate'),

   
    path('view_employer/<int:pk>', EmployerDetailView.as_view(),name='view_employer'),
    path('update_employer/<int:pk>', UpdateEmployerView.as_view(), name='update_employer'),
    path('delete_employer/<int:pk>', DeleteEmployerView.as_view(), name='delete_employer'),

    path('create_job', CreateJobView.as_view(), name='create_job'),
    path('view_jobs', ViewAllJobs.as_view(), name='view_jobs'),
    path('view_job/<int:pk>', JobDetailView.as_view(), name='view_job'),
    path('apply_to_job/<int:pk>', ApplyJobView.as_view(), name='apply_to_job'),
    path('update_job/<int:pk>', UpdateJobView.as_view(), name='update_job'),
    path('delete_job/<int:pk>', DeleteJobView.as_view(), name='delete_job'),


    path('view_applicants/<int:job_id>/', ManageApplicationsView.as_view(), name='view_applicants'),
    path('view_applicant/<int:application_id>/', ApplicantDetailView.as_view(), name='view_applicant'),
    path('update_application_status/<int:application_id>/', UpdateApplicationStatusView.as_view(), name='update_application_status'),

 
    path('view_mentor/<int:pk>', MentorDetailView.as_view(), name='view_mentor'),
    path('update_mentor/<int:pk>', UpdateMentorView.as_view(), name='update_mentor'),
    path('delete_mentor/<int:pk>',DeleteMentorView.as_view(), name='delete_mentor'),

   
]