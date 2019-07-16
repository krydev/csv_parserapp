from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

app_name = 'parser_app'

urlpatterns = [
    path('', views.UploaderView.as_view()),
    path('results/', views.results, name='results'),
    path('login/', LoginView.as_view(
            template_name='login.html',
            redirect_authenticated_user=True,
            extra_context={'next': '/', 'title': 'Login'}
        )),
    path('logout/', LogoutView.as_view(next_page='/login'))
]