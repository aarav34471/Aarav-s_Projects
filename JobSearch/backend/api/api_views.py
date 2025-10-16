# .backend/api/api_views.py
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from .serializers import *
from .auth_serializers import *
from rest_framework.response import Response
from core.models import *
from rest_framework.permissions import IsAdminUser, DjangoModelPermissions
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework import status



from rest_framework.permissions import IsAuthenticated

from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)



class GraduateViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]  
    queryset = Graduate.objects.all()
    
    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return GraduateReadSerializer
        return GraduateSerializer

    def get_queryset(self):
        return Graduate.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)      
    

    def perform_update(self, serializer):
        graduate = self.get_object()
        if graduate.user != self.request.user:
            raise PermissionDenied("You can only update your own profile.")
        
        updated_tags = serializer.validated_data.get('recommendation_tags', [])

        for tag in updated_tags:
            if tag not in graduate.recommendation_tags:
                graduate.add_tag(tag)
            else:
                graduate.increment_tag_score(tag)

        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own profile.")
        instance.delete()
    

class MentorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer

    def get_queryset(self):
        return Mentor.objects.all()  # Anyone can view all mentors

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()  # If not authenticated, user stays null or must be provided manually

    def perform_update(self, serializer):
        mentor = self.get_object()
        if self.request.user != mentor.user:
            raise PermissionDenied("You can only update your own mentor profile.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user:
            raise PermissionDenied("You can only delete your own mentor profile.")
        instance.delete()
    
    
class EmployerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    
    def get_queryset(self):
        return Employer.objects.all()  # All users can see all employer profiles

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()  

    def perform_update(self, serializer):
        employer = self.get_object()
        if employer.user != self.request.user:
            raise PermissionDenied("You can only update your own employer profile.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own employer profile.")
        instance.delete()
    

class JobViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    def get_queryset(self):
        return Job.objects.all()
    
    def list(self, request):
        queryset = self.get_queryset()
        serializers = self.serializer_class(queryset, many=True)
        return Response(serializers.data)
    
    def perform_create(self, serializer):
        
        serializer.save()

    def perform_update(self, serializer):
        job = self.get_object()
        # Ensure the authenticated user is the owner of the job
        if job.company.user != self.request.user:
            raise PermissionDenied("You can only update your own jobs.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        
        # Ensure the authenticated user is the owner of the job
        if job.company.user != self.request.user:
            raise PermissionDenied("You can only delete your own jobs.")
        return super().destroy(request, *args, **kwargs)
        
class BookmarkViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    def get_queryset(self):
        return Bookmark.objects.all()
    
    def list(self, request):
        queryset = self.get_queryset()
        serializers = self.serializer_class(queryset, many=True)
        return Response(serializers.data)
    
    def create(self, request):
        serializers = self.serializer_class(data=request.data)
        if (serializers.is_valid()):
            job_id = serializers.validated_data.get("jobID")
            grad_id = serializers.validated_data.get("gradID")  

            if self.queryset.filter(gradID=grad_id, jobID=job_id).exists():
                return Response("Job already exists", status=409)
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=400)
    
    def retrieve(self, request, pk=None):
        bookmark = self.queryset.get(pk=pk)
        serializers = self.serializer_class(bookmark)
        return Response(serializers.data)
    
    def update(self, request, pk=None):
        bookmark = self.queryset.get(pk=pk)
        serializers = self.serializer_class(bookmark, data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=400)
    
    def destroy(self, request, pk=None):
        bookmark = self.queryset.get(pk=pk)
        bookmark.delete()
        return Response(status=204)
    
class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
    def list(self, request):
        queryset = self.queryset
        serializers = self.serializer_class(queryset, many=True)
        return Response(serializers.data)
    
    def create(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=400)
    
    def retrieve(self, request, pk=None):
        event = self.queryset.get(pk=pk)
        serializers = self.serializer_class(event)
        return Response(serializers.data)
    
    def update(self, request, pk=None):
        event = self.queryset.get(pk=pk)
        serializers = self.serializer_class(event, data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=400)
    
    def destroy(self, request, pk=None):
        event = self.queryset.get(pk=pk)
        event.delete()
        return Response(status=204)
    
class JobApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer

    def get_queryset(self):
        return JobApplication.objects.all()
    
    def list(self, request):
        queryset = self.get_queryset()
        serializers = self.serializer_class(queryset, many=True)
        return Response(serializers.data)
    
    def create(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            graduate = serializers.validated_data.get("graduate")
            job  = serializers.validated_data.get("job")
            if JobApplication.objects.filter(graduate=graduate, job=job).exists():
                return Response({"error": "You have already applied for this job."}, status=400)
            serializers.save()
            for tag in job.tags:
                graduate.increment_tag_score(tag)

            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=400)
    
    def retrieve(self, request, pk=None):
        job_application = self.queryset.get(pk=pk)
        serializers = self.serializer_class(job_application)
        return Response(serializers.data)
    
    def update(self, request, pk=None):
        job_application = self.queryset.get(pk=pk)
        serializers = self.serializer_class(job_application, data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=400)
    
    def destroy(self, request, pk=None):
        job_application = self.queryset.get(pk=pk)
        job_application.delete()
        return Response(status=204)
    
class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = Resources.objects.all()
    serializer_class = ResourceSerializer
    
    def list(self, request):
        queryset = self.queryset
        serializers = self.serializer_class(queryset, many=True)
        return Response(serializers.data)
    
    def create(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=400)
    
    def retrieve(self, request, pk=None):
        resource = self.queryset.get(pk=pk)
        serializers = self.serializer_class(resource)
        return Response(serializers.data)
    
    def update(self, request, pk=None):
        resource = self.queryset.get(pk=pk)
        serializers = self.serializer_class(resource, data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data)
        else:
            return Response(serializers.errors, status=400)
    
    def destroy(self, request, pk=None):
        resource = self.queryset.get(pk=pk)
        resource.delete()
        return Response(status=204)