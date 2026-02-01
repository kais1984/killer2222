from rest_framework import serializers
from core.models import User, CompanySettings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_active']


class CompanySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = '__all__'
