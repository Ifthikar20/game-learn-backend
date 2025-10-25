from rest_framework import serializers
from .models import UserGame


class GameGenerateSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, max_length=500)


class UserGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGame
        fields = ['id', 'title', 'description', 'status', 'created_at']


class GamePlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGame
        fields = ['id', 'title', 'description', 'pixijs_code', 'game_data']