"""
calculator/views.py
"""

import json
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET

from .models import CalculationHistory

# ─── اعتبارسنجی عبارت ریاضی ──────────────────────────
SAFE_EXPRESSION = re.compile(r'^[0-9+\-*/.\s]+$')


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
            if user.is_superuser:
                return redirect('admin_panel')
            return redirect('calculator_home')
        else:
            return render(request, 'calculator/login.html', {'error': 'یوزرنیم یا رمز اشتباهه'})
    return render(request, 'calculator/login.html')


def logout_view(request):
    request.session.pop('selected_user_id', None)
    request.session.pop('selected_username', None)
    logout(request)
    return redirect('login')


@user_passes_test(lambda u: u.is_superuser)
def admin_panel_view(request):
    users = User.objects.exclude(is_superuser=True).order_by('username')
    selected_username = request.session.get('selected_username', None)
    return render(request, 'calculator/admin_panel.html', {
        'users': users,
        'selected_username': selected_username,
    })


@login_required
def select_user_view(request, user_id):
    if not request.user.is_superuser:
        return redirect('calculator_home')
    try:
        selected_user = User.objects.get(id=user_id)
        request.session['selected_user_id'] = selected_user.id
        request.session['selected_username'] = selected_user.username
    except User.DoesNotExist:
        pass
    return redirect('calculator_home')


@login_required
def calculator_view(request):
    selected_user_id = request.session.get('selected_user_id', None)
    is_admin_mode = False
    display_name = request.user.username

    if request.user.is_superuser and selected_user_id:
        try:
            target_user = User.objects.get(id=selected_user_id)
            history = CalculationHistory.objects.filter(user=target_user)[:50]
            display_name = f"{target_user.username}(admin)"
            is_admin_mode = True
        except User.DoesNotExist:
            history = CalculationHistory.objects.filter(user=request.user)[:50]
    else:
        history = CalculationHistory.objects.filter(user=request.user)[:50]

    return render(request, 'calculator/calculator.html', {
        'history': history,
        'display_name': display_name,
        'is_admin_mode': is_admin_mode,
    })


# ════════════════════════════
#  Helper
# ════════════════════════════

def _get_target_user(request):
    """برگرداندن کاربر هدف (ادمین یا کاربر انتخاب‌شده) و وضعیت ادمین بودن"""
    selected_user_id = request.session.get('selected_user_id', None)
    if request.user.is_superuser and selected_user_id:
        try:
            return User.objects.get(id=selected_user_id), True
        except User.DoesNotExist:
            pass
    return request.user, False


# ════════════════════════════
#  API endpoints
# ════════════════════════════

@login_required
@require_POST
def save_history_api(request):
    try:
        data = json.loads(request.body)
        expression = data.get('expression', '').strip()
        result = data.get('result', '').strip()

        if not expression or not result:
            return JsonResponse({'error': 'داده ناقصه'}, status=400)
        if not SAFE_EXPRESSION.match(expression):
            return JsonResponse({'error': 'عبارت نامعتبره'}, status=400)

        target_user, is_admin_mode = _get_target_user(request)

        # کاربری که عملیات رو انجام داده (همیشه request.user)
        performer = request.user

        # مقدار performed_by رو بر اساس انجام‌دهنده محاسبه کن
        if is_admin_mode:
            performed_by = f"{performer.username}(admin)"  # ادمین + پسوند
        else:
            performed_by = performer.username  # کاربر عادی

        history_item = CalculationHistory.objects.create(
            user=target_user,                # هیستوری به اسم این کاربر ثبت میشه
            expression=expression,
            result=result,
            performed_by=performed_by,       # انجام‌دهنده واقعی
        )

        return JsonResponse({
            'success': True,
            'id': history_item.id,
            'performed_by': performed_by,
            'created_at': history_item.created_at.strftime('%H:%M:%S'),
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'فرمت داده اشتباهه'}, status=400)


@login_required
@require_GET
def get_history_api(request):
    target_user, _ = _get_target_user(request)
    history = CalculationHistory.objects.filter(user=target_user)[:50]
    data = [
        {
            'id': h.id,
            'expression': h.expression,
            'result': h.result,
            'performed_by': h.performed_by,
            'created_at': h.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for h in history
    ]
    return JsonResponse({'history': data})


@login_required
@require_POST
def clear_history_api(request):
    target_user, _ = _get_target_user(request)
    CalculationHistory.objects.filter(user=target_user).delete()
    return JsonResponse({'success': True})


@login_required
def delete_last_history_api(request):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    target_user, _ = _get_target_user(request)
    last_item = CalculationHistory.objects.filter(user=target_user).first()

    if last_item:
        last_item.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'هیچ آیتمی برای حذف وجود ندارد'}, status=404)