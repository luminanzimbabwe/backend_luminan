from rest_framework import serializers
from bson import ObjectId
from datetime import datetime


class DriverSerializer(serializers.Serializer):
    _id = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    operational_area = serializers.CharField()
    drivers_licence_number = serializers.CharField()
    valid_zimbabwe_id = serializers.CharField()
    bio = serializers.CharField()
    vehicle_number = serializers.CharField()
    vehicle_color = serializers.CharField()
    role = serializers.CharField()
    is_verified = serializers.BooleanField()
    verified_at = serializers.DateTimeField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
    last_login = serializers.DateTimeField(required=False, allow_null=True)
    # Add other fields as necessary from your driver document structure

    def to_representation(self, instance):
        # Convert ObjectId to string for _id field
        if '_id' in instance and isinstance(instance['_id'], ObjectId):
            instance['_id'] = str(instance['_id'])
        # Convert datetime objects to ISO format strings
        for key, value in instance.items():
            if isinstance(value, datetime):
                instance[key] = value.isoformat()
        return super().to_representation(instance)
