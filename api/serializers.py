# .backend/api/serializers.py
from rest_framework import serializers
from core.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','first_name','last_name']
        
class GraduateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Graduate
        fields = [
            
        ]
class GraduateReadSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Graduate
        fields = [
            "id",
            "user",
            "email",
            "status",
            "recommendation_tags",
            "tag_scores",
            "degree",
            "latitude",
            "longitude",
        ]
        
        
class MentorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mentor
        fields = '__all__'
        
        
class EmployerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employer
        fields = '__all__'
        
class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = '__all__'

class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = '__all__'

        
class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = '__all__'

class ResourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Resources
        fields = ('name', 'description')


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'

