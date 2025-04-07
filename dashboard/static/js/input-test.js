/**
 * Test script to check if the input UI is being initialized
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Input test script loaded');
    
    // Check if the footer input container exists
    const footerInputContainer = document.getElementById('footer-input-container');
    console.log('Footer input container:', footerInputContainer);
    
    // Check if we're on a chat page
    const chatPages = ['/chat', '/assistant', '/'];
    const currentPath = window.location.pathname;
    console.log('Current path:', currentPath);
    console.log('Is chat page:', chatPages.includes(currentPath));
    
    // Check if the UnifiedInput class is available
    console.log('UnifiedInput class available:', typeof UnifiedInput !== 'undefined');
    
    // Try to manually initialize the input UI
    setTimeout(() => {
        console.log('Attempting to manually initialize input UI');
        if (footerInputContainer && chatPages.includes(currentPath)) {
            try {
                // Create a basic input UI
                footerInputContainer.innerHTML = `
                    <div class="input-group">
                        <button id="voice-button-test" class="btn input-group-prepend" title="Voice Input">
                            <i class="fas fa-microphone"></i>
                        </button>
                        <textarea id="user-input-test" class="form-control" placeholder="Message DMac..." rows="1"></textarea>
                        <div class="input-group-append d-flex">
                            <button id="upload-button-test" class="tool-pill" title="Upload Files">
                                <i class="fas fa-upload"></i> Files
                            </button>
                            <button id="send-button-test" class="btn">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                `;
                console.log('Manual initialization complete');
            } catch (error) {
                console.error('Error during manual initialization:', error);
            }
        }
    }, 1000);
});
