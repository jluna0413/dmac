/**
 * DMac Interactive Tutorial Configuration
 * 
 * This file defines the steps for the interactive tutorial.
 */

// Initialize the tutorial configuration
const dmacTutorial = {
    // Main tutorial for new users
    mainTutorial: [
        // Welcome step
        {
            element: '#sideMenuToggle',
            popover: {
                title: 'Welcome to DMac!',
                description: 'This quick tutorial will guide you through the main features of DMac. Let\'s start with the navigation menu.',
                position: 'right'
            }
        },
        // Side menu
        {
            element: '#sideMenu',
            popover: {
                title: 'Navigation Menu',
                description: 'This side menu gives you access to all sections of DMac. You can click on any item to navigate to that section.',
                position: 'right'
            }
        },
        // Dashboard
        {
            element: '.side-menu-item:nth-child(1)',
            popover: {
                title: 'Dashboard',
                description: 'The Dashboard gives you an overview of your AI agents, tasks, and system status.',
                position: 'right'
            }
        },
        // Chat
        {
            element: '.side-menu-item:nth-child(2)',
            popover: {
                title: 'Chat Interface',
                description: 'The Chat section allows you to interact with AI models directly through text or voice.',
                position: 'right'
            }
        },
        // Agents section
        {
            element: '.side-menu-section:nth-child(2)',
            popover: {
                title: 'Agents & Tasks',
                description: 'This section lets you manage your AI agents and assign tasks to them.',
                position: 'right'
            }
        },
        // Models section
        {
            element: '.side-menu-section:nth-child(3)',
            popover: {
                title: 'Models & WebArena',
                description: 'Here you can manage your AI models and access WebArena for testing agent performance.',
                position: 'right'
            }
        },
        // Settings
        {
            element: '.side-menu-section:nth-child(4)',
            popover: {
                title: 'Settings',
                description: 'Configure your profile, account settings, and system preferences here.',
                position: 'right'
            }
        },
        // User profile
        {
            element: '.user-profile',
            popover: {
                title: 'Your Profile',
                description: 'Click here to access your profile settings, switch accounts, or log out.',
                position: 'bottom'
            }
        },
        // Conclusion
        {
            element: 'body',
            popover: {
                title: 'You\'re All Set!',
                description: 'You\'ve completed the basic tutorial. Feel free to explore DMac on your own, or check the Help section for more detailed guides.',
                position: 'middle'
            }
        }
    ],
    
    // Chat page tutorial
    chatTutorial: [
        // Welcome to chat
        {
            element: '#user-input',
            popover: {
                title: 'Chat Interface',
                description: 'This is where you can type messages to interact with AI models.',
                position: 'top'
            }
        },
        // Voice input
        {
            element: '#voice-button',
            popover: {
                title: 'Voice Input',
                description: 'Click this button to use your microphone for voice input instead of typing.',
                position: 'top'
            }
        },
        // File upload
        {
            element: '#upload-button',
            popover: {
                title: 'Upload Files',
                description: 'You can upload documents, images, or code files to include in your conversation.',
                position: 'top'
            }
        },
        // Research button
        {
            element: '#research-button',
            popover: {
                title: 'Deep Research',
                description: 'This button activates deep research mode, allowing the AI to search for information online.',
                position: 'top'
            }
        },
        // Think button
        {
            element: '#think-button',
            popover: {
                title: 'Deep Thinking',
                description: 'Activates deep thinking mode, giving the AI more time to solve complex problems.',
                position: 'top'
            }
        },
        // Model selector
        {
            element: '#model-selector',
            popover: {
                title: 'Model Selection',
                description: 'Choose which AI model you want to chat with from this dropdown menu.',
                position: 'top'
            }
        }
    ],
    
    // Settings page tutorial
    settingsTutorial: [
        // Profile section
        {
            element: 'a[href="#profile"]',
            popover: {
                title: 'Profile Settings',
                description: 'Here you can update your profile information and upload a profile picture.',
                position: 'right'
            }
        },
        // Account section
        {
            element: 'a[href="#account"]',
            popover: {
                title: 'Account & Security',
                description: 'Manage your account security, connected accounts, and two-factor authentication.',
                position: 'right'
            }
        },
        // General settings
        {
            element: 'a[href="#general"]',
            popover: {
                title: 'General Settings',
                description: 'Configure general system settings like theme, language, and notifications.',
                position: 'right'
            }
        },
        // Models settings
        {
            element: 'a[href="#models"]',
            popover: {
                title: 'Models Settings',
                description: 'Configure AI model settings, endpoints, and caching options.',
                position: 'right'
            }
        }
    ]
};

// Function to start the appropriate tutorial based on the current page
function startTutorial(tutorialType = 'main') {
    // Create driver instance
    const driver = window.driver.js({
        animate: true,
        opacity: 0.75,
        padding: 10,
        showButtons: ['next', 'previous', 'close'],
        showProgress: true,
        allowClose: true,
        overlayClickNext: false,
        doneBtnText: 'Done',
        closeBtnText: 'Skip',
        nextBtnText: 'Next',
        prevBtnText: 'Previous',
        onHighlightStarted: (element) => {
            // If the element is in the side menu and the menu is closed, open it
            if (element && element.closest('#sideMenu') && !document.body.classList.contains('side-menu-open')) {
                document.getElementById('sideMenuToggle').click();
            }
        }
    });

    // Select the appropriate tutorial based on the current page
    let steps = [];
    if (tutorialType === 'main') {
        steps = dmacTutorial.mainTutorial;
    } else if (tutorialType === 'chat') {
        steps = dmacTutorial.chatTutorial;
    } else if (tutorialType === 'settings') {
        steps = dmacTutorial.settingsTutorial;
    }

    // Start the tutorial
    if (steps.length > 0) {
        driver.setSteps(steps);
        driver.start();
        
        // Save in localStorage that the user has seen the tutorial
        localStorage.setItem('dmac_tutorial_shown', 'true');
    }
}

// Function to check if the tutorial should be shown automatically
function checkAndStartTutorial() {
    // Check if this is a new user (tutorial not shown before)
    const tutorialShown = localStorage.getItem('dmac_tutorial_shown');
    
    if (!tutorialShown) {
        // For new users, show the tutorial automatically
        startTutorial('main');
    }
}

// Add a global function to restart the tutorial
window.restartTutorial = function(tutorialType = 'main') {
    startTutorial(tutorialType);
};
