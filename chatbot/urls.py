# chatbot/urls.py
from django.urls import path, include, views
from .views import chatbot_reply

urlpatterns = [
    path("", include("chatbot.urls")),
    path("chatbot/reply/", chatbot_reply, name="chatbot_reply"),
    

    
]
