# Register your models here.

from django.contrib import admin
from .models import ChatLog, FeedBack

@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question_preview', 'answer_preview', 'timestamp', 'feedback_count')
    list_filter = ('timestamp', 'user')
    search_fields = ('question', 'answer')
    readonly_fields = ('timestamp',)
    
    def question_preview(self, obj):
        return obj.question[:100] + "..." if len(obj.question) > 100 else obj.question
    question_preview.short_description = "Question Preview"
    
    def answer_preview(self, obj):
        return obj.answer[:100] + "..." if len(obj.answer) > 100 else obj.answer
    answer_preview.short_description = "Answer Preview"
    
    def feedback_count(self, obj):
        return obj.feedbacks.count()
    feedback_count.short_description = "Feedback Count"

@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('id', 'chatlog_id', 'user', 'feedback_type', 'timestamp', 'question_preview', 'answer_preview')
    list_filter = ('feedback_type', 'timestamp', 'user')
    search_fields = ('chatlog__question', 'chatlog__answer')
    readonly_fields = ('timestamp',)
    
    def chatlog_id(self, obj):
        return obj.chatlog.id
    chatlog_id.short_description = "ChatLog ID"
    
    def question_preview(self, obj):
        return obj.chatlog.question[:50] + "..." if len(obj.chatlog.question) > 50 else obj.chatlog.question
    question_preview.short_description = "Question Preview"

    def answer_preview(self, obj):
        return obj.chatlog.answer[:50] + "..." if len(obj.chatlog.answer) > 50 else obj.chatlog.answer
    answer_preview.short_description = "Answer Preview"