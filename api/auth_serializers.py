#.backend/api/auth_serializers.py
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework import serializers
from core.models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from core.models import User, Graduate, Mentor, Employer

class RegisterSerializer(serializers.Serializer):
    ACCOUNT_TYPES = (
        ('graduate', 'Graduate'),
        ('mentor', 'Mentor'),
        ('employer', 'Employer'),
    )

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    account_type = serializers.ChoiceField(choices=ACCOUNT_TYPES)
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()

    # Graduate-specific
    degree = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=Graduate.GRADUATE_LEVELS, required=False)

    # Mentor-specific
    mentor_degree = serializers.CharField(required=False)
    biography = serializers.CharField(required=False)
  

    # Employer-specific
    address = serializers.CharField(required=False)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        account_type = data.get('account_type')
        if account_type == 'mentor':
            if not data.get('mentor_degree'):
                raise serializers.ValidationError("Mentor degree is required for mentors.")
        elif account_type == 'employer':
            if not data.get('address'):
                raise serializers.ValidationError("Address is required for employers.")

        return data

    def create(self, validated_data):
        account_type = validated_data.pop('account_type')
        password = validated_data.pop('password')
        validated_data.pop('password2')

        username = validated_data['username']
        email = validated_data['email']
        user = User.objects.create_user(username=username, email=email, password=password)

        if account_type == 'graduate':
            Graduate.objects.create(
                user=user,
                degree=validated_data.get('degree'),
                status=validated_data.get('status', 'UG'),
                longitude=validated_data.get('longitude'),
                latitude=validated_data.get('latitude'),
            )
        elif account_type == 'mentor':
            Mentor.objects.create(
                user=user,
                mentor_degree=validated_data.get('mentor_degree'),
                biography=validated_data.get('biography', ''),
                longitude=validated_data.get('longitude'),
                latitude=validated_data.get('latitude'),
            )
        elif account_type == 'employer':
            Employer.objects.create(
                user=user,
                address=validated_data.get('address'),
                biography=validated_data.get('biography', ''),
                longitude=validated_data.get('longitude'),
                latitude=validated_data.get('latitude'),
            )

        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        account_type = None
       
        if hasattr(self.user, 'graduate'):
            account_type = 'graduate'
            longitude = self.user.graduate.longitude
            latitude = self.user.graduate.latitude
            modelId = self.user.graduate.id


        elif hasattr(self.user, 'mentor'):
            account_type = 'mentor'
            longitude = self.user.mentor.longitude
            latitude = self.user.mentor.latitude
            modelId = self.user.mentor.id
            tags = []
        elif hasattr(self.user, 'employer'):
            account_type = 'employer'
            longitude = self.user.employer.longitude
            latitude = self.user.employer.latitude
            modelId = self.user.employer.id
            tags = []

            

        # Add extra user info to response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'account_type': account_type,
            'longitude': longitude,
            'latitude': latitude,
            'modelId': modelId,
        }
        return data
