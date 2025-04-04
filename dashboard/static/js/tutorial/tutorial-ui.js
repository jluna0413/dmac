/**
 * DMac Tutorial UI
 *
 * This file handles the UI elements for the interactive tutorial.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Create the help button
    createHelpButton();

    // Check if we should show welcome message or start tutorial for new users
    setTimeout(() => {
        // Show welcome message for first-time visitors
        showWelcomeMessage();

        // Or automatically start tutorial if welcome message isn't shown
        checkAndStartTutorial();
    }, 1000); // Delay to ensure the page is fully loaded
});

/**
 * Creates the help button and tutorial menu
 */
function createHelpButton() {
    // Create help button
    const helpButton = document.createElement('div');
    helpButton.className = 'help-button';
    helpButton.innerHTML = '<i class="fas fa-question"></i>';
    helpButton.setAttribute('aria-label', 'Help');
    helpButton.setAttribute('role', 'button');
    helpButton.setAttribute('tabindex', '0');

    // Create tutorial menu
    const tutorialMenu = document.createElement('div');
    tutorialMenu.className = 'tutorial-menu';

    // Create tutorial menu header
    const tutorialMenuHeader = document.createElement('div');
    tutorialMenuHeader.className = 'tutorial-menu-header';
    tutorialMenuHeader.textContent = 'Tutorial Options';

    // Create tutorial menu items
    const tutorialMenuItems = document.createElement('div');
    tutorialMenuItems.className = 'tutorial-menu-items';

    // Add menu items based on the current page
    const currentPath = window.location.pathname;

    // Main tutorial (always available)
    const mainTutorialItem = document.createElement('div');
    mainTutorialItem.className = 'tutorial-menu-item';
    mainTutorialItem.innerHTML = '<i class="fas fa-play-circle"></i> Main Tutorial';
    mainTutorialItem.addEventListener('click', function () {
        tutorialMenu.classList.remove('open');
        window.restartTutorial('main');
    });
    tutorialMenuItems.appendChild(mainTutorialItem);

    // Page-specific tutorials
    if (currentPath.includes('/chat')) {
        const chatTutorialItem = document.createElement('div');
        chatTutorialItem.className = 'tutorial-menu-item';
        chatTutorialItem.innerHTML = '<i class="fas fa-comment-dots"></i> Chat Tutorial';
        chatTutorialItem.addEventListener('click', function () {
            tutorialMenu.classList.remove('open');
            window.restartTutorial('chat');
        });
        tutorialMenuItems.appendChild(chatTutorialItem);
    }

    if (currentPath.includes('/settings')) {
        const settingsTutorialItem = document.createElement('div');
        settingsTutorialItem.className = 'tutorial-menu-item';
        settingsTutorialItem.innerHTML = '<i class="fas fa-cog"></i> Settings Tutorial';
        settingsTutorialItem.addEventListener('click', function () {
            tutorialMenu.classList.remove('open');
            window.restartTutorial('settings');
        });
        tutorialMenuItems.appendChild(settingsTutorialItem);
    }

    // Help center item
    const helpCenterItem = document.createElement('div');
    helpCenterItem.className = 'tutorial-menu-item';
    helpCenterItem.innerHTML = '<i class="fas fa-book"></i> Help Center';
    helpCenterItem.addEventListener('click', function () {
        tutorialMenu.classList.remove('open');
        // Open help center (placeholder for now)
        alert('Help Center will be available soon!');
    });
    tutorialMenuItems.appendChild(helpCenterItem);

    // Assemble the menu
    tutorialMenu.appendChild(tutorialMenuHeader);
    tutorialMenu.appendChild(tutorialMenuItems);

    // Add event listener to toggle the menu
    helpButton.addEventListener('click', function () {
        tutorialMenu.classList.toggle('open');
    });

    // Close menu when clicking outside
    document.addEventListener('click', function (event) {
        if (!helpButton.contains(event.target) && !tutorialMenu.contains(event.target)) {
            tutorialMenu.classList.remove('open');
        }
    });

    // Add elements to the body
    document.body.appendChild(helpButton);
    document.body.appendChild(tutorialMenu);
}

/**
 * Shows a welcome message for first-time users
 */
function showWelcomeMessage() {
    // Check if this is the first visit
    const firstVisit = !localStorage.getItem('dmac_visited');

    if (firstVisit) {
        // Mark as visited
        localStorage.setItem('dmac_visited', 'true');

        // Create welcome message
        const welcomeMessage = document.createElement('div');
        welcomeMessage.className = 'welcome-message';
        welcomeMessage.innerHTML = `
            <div class="welcome-message-content">
                <h2>Welcome to DMac!</h2>
                <p>Would you like to take a quick tour to learn about the main features?</p>
                <div class="welcome-message-buttons">
                    <button class="btn btn-primary" id="startTutorialBtn">Start Tutorial</button>
                    <button class="btn btn-outline-secondary" id="skipTutorialBtn">Skip for Now</button>
                </div>
            </div>
        `;

        // Add event listeners
        welcomeMessage.querySelector('#startTutorialBtn').addEventListener('click', function () {
            document.body.removeChild(welcomeMessage);
            window.restartTutorial('main');
        });

        welcomeMessage.querySelector('#skipTutorialBtn').addEventListener('click', function () {
            document.body.removeChild(welcomeMessage);
        });

        // Add to body
        document.body.appendChild(welcomeMessage);
    }
}
