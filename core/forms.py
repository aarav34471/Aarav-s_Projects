#forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .views import *

class LoginForm(forms.Form):
     """"
     A login form that allows the user to enter their username and password, on the home.html page
     """
     username = forms.CharField(max_length=65)
     password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class CustomUserCreationForm(forms.ModelForm):
    """
    This for is a custom user creation form that allows the user to select their account type when
    joining ReadyJobs. It the fields incorporates the username, password, and email fields from django's
    built in User model. The account type is the custom field that is added to the form.
    """
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    account_type = forms.ChoiceField(choices=[
        ('graduate', 'Graduate'),
        ('employer', 'Employer'),
        ('mentor', 'Mentor'),
    ])

    class Meta:
        model = User
        fields = ['username', 'password','account_type', 'email', 'password2']

    def save(self, commit=True):
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise forms.ValidationError("Passwords do not match.")

        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Create the corresponding profile based on account type
            account_type = self.cleaned_data['account_type']
            if account_type == 'graduate':
                Graduate.objects.create(user=user)
            elif account_type == 'employer':
                Employer.objects.create(user=user)
            elif account_type == 'mentor':
                Mentor.objects.create(user=user)
        return user



class ApplicationForm(forms.ModelForm):
    """
    This form is used by  the graduate to apply for a job, currently the form only only supports uploading a 
    CV and cover letter but, in the future we'd like to expand this to have other fields such as links to their social media
    """
    class Meta:
        model = JobApplication
        fields = ['cover_letter','cv']
      