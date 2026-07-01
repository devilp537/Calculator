"""
calculator/models.py
مدل (ساختار جدول) دیتابیس برای ذخیره هیستوری محاسبات
"""

from django.db import models
from django.contrib.auth.models import User


class CalculationHistory(models.Model):
    # هر هیستوری متعلق به یه کاربر خاصه
    # وقتی کاربر حذف بشه، هیستوری‌هاش هم حذف میشن (CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')

    expression = models.CharField(max_length=255)  # مثلاً "2+2"
    result = models.CharField(max_length=255)       # مثلاً "4"

    created_at = models.DateTimeField(auto_now_add=True)  # زمان ذخیره، خودکار پر میشه

    class Meta:
        ordering = ['-created_at']  # جدیدترین‌ها اول نمایش داده بشن

    def __str__(self):
        return f"{self.user.username}: {self.expression} = {self.result}"
