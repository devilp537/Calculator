# Django Calculator — فایل مرجع

این یه نسخه آماده‌ست تا بدونی پروژه نهایی چه شکلیه.
وقتی قدم‌به‌قدم با هم پیش رفتیم، خودت این فایل‌ها را از صفر می‌سازی.

## ساختار پروژه

```
django-calculator/
├── manage.py                          ← فرمان‌های جنگو از اینجا اجرا میشن
├── requirements.txt                   ← لیست پکیج‌های لازم
├── project/                           ← تنظیمات اصلی پروژه
│   ├── settings.py                    ← تنظیمات (دیتابیس، اپ‌ها، ...)
│   ├── urls.py                        ← نقشه کلی آدرس‌ها
│   └── wsgi.py
└── calculator/                        ← اپ اصلی
    ├── models.py                      ← مدل CalculationHistory
    ├── views.py                       ← منطق لاگین/ثبت‌نام/ماشین‌حساب/API
    ├── urls.py                        ← آدرس‌های مخصوص این اپ
    ├── admin.py                       ← نمایش در پنل ادمین
    ├── templates/calculator/
    │   ├── base.html                  ← قالب پایه (بوت‌استرپ لینک شده)
    │   ├── login.html
    │   ├── register.html
    │   └── calculator.html            ← همون HTML قبلی‌ت، با اضافات
    └── static/calculator/
        ├── main.css                   ← همون CSS قبلی‌ت
        └── main.js                    ← همون JS قبلی‌ت + اتصال به Django

```

## چطور اجرا میشه (وقتی آماده بودی)

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # اختیاری، برای پنل ادمین
python manage.py runserver
```

بعد برو به `http://127.0.0.1:8000/`

## نکات مهم برای وقتی قدم‌به‌قدم پیش می‌ریم

1. **models.py** — اینجا تعریف میشه هر هیستوری به کدوم کاربر وصله (`ForeignKey`)
2. **views.py** — هر تابع یه صفحه یا یه API رو مدیریت می‌کنه
3. **CSRF Token** — جنگو برای امنیت، یه توکن می‌خواد که توی `main.js` با هر `fetch` فرستاده میشه
4. **`@login_required`** — این decorator روی توابع views.py باعث میشه فقط کاربر لاگین‌کرده بتونه ببینتشون
5. **eval() در main.js** — همون قبلیه؛ چون محاسبه کاملاً سمت کلاینته و سمت سرور هم expression با regex چک میشه، امن نگه داشته شده
