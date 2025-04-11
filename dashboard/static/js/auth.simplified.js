/**
 * Authentication JavaScript
 *
 * Handles login, registration, and two-factor authentication.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Check if the user is already logged in
    const token = localStorage.getItem('dmac_token');
    if (token && !window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        // Redirect to dashboard
        window.location.href = '/dashboard';
    }

    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function () {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);

            // Toggle icon
            const icon = this.querySelector('i');
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
        });
    });

    // Handle login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('rememberMe').checked;

            // Show loading state
            const loginBtn = document.getElementById('loginBtn');
            const originalText = loginBtn.textContent;
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Signing in...';

            // Simulate API call
            setTimeout(() => {
                // Store token
                const token = `user-token-${Date.now()}`;
                localStorage.setItem('dmac_token', token);

                // Store user info
                const userInfo = {
                    id: '1',
                    name: 'Demo User',
                    email: email,
                    avatar: '/static/img/user-avatar.png',
                    role: 'User'
                };
                localStorage.setItem('dmac_user', JSON.stringify(userInfo));

                // Show success message
                showToast('Success', 'Successfully signed in!');

                // Redirect to dashboard after a delay
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            }, 1500);
        });
    }

    // Handle registration form submission
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            const termsAgreement = document.getElementById('termsAgreement').checked;

            // Validate passwords match
            if (password !== confirmPassword) {
                showToast('Error', 'Passwords do not match.');
                return;
            }

            // Validate terms agreement
            if (!termsAgreement) {
                showToast('Error', 'You must agree to the Terms of Service and Privacy Policy.');
                return;
            }

            // Show loading state
            const registerBtn = document.getElementById('registerBtn');
            const originalText = registerBtn.textContent;
            registerBtn.disabled = true;
            registerBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating account...';

            // Simulate API call
            setTimeout(() => {
                // Store token
                const token = `user-token-${Date.now()}`;
                localStorage.setItem('dmac_token', token);

                // Store user info
                const userInfo = {
                    id: '1',
                    name: name,
                    email: email,
                    avatar: '/static/img/user-avatar.png',
                    role: 'User'
                };
                localStorage.setItem('dmac_user', JSON.stringify(userInfo));

                // Show success message
                showToast('Success', 'Account created successfully!');

                // Redirect to dashboard after a delay
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            }, 1500);
        });
    }

    // Handle social login buttons
    const socialButtons = document.querySelectorAll('.btn-social');
    socialButtons.forEach(button => {
        button.addEventListener('click', function () {
            const provider = this.textContent.trim().replace('Sign in with ', '').replace('Sign up with ', '');

            // Show loading state
            const originalText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Connecting...`;

            // Simulate API call
            setTimeout(() => {
                // Store token
                const token = `${provider.toLowerCase()}-token-${Date.now()}`;
                localStorage.setItem('dmac_token', token);

                // Store user info
                const userInfo = {
                    id: '3',
                    name: `${provider} User`,
                    email: `${provider.toLowerCase()}user@example.com`,
                    avatar: '/static/img/user-avatar.png',
                    role: 'User'
                };
                localStorage.setItem('dmac_user', JSON.stringify(userInfo));

                // Show success message
                showToast('Success', `Successfully signed in with ${provider}!`);

                // Redirect to dashboard after a delay
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            }, 1500);
        });
    });
});

/**
 * Show a toast notification
 * @param {string} title - The toast title
 * @param {string} message - The toast message
 */
function showToast(title, message) {
    // Create toast container if it doesn't exist
    if (!document.querySelector('.toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Create toast
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    document.querySelector('.toast-container').insertAdjacentHTML('beforeend', toastHTML);

    // Show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();
}
