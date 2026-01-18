from django.shortcuts import render

def home(request):
    if request.user.is_authenticated:
        return render(request, "pages/main_logged_in.html")
    return render(request, "pages/main_logged_out.html")
