/**
 * Authentication JavaScript
 * 
 * Handles login, registration, and two-factor authentication.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if the user is already logged in
    const token = localStorage.getItem('dmac_token');
    if (token && !window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        // Redirect to dashboard
        window.location.href = '/dashboard';
    }
    
    // Toggle password visibility
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
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
        loginForm.addEventListener('submit', function(e) {
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
                // For demo purposes, check if this is a test account
                if (email === 'demo@example.com' && password === 'password') {
                    // Show 2FA modal for demo account
                    const twoFactorModal = new bootstrap.Modal(document.getElementById('twoFactorModal'));
                    twoFactorModal.show();
                    
                    // Focus on first OTP input
                    document.querySelector('.otp-input').focus();
                    
                    // Reset button
                    loginBtn.disabled = false;
                    loginBtn.textContent = originalText;
                } else if (email === 'user@example.com' && password === 'password') {
                    // Direct login for test account without 2FA
                    // Store token
                    const token = 'demo-token-' + Date.now();
                    localStorage.setItem('dmac_token', token);
                    
                    // Store user info
                    const userInfo = {
                        id: '1',
                        name: 'John Doe',
                        email: 'user@example.com',
                        avatar: '/static/img/user-avatar.png',
                        role: 'Administrator'
                    };
                    localStorage.setItem('dmac_user', JSON.stringify(userInfo));
                    
                    // Redirect to dashboard
                    window.location.href = '/dashboard';
                } else {
                    // Show error for invalid credentials
                    showToast('Error', 'Invalid email or password. Try demo@example.com / password (with 2FA) or user@example.com / password (without 2FA).');
                    
                    // Reset button
                    loginBtn.disabled = false;
                    loginBtn.textContent = originalText;
                }
            }, 1500);
        });
    }
    
    // Handle registration form submission
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            // Validate passwords match
            if (password !== confirmPassword) {
                showToast('Error', 'Passwords do not match.');
                return;
            }
            
            // Show loading state
            const registerBtn = document.getElementById('registerBtn');
            const originalText = registerBtn.textContent;
            registerBtn.disabled = true;
            registerBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating account...';
            
            // Simulate API call
            setTimeout(() => {
                // For demo purposes, always succeed
                showToast('Success', 'Account created successfully! You can now log in.');
                
                // Reset form
                registerForm.reset();
                
                // Redirect to login page after a delay
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            }, 1500);
        });
    }
    
    // Handle OTP input
    const otpInputs = document.querySelectorAll('.otp-input');
    if (otpInputs.length > 0) {
        otpInputs.forEach((input, index) => {
            // Auto-focus next input when a digit is entered
            input.addEventListener('input', function() {
                if (this.value.length === 1) {
                    // Move to next input
                    if (index < otpInputs.length - 1) {
                        otpInputs[index + 1].focus();
                    }
                }
            });
            
            // Handle backspace
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && this.value.length === 0) {
                    // Move to previous input
                    if (index > 0) {
                        otpInputs[index - 1].focus();
                    }
                }
            });
        });
        
        // Handle OTP verification
        const verifyOtpBtn = document.getElementById('verifyOtpBtn');
        if (verifyOtpBtn) {
            verifyOtpBtn.addEventListener('click', function() {
                // Get OTP value
                let otp = '';
                otpInputs.forEach(input => {
                    otp += input.value;
                });
                
                // Validate OTP length
                if (otp.length !== otpInputs.length) {
                    showToast('Error', 'Please enter all digits of the verification code.');
                    return;
                }
                
                // Show loading state
                const originalText = verifyOtpBtn.textContent;
                verifyOtpBtn.disabled = true;
                verifyOtpBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Verifying...';
                
                // Simulate API call
                setTimeout(() => {
                    // For demo purposes, check if OTP is 123456
                    if (otp === '123456') {
                        // Store token
                        const token = 'demo-token-' + Date.now();
                        localStorage.setItem('dmac_token', token);
                        
                        // Store user info
                        const userInfo = {
                            id: '2',
                            name: 'Demo User',
                            email: 'demo@example.com',
                            avatar: '/static/img/user-avatar.png',
                            role: 'User'
                        };
                        localStorage.setItem('dmac_user', JSON.stringify(userInfo));
                        
                        // Close modal
                        const twoFactorModal = bootstrap.Modal.getInstance(document.getElementById('twoFactorModal'));
                        twoFactorModal.hide();
                        
                        // Show success message
                        showToast('Success', 'Two-factor authentication successful!');
                        
                        // Redirect to dashboard after a delay
                        setTimeout(() => {
                            window.location.href = '/dashboard';
                        }, 1000);
                    } else {
                        // Show error for invalid OTP
                        showToast('Error', 'Invalid verification code. Try 123456 for demo.');
                        
                        // Reset button
                        verifyOtpBtn.disabled = false;
                        verifyOtpBtn.textContent = originalText;
                        
                        // Clear OTP inputs
                        otpInputs.forEach(input => {
                            input.value = '';
                        });
                        
                        // Focus on first input
                        otpInputs[0].focus();
                    }
                }, 1500);
            });
        }
    }
    
    // Handle social login buttons
    const socialButtons = document.querySelectorAll('.btn-social');
    socialButtons.forEach(button => {
        button.addEventListener('click', function() {
            const provider = this.textContent.trim().replace('Sign in with ', '');
            
            // Show loading state
            const originalText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Connecting...`;
            
            // Simulate API call
            setTimeout(() => {
                // For demo purposes, always succeed
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
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}
