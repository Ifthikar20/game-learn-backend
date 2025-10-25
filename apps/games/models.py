from django.db import models
from django.conf import settings
import uuid


class UserGame(models.Model):
    """Simplified game model for MVP"""
    
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Game details
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Generated content
    pixijs_code = models.TextField()
    game_data = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    user_prompt = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_games'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"