from rest_framework import serializers
from .models import User

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["mobile", "first_name", "last_name", "email", "role", "is_active", "created_at"]
        read_only_fields = ["mobile", "role", "is_active", "created_at"]
