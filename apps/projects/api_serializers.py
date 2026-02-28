from rest_framework import serializers
from .models import Project

class PublicProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    zip_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "short_desc", "content",
            "youtube_url", "image_url", "zip_url",
            "published_at", "coding_env_note",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_zip_url(self, obj):
        request = self.context.get("request")
        if obj.code_zip and request:
            return request.build_absolute_uri(obj.code_zip.url)
        return None