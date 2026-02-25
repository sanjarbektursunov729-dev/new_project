from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Project
from .api_serializers import PublicProjectSerializer

@api_view(["GET"])
def public_projects_list(request):
    qs = Project.objects.filter(status=Project.Status.PUBLISHED).order_by("-published_at")
    ser = PublicProjectSerializer(qs, many=True, context={"request": request})
    return Response(ser.data)

@api_view(["GET"])
def public_projects_detail(request, pk: int):
    obj = get_object_or_404(Project, pk=pk, status=Project.Status.PUBLISHED)
    ser = PublicProjectSerializer(obj, context={"request": request})
    return Response(ser.data)