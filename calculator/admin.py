"""
calculator/admin.py
نمایش مدل‌ها توی پنل ادمین جنگو (مسیر /admin/)
برای اینکه بتونی هیستوری کاربرا را از پنل ادمین هم ببینی
"""

from django.contrib import admin
from .models import CalculationHistory


@admin.register(CalculationHistory)
class CalculationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'expression', 'result', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('expression', 'result', 'performed_by')