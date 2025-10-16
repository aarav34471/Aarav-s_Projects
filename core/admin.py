from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import *


admin.site.register(Graduate)
admin.site.register(Employer)
admin.site.register(Mentor)
admin.site.register(Job)
admin.site.register(Resources)
admin.site.register(Bookmark)
admin.site.register(Event)
admin.site.register(JobApplication)

