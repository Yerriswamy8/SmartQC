from rest_framework import serializers
from .models import Project, Recipe, AIModel


class ProjectSerializer(serializers.ModelSerializer):
    recipe_count = serializers.IntegerField(source="recipes.count", read_only=True)
    model_count = serializers.IntegerField(source="models.count", read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    project_code = serializers.CharField(source="project.code", read_only=True)

    class Meta:
        model = Recipe
        fields = "__all__"


class AIModelSerializer(serializers.ModelSerializer):
    project_code = serializers.CharField(source="project.code", read_only=True)

    class Meta:
        model = AIModel
        fields = "__all__"
