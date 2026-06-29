// ============================================================
// مدیریت احراز هویت با JWT - کالسور
// ============================================================

const API = {
    REGISTER: '/api/register/',
    LOGIN: '/api/token/',
    REFRESH: '/api/token/refresh/',
    PROFILE_UPDATE: '/api/profile/update/',
};

// ============================================================
// ثبت‌نام
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.querySelector('#register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    const profileForm = document.querySelector('#profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', handleProfileUpdate);
    }
});

async function handleRegister(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    
    // گرفتن داده‌ها
    const data = {
        first_name: form.querySelector('#first_name')?.value || '',
        last_name: form.querySelector('#last_name')?.value || '',
        username: form.querySelector('#username').value,
        email: form.querySelector('#email').value,
        password: form.querySelector('#password').value,
    };

    // اعتبارسنجی
    if (!data.username || data.username.length < 4) {
        showMessage('نام کاربری حداقل ۴ کاراکتر باشد', 'error');
        return;
    }
    if (!data.password || data.password.length < 6) {
        showMessage('رمز عبور حداقل ۶ کاراکتر باشد', 'error');
        return;
    }

    // غیرفعال کردن دکمه
    btn.disabled = true;
    btn.textContent = 'در حال ثبت‌نام...';

    try {
        const response = await fetch(API.REGISTER, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            // ذخیره توکن‌ها
            saveTokens(result.access, result.refresh);
            saveUser(result.user);
            
            showMessage('✅ ثبت‌نام با موفقیت انجام شد!', 'success');
            
            setTimeout(() => {
                window.location.href = '/dashboard/';
            }, 1500);
        } else {
            const errorMsg = extractErrors(result);
            showMessage('❌ ' + errorMsg, 'error');
            btn.disabled = false;
            btn.textContent = 'ثبت‌نام';
        }
    } catch (error) {
        showMessage('❌ خطا در ارتباط با سرور', 'error');
        btn.disabled = false;
        btn.textContent = 'ثبت‌نام';
    }
}

// ============================================================
// ورود
// ============================================================
async function handleLogin(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    
    const data = {
        username: form.querySelector('#username').value,
        password: form.querySelector('#password').value,
    };

    if (!data.username || !data.password) {
        showMessage('لطفاً نام کاربری و رمز عبور را وارد کنید', 'error');
        return;
    }

    btn.disabled = true;
    btn.textContent = 'در حال ورود...';

    try {
        const response = await fetch(API.LOGIN, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            // ذخیره توکن‌ها
            saveTokens(result.access, result.refresh);
            
            // اگه اطلاعات کاربر برگشت (با CustomTokenObtainPairView)
            if (result.user) {
                saveUser(result.user);
            }
            
            showMessage('✅ خوش آمدید!', 'success');
            
            setTimeout(() => {
                window.location.href = '/dashboard/';
            }, 1000);
        } else {
            const errorMsg = result.detail || 'نام کاربری یا رمز عبور اشتباه است';
            showMessage('❌ ' + errorMsg, 'error');
            btn.disabled = false;
            btn.textContent = 'ورود';
        }
    } catch (error) {
        showMessage('❌ خطا در ارتباط با سرور', 'error');
        btn.disabled = false;
        btn.textContent = 'ورود';
    }
}

// ============================================================
// ویرایش پروفایل
// ============================================================
async function handleProfileUpdate(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');

    // گرفتن داده‌ها — پسورد فقط اگه پر شده باشه فرستاده می‌شود
    const data = {
        first_name: form.querySelector('#first_name')?.value || '',
        last_name: form.querySelector('#last_name')?.value || '',
        email: form.querySelector('#email')?.value || '',
    };
    const passwordValue = form.querySelector('#password')?.value || '';
    if (passwordValue) {
        data.password = passwordValue;
    }

    btn.disabled = true;
    btn.textContent = 'در حال ذخیره...';

    try {
        // fetchWithAuth خودش هدر Authorization و رفرش خودکار توکن را مدیریت می‌کند
        const response = await fetchWithAuth(API.PROFILE_UPDATE, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });

        const result = await response.json();

        if (response.ok) {
            // به‌روزرسانی اطلاعات کاربر در localStorage
            saveUser(result);

            // خالی کردن فیلد پسورد بعد از ذخیره موفق
            const passwordField = form.querySelector('#password');
            if (passwordField) passwordField.value = '';
            showMessage('✅ تغییرات با موفقیت ذخیره شد', 'success', form);
        } else {
            const errorMsg = extractErrors(result);
            showMessage('❌ ' + errorMsg, 'error', form);
        }
    } catch (error) {
        showMessage('❌ خطا در ارتباط با سرور', 'error', form);
    } finally {
        btn.disabled = false;
        btn.textContent = 'ذخیره تغییرات';
    }
}

// ============================================================
// رفرش توکن (وقتی منقضی شد)
// ============================================================
 async function refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) {
        redirectToLogin();
        return null;
    }

    try {
        const response = await fetch(API.REFRESH, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh }),
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('access_token', data.access);
            return data.access;
        } else {
            redirectToLogin();
            return null;
        }
    } catch (error) {
        redirectToLogin();
        return null;
    }
}

// ============================================================
// درخواست با احراز هویت (خودکار رفرش می‌کنه)
// ============================================================
 async function fetchWithAuth(url, options = {}) {
    let token = localStorage.getItem('access_token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    let response = await fetch(url, {
        ...options,
        headers,
    });

    // اگر توکن منقضی شده بود، رفرش کن
    if (response.status === 401) {
        const newToken = await refreshToken();
        if (newToken) {
            headers['Authorization'] = `Bearer ${newToken}`;
            response = await fetch(url, {
                ...options,
                headers,
            });
        }
    }

    return response;
}

// ============================================================
// توابع کمکی
// ============================================================

function saveTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
}

function saveUser(user) {
    localStorage.setItem('user', JSON.stringify(user));
}

function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function redirectToLogin() {
    localStorage.clear();
    window.location.href = '/login/';
}

function extractErrors(data) {
    if (typeof data === 'string') return data;
    if (data.detail) return data.detail;
    if (data.non_field_errors) return data.non_field_errors.join('، ');
    
    const messages = [];
    for (const [field, errors] of Object.entries(data)) {
        if (Array.isArray(errors)) {
            messages.push(`${field}: ${errors.join('، ')}`);
        } else if (typeof errors === 'string') {
            messages.push(`${field}: ${errors}`);
        }
    }
    return messages.join(' | ') || 'خطای ناشناخته';
}

function showMessage(text, type = 'info', targetForm = null) {
    // حذف پیام قبلی
    const oldMsg = document.querySelector('.auth-message');
    if (oldMsg) oldMsg.remove();

    const msg = document.createElement('div');
    msg.className = `auth-message auth-message-${type}`;
    msg.textContent = text;
    
    const colors = {
        success: { bg: 'var(--success-bg, #d4edda)', color: 'var(--success, #155724)', border: 'var(--success, #28a745)' },
        error: { bg: 'var(--danger-bg, #f8d7da)', color: 'var(--danger, #721c24)', border: 'var(--danger, #dc3545)' },
        info: { bg: 'var(--info-bg, #d1ecf1)', color: 'var(--info, #0c5460)', border: 'var(--info, #17a2b8)' },
    };
    
    const style = colors[type] || colors.info;
    msg.style.cssText = `
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 18px;
        font-size: 14px;
        font-weight: 500;
        background: ${style.bg};
        color: ${style.color};
        border-right: 4px solid ${style.border};
        animation: slideDown 0.3s ease-out;
    `;
    
    const form = targetForm || document.querySelector('form');
    if (form) {
        form.parentNode.insertBefore(msg, form);
    }
}

// ============================================================
// چک کردن وضعیت لاگین (برای صفحات محافظت شده)
// ============================================================
 function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        redirectToLogin();
        return false;
    }
    return true;
}

// ============================================================
// خروج از حساب کاربری
// ============================================================
 function logout() {
    localStorage.clear();
    window.location.href = '/login/';
}

// ============================================================
// استایل انیمیشن (یکبار اضافه میشه)
// ============================================================
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(styleSheet);