"""
project/urls.py
نقشه اصلی URL های کل پروژه
این فایل کارش وصل کردن آدرس‌ها به اپ calculator هست
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('calculator.urls')),  # همه آدرس‌های دیگه میره توی calculator/urls.py
]
