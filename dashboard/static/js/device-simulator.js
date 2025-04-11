/**
 * Device Simulator JavaScript
 * 
 * Handles the device simulator functionality for testing responsive designs.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add device simulator CSS if not already added
    if (!document.querySelector('link[href="/static/css/device-simulator.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/css/device-simulator.css';
        document.head.appendChild(link);
    }
    
    // Toggle device simulator
    const deviceToggleBtn = document.getElementById('deviceToggleBtn');
    const deviceSimulatorPanel = document.querySelector('.device-simulator-panel');
    const closeDeviceSimulator = document.getElementById('closeDeviceSimulator');
    
    if (deviceToggleBtn && deviceSimulatorPanel) {
        deviceToggleBtn.addEventListener('click', function() {
            deviceSimulatorPanel.classList.toggle('open');
        });
        
        closeDeviceSimulator.addEventListener('click', function() {
            deviceSimulatorPanel.classList.remove('open');
        });
        
        // Close on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && deviceSimulatorPanel.classList.contains('open')) {
                deviceSimulatorPanel.classList.remove('open');
            }
        });
    }
    
    // Handle device selection
    const deviceSelect = document.getElementById('deviceSelect');
    const deviceFrame = document.querySelector('.device-frame');
    const deviceFrame2 = document.getElementById('deviceFrame');
    
    if (deviceSelect && deviceFrame && deviceFrame2) {
        deviceSelect.addEventListener('change', function() {
            // Remove all device classes
            deviceFrame.className = 'device-frame';
            
            // Add selected device class
            if (this.value !== 'default') {
                deviceFrame.classList.add(this.value);
            }
            
            // Apply orientation
            const orientationRadios = document.querySelectorAll('input[name="orientation"]');
            for (const radio of orientationRadios) {
                if (radio.checked && radio.id === 'landscape') {
                    deviceFrame.classList.add('landscape');
                }
            }
            
            // Update iframe source to current page if not already set
            if (!deviceFrame2.src || deviceFrame2.src === 'about:blank') {
                deviceFrame2.src = window.location.href;
            }
            
            // Adjust scale for very large devices
            if (['laptop', 'laptop-hd', 'ipad-pro'].includes(this.value)) {
                const scale = this.value === 'laptop-hd' ? 0.3 : 0.5;
                deviceFrame2.style.transform = `scale(${scale})`;
                deviceFrame2.style.width = `${100 / scale}%`;
                deviceFrame2.style.height = `${100 / scale}%`;
            } else {
                deviceFrame2.style.transform = '';
                deviceFrame2.style.width = '100%';
                deviceFrame2.style.height = '100%';
            }
        });
    }
    
    // Handle orientation change
    const orientationRadios = document.querySelectorAll('input[name="orientation"]');
    
    if (orientationRadios.length && deviceFrame) {
        orientationRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.id === 'landscape') {
                    deviceFrame.classList.add('landscape');
                } else {
                    deviceFrame.classList.remove('landscape');
                }
            });
        });
    }
    
    // Initialize iframe with current page
    if (deviceFrame2 && (!deviceFrame2.src || deviceFrame2.src === 'about:blank')) {
        // Use current page URL, but remove any query parameters that might cause infinite loops
        const url = new URL(window.location.href);
        url.searchParams.delete('simulator');
        deviceFrame2.src = url.toString();
    }
    
    // Prevent simulator iframe from opening another simulator
    if (window.self !== window.top) {
        // We're in an iframe, hide the simulator toggle
        const toggleBtn = document.getElementById('deviceToggleBtn');
        if (toggleBtn) {
            toggleBtn.style.display = 'none';
        }
    }
});
