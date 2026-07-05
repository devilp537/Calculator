"""
calculator/urls.py
نقشه آدرس‌های مربوط به اپ calculator
"""

from django.urls import path
from . import views

urlpatterns = [
    # صفحات
    path('', views.calculator_view, name='calculator_home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # پنل ادمین (جدید)
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('admin-panel/select/<int:user_id>/', views.select_user_view, name='select_user'),


    # API
    path('api/history/save/', views.save_history_api, name='save_history_api'),
    path('api/history/', views.get_history_api, name='get_history_api'),
    path('api/history/clear/', views.clear_history_api, name='clear_history_api'),
    path('api/history/delete-last/', views.delete_last_history_api, name='delete_last_history_api'),
]
