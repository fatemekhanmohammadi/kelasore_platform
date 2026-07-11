// static/accounts/js/api.js
const API_BASE = 'http://127.0.0.1:8000';

const getToken = () => localStorage.getItem('access_token');
const getRefreshToken = () => localStorage.getItem('refresh_token');

const setToken = (tokens) => {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
};

const removeToken = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
};

// ===== درخواست با احراز هویت =====
async function fetchWithAuth(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };

    let response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        const refresh = getRefreshToken();
        if (refresh) {
            try {
                const res = await fetch(`${API_BASE}/api/token/refresh/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh })
                });
                
                if (res.ok) {
                    const data = await res.json();
                    setToken(data);
                    response = await fetch(`${API_BASE}${endpoint}`, {
                        ...options,
                        headers: {
                            ...headers,
                            'Authorization': `Bearer ${data.access}`
                        }
                    });
                } else {
                    removeToken();
                    window.location.href = '/login/';
                    throw new Error('Session expired');
                }
            } catch (error) {
                removeToken();
                window.location.href = '/login/';
                throw error;
            }
        } else {
            window.location.href = '/login/';
            throw new Error('No refresh token');
        }
    }
    
    return response;
}

// ===== API های احراز هویت =====
export const authAPI = {
    login: (username, password) => 
        fetch(`${API_BASE}/api/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        }),
    
    register: (userData) => 
        fetch(`${API_BASE}/api/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        }),
    
    profile: () => fetchWithAuth('/api/profile/'),
    updateProfile: (data) => fetchWithAuth('/api/profile/update/', {
        method: 'PUT',
        body: JSON.stringify(data)
    })
};

// ===== API های کلاس =====
export const classAPI = {
    list: () => fetchWithAuth('/classes/list/api/'),
    create: (data) => fetchWithAuth('/classes/create/', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    detail: (id) => fetchWithAuth(`/classes/detail/${id}/`),
    join: (id, password = null) => fetchWithAuth(`/classes/join/${id}/`, {
        method: 'POST',
        body: JSON.stringify({ password })
    }),
    leave: (id) => fetchWithAuth(`/classes/leave/${id}/`, {
        method: 'POST'
    }),
    members: (id) => fetchWithAuth(`/classes/${id}/members/`),
    invite: (id, username) => fetchWithAuth(`/classes/invite/${id}/`, {
        method: 'POST',
        body: JSON.stringify({ username })
    }),
    acceptInvite: (token) => fetchWithAuth('/classes/invite/accept/', {
        method: 'POST',
        body: JSON.stringify({ token })
    })
};

export { setToken, removeToken, getToken, getRefreshToken };

export const utils = {
    getToken,
    setToken,
    removeToken,
    getRefreshToken,
    fetchWithAuth
};