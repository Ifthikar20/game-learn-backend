from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import UserGame
from ..serializers import (
    GameGenerateSerializer,
    UserGameSerializer,
    GamePlaySerializer
)
from apps.ai_engine.generators.simple_generator import SimpleGameGenerator


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_game(request):
    """Generate a new game"""
    serializer = GameGenerateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    prompt = serializer.validated_data['prompt']
    
    # Create game with 'generating' status
    user_game = UserGame.objects.create(
        user=request.user,
        title="Generating...",
        description="Game is being generated",
        pixijs_code="",
        user_prompt=prompt,
        status='generating'
    )
    
    # Generate game (synchronous for MVP, can be async later)
    try:
        generator = SimpleGameGenerator()
        result = generator.generate_quiz_game(prompt)
        
        # Update game with generated content
        user_game.title = result['title']
        user_game.description = result['description']
        user_game.pixijs_code = result['pixijs_code']
        user_game.game_data = result['game_data']
        user_game.status = 'ready'
        user_game.save()
        
    except Exception as e:
        user_game.status = 'failed'
        user_game.description = f"Generation failed: {str(e)}"
        user_game.save()
    
    return Response({
        'success': True,
        'data': UserGameSerializer(user_game).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_games(request):
    """List user's games"""
    games = UserGame.objects.filter(user=request.user)
    serializer = UserGameSerializer(games, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def play_game(request, game_id):
    """Get game code to play"""
    game = get_object_or_404(UserGame, id=game_id, user=request.user)
    
    if game.status != 'ready':
        return Response({
            'success': False,
            'message': f'Game is not ready. Status: {game.status}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = GamePlaySerializer(game)
    return Response({
        'success': True,
        'data': serializer.data
    })