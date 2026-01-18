from django.contrib.auth import get_user_model
from django.shortcuts import render

def ranking(request):
    User = get_user_model()
    users = User.objects.all().order_by("-total_score", "username")
    return render(request, "pages/ranking.html", {"users": users})
