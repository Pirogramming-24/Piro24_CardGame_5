from django.urls import path
from . import views
from allauth.account.views import LoginView

app_name = 'accounts'

urlpatterns = [
    # 127.0.0.1:8000/accounts/ranking/ 으로 접속
    path('ranking/', views.ranking, name='ranking'),
    path('login/', LoginView.as_view(template_name='pages/login.html'), name='login'),
]