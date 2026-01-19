from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# 커스텀 유저 모델을 관리자 페이지에 등록
admin.site.register(User, UserAdmin)