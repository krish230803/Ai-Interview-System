const API_BASE_URL = 'http://localhost:5000';

// Common fetch options with proper CORS settings
const fetchOptions = {
    credentials: 'include',
    mode: 'cors',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// Helper functions
function showError(message) {
    console.error('Error:', message);  // Add console logging for debugging
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 5000);
    }
}

function validatePassword(password) {
    return password.length >= 8;
}

// Login form handler
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        // Clear any previous messages
        const errorDiv = document.getElementById('error-message');
        const successDiv = document.getElementById('success-message');
        if (errorDiv) errorDiv.style.display = 'none';
        if (successDiv) successDiv.style.display = 'none';

        if (!email || !password) {
            showError('Email and password are required');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                ...fetchOptions,
                method: 'POST',
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Invalid email or password');
            }

            // Store user data only after successful login
            localStorage.setItem('user', JSON.stringify(data.user));
            
            showSuccess('Login successful! Redirecting...');

            // Redirect after successful login
            setTimeout(() => {
                const redirectUrl = localStorage.getItem('redirectAfterLogin');
                if (redirectUrl) {
                    localStorage.removeItem('redirectAfterLogin');
                    window.location.href = redirectUrl;
                } else {
                    window.location.href = 'index.html';
                }
            }, 1500);
        } catch (error) {
            console.error('Login error:', error);
            showError(error.message || 'Invalid email or password');
        }
    });
}

// Registration form handler
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    console.log('Registration form found');
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Registration form submitted');
        
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        // Validation
        if (!name || !email || !password || !confirmPassword) {
            showError('All fields are required');
            return;
        }

        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }

        if (!validatePassword(password)) {
            showError('Password must be at least 8 characters long');
            return;
        }

        try {
            console.log('Sending registration request...');
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                ...fetchOptions,
                method: 'POST',
                body: JSON.stringify({ name, email, password })
            });

            const data = await response.json();
            console.log('Registration response:', data);
            
            if (!response.ok) {
                throw new Error(data.error || 'Registration failed');
            }

            showSuccess('Registration successful! Please log in with your credentials.');

            // Remove any stored user data
            localStorage.removeItem('user');
            
            // Redirect to login page after a short delay
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } catch (error) {
            console.error('Registration error:', error);
            showError(error.message || 'Network error occurred. Please try again.');
        }
    });
} else {
    console.error('Registration form not found!');
}

// Forgot password form handler
const forgotPasswordForm = document.getElementById('forgot-password-form');
if (forgotPasswordForm) {
    forgotPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;

        try {
            const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
                ...fetchOptions,
                method: 'POST',
                body: JSON.stringify({ email })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to send reset link');
            }

            // Handle development mode response
            if (data.reset_url) {
                showSuccess('Development mode: Click the button below to reset your password');
                const resetButton = document.createElement('a');
                resetButton.href = data.reset_url;
                resetButton.className = 'btn btn-primary mt-3 d-block';
                resetButton.textContent = 'Reset Password';
                document.getElementById('success-message').appendChild(resetButton);
            } else {
                showSuccess('Password reset instructions have been sent to your email.');
            }
        } catch (error) {
            showError(error.message);
        }
    });
}

// Reset password form handler
const resetPasswordForm = document.getElementById('reset-password-form');
if (resetPasswordForm) {
    // Get token from URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
        document.getElementById('reset-token').value = token;
    }

    resetPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const token = document.getElementById('reset-token').value;

        if (password !== confirmPassword) {
            showError('Passwords do not match');
            return;
        }

        if (!validatePassword(password)) {
            showError('Password must be at least 8 characters long');
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/reset-password/${token}`, {
                ...fetchOptions,
                method: 'POST',
                body: JSON.stringify({ password })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to reset password');
            }

            showSuccess('Password has been reset successfully!');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 3000);
        } catch (error) {
            showError(error.message);
        }
    });
}

// Check authentication status
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            ...fetchOptions,
            method: 'GET'
        });

        if (!response.ok) {
            throw new Error('Not authenticated');
        }

        const data = await response.json();
        localStorage.setItem('user', JSON.stringify(data.user));
        return data.user;
    } catch (error) {
        console.error('Auth check error:', error);
        localStorage.removeItem('user');
        return null;
    }
}

// Protect routes that require authentication
async function protectRoute() {
    const publicPages = ['index.html', 'login.html', 'register.html', 'forgot-password.html', 'reset-password.html'];
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // If it's a public page, no need to check authentication
    if (publicPages.includes(currentPage)) {
        return;
    }
    
    try {
        const user = await checkAuth();
        if (!user && !publicPages.includes(currentPage)) {
            window.location.href = 'login.html';
        }
        return user;
    } catch (error) {
        if (!publicPages.includes(currentPage)) {
            window.location.href = 'login.html';
        }
    }
}

// Initialize authentication check
document.addEventListener('DOMContentLoaded', () => {
    protectRoute();
});

// Update user info display function
function updateUserInfo(user) {
    const userInfoElement = document.getElementById('userInfo');
    if (userInfoElement && user) {
        userInfoElement.textContent = `Welcome, ${user.name}!`;
    }
}

// Update navbar user display
function updateNavbar(user) {
    const userEmailSpan = document.getElementById('userEmail');
    if (userEmailSpan && user) {
        userEmailSpan.textContent = user.name;
    }
} 