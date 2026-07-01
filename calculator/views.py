"""
calculator/views.py
منطق صفحات:
- لاگین / ثبت‌نام / خروج
- صفحه اصلی ماشین‌حساب
- API برای ذخیره و خوندن هیستوری
"""

import json
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import CalculationHistory


# ════════════════════════════
#  صفحات HTML
# ════════════════════════════

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            return render(request, 'calculator/register.html', {'error': 'همه فیلدها را پر کن'})

        if User.objects.filter(username=username).exists():
            return render(request, 'calculator/register.html', {'error': 'این یوزرنیم قبلاً گرفته شده'})

        # ساخت کاربر جدید — جنگو خودش رمز را هش می‌کنه (امن)
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('calculator_home')

    return render(request, 'calculator/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('calculator_home')
        else:
            return render(request, 'calculator/login.html', {'error': 'یوزرنیم یا رمز اشتباهه'})

    return render(request, 'calculator/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required  # فقط کاربر لاگین‌کرده می‌تونه این صفحه را ببینه
def calculator_view(request):
    # هیستوری همین کاربر را از دیتابیس می‌خونیم
    history = CalculationHistory.objects.filter(user=request.user)[:50]  # فقط ۵۰ تای آخر
    return render(request, 'calculator/calculator.html', {'history': history})


# ════════════════════════════
#  API endpoints (برای JS)
# ════════════════════════════

# regex ساده برای اینکه expression فقط شامل عدد و عملگرهای مجاز باشه
SAFE_EXPRESSION = re.compile(r'^[0-9+\-*/.\s]+$')


@login_required
@require_POST
def save_history_api(request):
    """
    JS بعد از هر محاسبه موفق، اینجا را صدا می‌زنه تا هیستوری ذخیره بشه
    """
    try:
        data = json.loads(request.body)
        expression = data.get('expression', '').strip()
        result = data.get('result', '').strip()

        # اعتبارسنجی ساده — فقط عدد و عملگر مجازه، نه کد دلخواه
        if not expression or not result:
            return JsonResponse({'error': 'داده ناقصه'}, status=400)

        if not SAFE_EXPRESSION.match(expression):
            return JsonResponse({'error': 'عبارت نامعتبره'}, status=400)

        history_item = CalculationHistory.objects.create(
            user=request.user,
            expression=expression,
            result=result,
        )

        return JsonResponse({
            'success': True,
            'id': history_item.id,
            'created_at': history_item.created_at.strftime('%H:%M:%S'),
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت داده اشتباهه'}, status=400)


@login_required
@require_GET
def get_history_api(request):
    """
    گرفتن هیستوری کاربر لاگین‌شده (برای لود اولیه صفحه با fetch، اگه لازم شد)
    """
    history = CalculationHistory.objects.filter(user=request.user)[:50]
    data = [
        {
            'id': h.id,
            'expression': h.expression,
            'result': h.result,
            'created_at': h.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for h in history
    ]
    return JsonResponse({'history': data})


@login_required
@require_POST
def clear_history_api(request):
    """
    پاک کردن کل هیستوری کاربر لاگین‌شده
    """
    CalculationHistory.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True})
