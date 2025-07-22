from django.urls import path 
from polls.views import ask, feedback, home


urlpatterns = [
    path('', home, name='home'),
    path("ask", ask, name="ask"),
    path("feedback", feedback, name="feedback")
]