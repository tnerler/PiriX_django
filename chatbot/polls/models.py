from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ChatLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return f"Q: {self.question[:50]}... A: {self.answer[:50]}..."

class FeedBack(models.Model):
    chatlog = models.ForeignKey(ChatLog, on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    feedback_type = models.CharField(max_length=10, choices=[("like", "Like"), ("dislike", "Dislike")])
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        unique_together = ("chatlog", "user")

    def __str__(self):
        return f"{self.user} gave {self.feedback_type} on Q:{self.chatlog.id}"
    