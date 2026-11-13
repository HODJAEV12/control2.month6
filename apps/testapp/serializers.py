from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        data['role'] = self.user.role
        return data

class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField(
        required=True, 
        help_text="Одноразовый code, полученный фронтендом от Google"
    )