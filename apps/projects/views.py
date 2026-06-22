from rest_framework import viewsets
from .models import Project, Recipe, AIModel
from .serializers import ProjectSerializer, RecipeSerializer, AIModelSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "status", "created_at"]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related("project").all()
    serializer_class = RecipeSerializer
    search_fields = ["name", "version", "project__code"]
    ordering_fields = ["name", "version", "created_at"]


class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.select_related("project").all()
    serializer_class = AIModelSerializer
    search_fields = ["name", "version", "framework", "project__code"]
    ordering_fields = ["name", "version", "status", "created_at"]
