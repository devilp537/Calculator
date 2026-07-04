'use strict'

const displayEL = document.querySelector('.display');
const cleanBtnEL = document.querySelector('.cleanBtn');
const delBtnEL = document.querySelector('.delBtn');
const equalBtnEL = document.querySelector('.equalBtn');
const historyEL = document.querySelector('.history');
const cleanHistoryEL = document.querySelector('.cleanHistory');
const deleteLastBtn = document.querySelector('.deleteLastBtn');
const timer = 1500


const displayUpdate = (element) => { displayEL.value += element.textContent };
const cleanDisplay = () => {displayEL.value = ""};
const removeClass = () => {displayEL.classList.remove('displayError')};
const deleteDisplay = () => {displayEL.value = displayEL.value.slice(0, -1)};


// ════════════════════════════
//  بخش جدید: ارتباط با Django
// ════════════════════════════

// ─── دریافت CSRF Token از کوکی ──────────────────────
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return value;
    }
    return '';
}
const CSRFToken = getCSRFToken();

// ذخیره یه محاسبه در دیتابیس (از طریق API جنگو)
async function saveToServer(expression, result) {
    try {
        const response = await fetch('/api/history/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN, // امنیت — جنگو بدون این، درخواست را رد می‌کنه
            },
            body: JSON.stringify({ expression, result }),
        });

        if (!response.ok) {
            console.error('ذخیره هیستوری ناموفق بود');
        }
    } catch (err) {
        // اگه اینترنت قطع بود یا سرور در دسترس نبود
        console.error('خطا در اتصال به سرور:', err);
    }
}

// پاک کردن کل هیستوری از دیتابیس
async function clearServerHistory() {
    try {
        await fetch('/api/history/clear/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
        });
    } catch (err) {
        console.error('خطا در پاک کردن هیستوری:', err);
    }
}

// ─── حذف آخرین عملیات از تاریخچه ────────────────────
async function deleteLastOperation() {
    // ۱. پیدا کردن آخرین آیتم تاریخچه در صفحه
    const lastItem = document.querySelector('.history .operations:last-child');
    
    // ۲. اگه هیچ آیتمی نبود، به کاربر بگو
    if (!lastItem) {
        console.log('⚠️ هیچ آیتمی برای حذف وجود ندارد');
        return;
    }

    // ۳. حذف از صفحه (DOM)
    lastItem.remove();

    // ۴. درخواست به سرور برای حذف آخرین آیتم از دیتابیس
    try {
        const response = await fetch('/api/history/delete-last/', {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': CSRF_TOKEN,
            },
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('❌ خطا در حذف آخرین عملیات:', errorData.error);
        } else {
            console.log('✅ آخرین عملیات با موفقیت حذف شد');
        }
    } catch (err) {
        console.error('❌ خطا در ارتباط با سرور:', err);
    }
}

// ════════════════════════════
//  منطق ماشین‌حساب (همون قبلی)
// ════════════════════════════

const cleanHistoryDisplay = () => {
    document.querySelectorAll('.operations').forEach(operation => {operation.remove()});
    clearServerHistory(); // اضافه شد: هیستوری سمت سرور هم پاک بشه
};

const equalDisplay = function() {
    try{
        const primaryDisplay = displayEL.value
        displayEL.value = eval(displayEL.value);
        const lastOperations = ` <li class = 'operations'>  ${primaryDisplay} = ${displayEL.value} </li> `
        historyEL.insertAdjacentHTML("beforeend",lastOperations);

        // اضافه شد: نتیجه را به Django بفرست تا ذخیره بشه
        saveToServer(primaryDisplay, String(displayEL.value));
    }
    catch{
        displayEL.value = 'error';
        displayEL.classList.add('displayError');
        setTimeout(cleanDisplay,timer);
        setTimeout(removeClass,timer);
    }

}


cleanBtnEL.addEventListener('click', cleanDisplay);
delBtnEL.addEventListener('click', deleteDisplay);
equalBtnEL.addEventListener('click', equalDisplay);
cleanHistoryEL.addEventListener('click', cleanHistoryDisplay);
deleteLastBtn.addEventListener('click', deleteLastOperation);