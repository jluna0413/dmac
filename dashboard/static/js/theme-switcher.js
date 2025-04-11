/**
 * Theme Switcher for DMac Dashboard
 * Handles switching between light and dark themes
 */

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    setupThemeToggle();
});

/**
 * Initialize the theme based on user preference or system preference
 */
function initializeTheme() {
    // Check if user has a saved preference
    const savedTheme = localStorage.getItem('dmac-theme');
    
    if (savedTheme) {
        // Apply saved theme
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeToggle(savedTheme === 'dark');
    } else {
        // Check system preference
        const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (prefersDarkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
            updateThemeToggle(true);
            localStorage.setItem('dmac-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            updateThemeToggle(false);
            localStorage.setItem('dmac-theme', 'light');
        }
    }
    
    // Add transition after initial load to prevent flash
    setTimeout(() => {
        document.body.classList.add('theme-transition');
    }, 100);
}

/**
 * Set up the theme toggle switch
 */
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                // Switch to dark theme
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('dmac-theme', 'dark');
            } else {
                // Switch to light theme
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('dmac-theme', 'light');
            }
        });
    }
}

/**
 * Update the theme toggle switch state
 * @param {boolean} isDark - Whether the current theme is dark
 */
function updateThemeToggle(isDark) {
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        themeToggle.checked = isDark;
    }
}

/**
 * Toggle the theme manually
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('dmac-theme', newTheme);
    updateThemeToggle(newTheme === 'dark');
}

/**
 * Apply ripple effect to buttons
 */
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.classList.add('ripple');
    });
    
    // Add ripple effect to buttons dynamically added to the DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        const newButtons = node.querySelectorAll('.btn');
                        newButtons.forEach(button => {
                            button.classList.add('ripple');
                        });
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});
