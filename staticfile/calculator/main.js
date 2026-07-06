'use strict';

function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return value;
    }
    return '';
}
const CSRF_TOKEN = getCSRFToken();

const displayEL = document.querySelector('.display');
const cleanBtnEL = document.querySelector('.cleanBtn');
const delBtnEL = document.querySelector('.delBtn');
const equalBtnEL = document.querySelector('.equalBtn');
const historyEL = document.querySelector('.history');
const cleanHistoryEL = document.querySelector('.cleanHistory');
const deleteLastBtn = document.querySelector('.deleteLastBtn');
const timer = 1500;

const displayUpdate = (element) => { displayEL.value += element.textContent; };
const cleanDisplay = () => { displayEL.value = ''; };
const removeClass = () => { displayEL.classList.remove('displayError'); };
const deleteDisplay = () => { displayEL.value = displayEL.value.slice(0, -1); };

async function saveToServer(expression, result) {
    try {
        const response = await fetch('/api/history/save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify({ expression, result }),
        });
        if (response.ok) {
            const data = await response.json();
            const lastItem = historyEL.querySelector('.operations:last-child');
            if (lastItem && data.performed_by) {
                const badge = data.performed_by.includes('(admin)')
                    ? `<span class="badge bg-warning text-dark ms-1">👑 ادمین</span>`
                    : '';
                lastItem.innerHTML += ` <small class="text-muted">(${data.performed_by})</small>${badge}`;
            }
        } else {
            console.error('ذخیره هیستوری ناموفق بود');
        }
    } catch (err) {
        console.error('خطا در اتصال به سرور:', err);
    }
}

async function clearServerHistory() {
    try {
        await fetch('/api/history/clear/', {
            method: 'POST',
            headers: { 'X-CSRFToken': CSRF_TOKEN },
        });
    } catch (err) {
        console.error('خطا در پاک کردن هیستوری:', err);
    }
}

async function deleteLastOperation() {
    const lastItem = document.querySelector('.history .operations:last-child');
    if (!lastItem) {
        console.log('هیچ آیتمی برای حذف وجود ندارد');
        return;
    }
    lastItem.remove();
    try {
        const response = await fetch('/api/history/delete-last/', {
            method: 'DELETE',
            headers: { 'X-CSRFToken': CSRF_TOKEN },
        });
        if (!response.ok) {
            const errorData = await response.json();
            console.error('خطا در حذف آخرین عملیات:', errorData.error);
        } else {
            await loadHistory();
        }
    } catch (err) {
        console.error('خطا در ارتباط با سرور:', err);
    }
}

async function loadHistory() {
    try {
        const response = await fetch('/api/history/');
        if (!response.ok) {
            console.error('دریافت تاریخچه ناموفق');
            return;
        }
        const data = await response.json();
        const historyEL = document.querySelector('.history');
        if (historyEL) {
            historyEL.innerHTML = '';
            data.history.forEach(item => {
                const li = document.createElement('li');
                li.className = 'operations';
                let badge = '';
                if (item.performed_by && item.performed_by.includes('(admin)')) {
                    badge = `<span class="badge bg-warning text-dark ms-1">👑 ادمین</span>`;
                }
                li.innerHTML = `${item.expression} = ${item.result} <small class="text-muted">(${item.performed_by || 'کاربر'})</small>${badge}`;
                historyEL.appendChild(li);
            });
        }
    } catch (err) {
        console.error('خطا در دریافت تاریخچه:', err);
    }
}

const cleanHistoryDisplay = async () => {
    document.querySelectorAll('.operations').forEach(op => op.remove());
    await clearServerHistory();
    await loadHistory();
};

const equalDisplay = function() {
    try {
        const primaryDisplay = displayEL.value;
        displayEL.value = eval(displayEL.value);
        const lastOperations = `<li class='operations'>${primaryDisplay} = ${displayEL.value}</li>`;
        historyEL.insertAdjacentHTML('beforeend', lastOperations);
        saveToServer(primaryDisplay, String(displayEL.value));
    } catch {
        displayEL.value = 'error';
        displayEL.classList.add('displayError');
        setTimeout(cleanDisplay, timer);
        setTimeout(removeClass, timer);
    }
};

cleanBtnEL.addEventListener('click', cleanDisplay);
delBtnEL.addEventListener('click', deleteDisplay);
equalBtnEL.addEventListener('click', equalDisplay);
cleanHistoryEL.addEventListener('click', cleanHistoryDisplay);
deleteLastBtn.addEventListener('click', deleteLastOperation);

document.addEventListener('DOMContentLoaded', loadHistory);
