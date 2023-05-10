from rest_framework import serializers


class HTTP_400(serializers.Serializer):
    error = serializers.CharField(max_length=150)