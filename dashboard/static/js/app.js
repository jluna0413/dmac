/**
 * DMac Dashboard JavaScript
 */

$(document).ready(function() {
    // Check if the user is logged in (except on the login page)
    if (window.location.pathname !== '/login') {
        const token = localStorage.getItem('dmac_token');
        if (!token) {
            // Redirect to login page
            window.location.href = '/login';
            return;
        }
    }
    
    // Handle logout
    $('#logoutLink').click(function(e) {
        e.preventDefault();
        logout();
    });
    
    // Set up AJAX defaults
    $.ajaxSetup({
        error: function(xhr, status, error) {
            // Check if the error is due to an expired token
            if (xhr.status === 401) {
                // Clear the token
                localStorage.removeItem('dmac_token');
                
                // Redirect to login page
                window.location.href = '/login';
            }
        }
    });
});

/**
 * Logout the user
 */
function logout() {
    const token = localStorage.getItem('dmac_token');
    
    if (!token) {
        // No token, just redirect to login page
        window.location.href = '/login';
        return;
    }
    
    // Send logout request
    $.ajax({
        url: '/api/auth/logout',
        type: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        success: function() {
            // Clear the token
            localStorage.removeItem('dmac_token');
            
            // Redirect to login page
            window.location.href = '/login';
        },
        error: function() {
            // Clear the token anyway
            localStorage.removeItem('dmac_token');
            
            // Redirect to login page
            window.location.href = '/login';
        }
    });
}

/**
 * Format a date from a timestamp
 * 
 * @param {number} timestamp - The timestamp in seconds
 * @returns {string} The formatted date
 */
function formatDate(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

/**
 * Format a duration in seconds
 * 
 * @param {number} seconds - The duration in seconds
 * @returns {string} The formatted duration
 */
function formatDuration(seconds) {
    if (!seconds) return '';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

/**
 * Get the CSS class for a status badge
 * 
 * @param {string} status - The status
 * @returns {string} The CSS class
 */
function getStatusBadgeClass(status) {
    switch (status) {
        case 'completed':
        case 'success':
            return 'bg-success';
        case 'running':
        case 'active':
            return 'bg-info';
        case 'pending':
            return 'bg-warning';
        case 'failed':
        case 'error':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

/**
 * Show a notification
 * 
 * @param {string} message - The message to show
 * @param {string} type - The type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Check if the notification container exists
    let container = $('#notificationContainer');
    if (container.length === 0) {
        // Create the container
        $('body').append('<div id="notificationContainer" style="position: fixed; top: 20px; right: 20px; z-index: 9999;"></div>');
        container = $('#notificationContainer');
    }
    
    // Create the notification
    const notification = $(`
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-delay="5000">
            <div class="toast-header bg-${type} text-white">
                <strong class="mr-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `);
    
    // Add the notification to the container
    container.append(notification);
    
    // Show the notification
    notification.toast('show');
    
    // Remove the notification when it's hidden
    notification.on('hidden.bs.toast', function() {
        notification.remove();
    });
}

/**
 * Copy text to clipboard
 * 
 * @param {string} text - The text to copy
 * @returns {boolean} Whether the copy was successful
 */
function copyToClipboard(text) {
    // Create a temporary textarea
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // Select and copy the text
    textarea.select();
    let success = false;
    try {
        success = document.execCommand('copy');
    } catch (err) {
        console.error('Error copying text to clipboard:', err);
    }
    
    // Remove the textarea
    document.body.removeChild(textarea);
    
    return success;
}

/**
 * Download data as a file
 * 
 * @param {string} filename - The name of the file
 * @param {string} data - The data to download
 * @param {string} type - The MIME type of the file
 */
function downloadFile(filename, data, type = 'text/plain') {
    const blob = new Blob([data], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
