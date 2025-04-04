/**
 * Side Menu Functionality
 * 
 * This script handles the sliding side menu (drawer) functionality.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const sideMenu = document.getElementById('sideMenu');
    const sideMenuOverlay = document.getElementById('sideMenuOverlay');
    const sideMenuToggle = document.getElementById('sideMenuToggle');
    const sideMenuClose = document.getElementById('sideMenuClose');
    const body = document.body;
    
    // Dropdown toggles
    const dropdownToggles = document.querySelectorAll('.side-menu-dropdown-toggle');
    
    // Functions
    function openSideMenu() {
        sideMenu.classList.add('open');
        sideMenuOverlay.classList.add('open');
        body.classList.add('side-menu-open');
    }
    
    function closeSideMenu() {
        sideMenu.classList.remove('open');
        sideMenuOverlay.classList.remove('open');
        body.classList.remove('side-menu-open');
    }
    
    // Event Listeners
    sideMenuToggle.addEventListener('click', openSideMenu);
    sideMenuClose.addEventListener('click', closeSideMenu);
    sideMenuOverlay.addEventListener('click', closeSideMenu);
    
    // Handle dropdown toggles
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const parentItem = this.closest('.side-menu-item');
            
            // Check if this item is already active
            const isActive = parentItem.classList.contains('active');
            
            // Close all other dropdowns
            document.querySelectorAll('.side-menu-item').forEach(item => {
                if (item !== parentItem && item.querySelector('.side-menu-dropdown-toggle')) {
                    item.classList.remove('active');
                }
            });
            
            // Toggle this dropdown
            parentItem.classList.toggle('active', !isActive);
        });
    });
    
    // Auto-open dropdowns for active items
    document.querySelectorAll('.side-menu-dropdown li a').forEach(link => {
        if (link.getAttribute('href') === window.location.pathname) {
            const parentDropdown = link.closest('.side-menu-item');
            if (parentDropdown) {
                parentDropdown.classList.add('active');
            }
        }
    });
    
    // Handle keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sideMenu.classList.contains('open')) {
            closeSideMenu();
        }
    });
    
    // Close side menu on window resize if in mobile view
    window.addEventListener('resize', function() {
        if (window.innerWidth < 992 && sideMenu.classList.contains('open')) {
            closeSideMenu();
        }
    });
    
    // Open side menu by default on large screens
    if (window.innerWidth >= 1200) {
        openSideMenu();
    }
});
