from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

app_name = 'parser_app'

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view())
]