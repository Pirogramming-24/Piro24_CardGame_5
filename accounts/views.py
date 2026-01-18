# accounts/views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model

def ranking(request):
    User = get_user_model()
    users = User.objects.all().order_by("-total_score", "username")
    return render(request, "pages/ranking.html", {"users": users})