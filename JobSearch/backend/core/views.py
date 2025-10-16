# .backend/core/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from typing import Any
from .models import *
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.templatetags.static import static
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import LoginForm, CustomUserCreationForm, ApplicationForm
from django.views.generic import *
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"

    def form_valid(self, form):
        messages.success(self.request, "Your account has been created successfully!")
        return super().form_valid(form)


class ManageApplicationsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = JobApplication
    template_name = "ready_jobs/employer/view_applicants.html"
    context_object_name = "applications"

    def get_queryset(self):
        job = get_object_or_404(Job, id=self.kwargs['job_id'])
        return JobApplication.objects.filter(job=job)

    def test_func(self):
        job = get_object_or_404(Job, id=self.kwargs['job_id'])
        return self.request.user == job.company.user  # Ensure the employer owns the job


class ApplicantDetailView(LoginRequiredMixin, DetailView):
    model = JobApplication
    template_name = "ready_jobs/employer/view_applicant.html"
    context_object_name = "application"

    def get_object(self):
        return get_object_or_404(JobApplication, id=self.kwargs['application_id'])

    def test_func(self):
        application = self.get_object()
        return self.request.user == application.job.company.user  # Ensure the employer owns the job
    


  
    
