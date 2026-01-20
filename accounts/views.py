from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render

@login_required
def ranking(request):
    User = get_user_model()
    users = User.objects.order_by("-total_score", "id")  # total_score 필드 있다는 전제
    return render(request, "accounts/ranking.html", {"users": users})
