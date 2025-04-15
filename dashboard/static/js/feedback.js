/**
 * Feedback System for Model Responses
 * 
 * This module provides functionality for users to provide feedback on model responses,
 * helping to improve model performance through reinforcement learning.
 */

class FeedbackSystem {
    constructor() {
        this.feedbackData = {};
        this.feedbackCategories = {
            positive: [
                'Accurate',
                'Helpful',
                'Clear',
                'Concise',
                'Well-reasoned',
                'Creative',
                'Comprehensive'
            ],
            negative: [
                'Inaccurate',
                'Hallucinated facts',
                'Confusing',
                'Too verbose',
                'Incomplete',
                'Harmful',
                'Off-topic'
            ]
        };
    }

    /**
     * Initialize the feedback system
     */
    init() {
        // Add feedback CSS if not already added
        if (!document.querySelector('link[href="/static/css/feedback.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/css/feedback.css';
            document.head.appendChild(link);
        }

        // Add event delegation for feedback buttons
        document.addEventListener('click', (event) => {
            // Handle thumbs up/down clicks
            if (event.target.closest('.feedback-button')) {
                const button = event.target.closest('.feedback-button');
                const messageId = button.closest('.message').dataset.messageId;
                const isPositive = button.classList.contains('positive');
                this.handleFeedbackButtonClick(messageId, isPositive, button);
            }

            // Handle category selection
            if (event.target.closest('.feedback-category')) {
                const category = event.target.closest('.feedback-category');
                category.classList.toggle('selected');
                
                // Update feedback data
                const messageId = category.closest('.message').dataset.messageId;
                const categoryText = category.textContent.trim();
                
                if (!this.feedbackData[messageId]) {
                    this.feedbackData[messageId] = { categories: [] };
                }
                
                if (category.classList.contains('selected')) {
                    if (!this.feedbackData[messageId].categories.includes(categoryText)) {
                        this.feedbackData[messageId].categories.push(categoryText);
                    }
                } else {
                    this.feedbackData[messageId].categories = this.feedbackData[messageId].categories.filter(
                        c => c !== categoryText
                    );
                }
            }

            // Handle feedback submission
            if (event.target.closest('.feedback-submit')) {
                const submitButton = event.target.closest('.feedback-submit');
                const messageId = submitButton.closest('.message').dataset.messageId;
                this.submitFeedback(messageId);
            }
        });

        // Handle textarea input
        document.addEventListener('input', (event) => {
            if (event.target.classList.contains('feedback-textarea')) {
                const messageId = event.target.closest('.message').dataset.messageId;
                if (!this.feedbackData[messageId]) {
                    this.feedbackData[messageId] = {};
                }
                this.feedbackData[messageId].comment = event.target.value;
            }
        });
    }

    /**
     * Add feedback UI to a message
     * @param {HTMLElement} messageElement - The message element
     * @param {string} messageId - The unique ID of the message
     */
    addFeedbackUI(messageElement, messageId) {
        // Skip if not an assistant message or already has feedback
        if (!messageElement.classList.contains('assistant-message') || 
            messageElement.querySelector('.message-feedback')) {
            return;
        }

        // Set message ID
        messageElement.dataset.messageId = messageId;

        // Create feedback container
        const feedbackContainer = document.createElement('div');
        feedbackContainer.className = 'message-feedback';
        feedbackContainer.innerHTML = `
            <span class="feedback-label">Was this response helpful?</span>
            <div class="feedback-buttons">
                <button class="feedback-button positive" title="Helpful">
                    <i class="fas fa-thumbs-up"></i>
                </button>
                <button class="feedback-button negative" title="Not helpful">
                    <i class="fas fa-thumbs-down"></i>
                </button>
            </div>
        `;

        // Create feedback details container (hidden initially)
        const feedbackDetails = document.createElement('div');
        feedbackDetails.className = 'feedback-details';
        
        // Add feedback categories
        let categoriesHTML = '<div class="feedback-categories positive-categories">';
        this.feedbackCategories.positive.forEach(category => {
            categoriesHTML += `<div class="feedback-category">${category}</div>`;
        });
        categoriesHTML += '</div>';
        
        categoriesHTML += '<div class="feedback-categories negative-categories" style="display: none;">';
        this.feedbackCategories.negative.forEach(category => {
            categoriesHTML += `<div class="feedback-category negative">${category}</div>`;
        });
        categoriesHTML += '</div>';
        
        // Add comment textarea and submit button
        feedbackDetails.innerHTML = `
            ${categoriesHTML}
            <textarea class="feedback-textarea" placeholder="Additional comments (optional)"></textarea>
            <button class="feedback-submit">Submit Feedback</button>
        `;

        // Add to message
        messageElement.querySelector('.message-content').appendChild(feedbackContainer);
        messageElement.querySelector('.message-content').appendChild(feedbackDetails);
    }

    /**
     * Handle feedback button click
     * @param {string} messageId - The message ID
     * @param {boolean} isPositive - Whether the feedback is positive
     * @param {HTMLElement} button - The clicked button
     */
    handleFeedbackButtonClick(messageId, isPositive, button) {
        const message = document.querySelector(`.message[data-message-id="${messageId}"]`);
        const feedbackDetails = message.querySelector('.feedback-details');
        const positiveButton = message.querySelector('.feedback-button.positive');
        const negativeButton = message.querySelector('.feedback-button.negative');
        const positiveCategories = message.querySelector('.positive-categories');
        const negativeCategories = message.querySelector('.negative-categories');
        
        // Reset buttons
        positiveButton.classList.remove('selected');
        negativeButton.classList.remove('selected');
        
        // Select clicked button
        button.classList.add('selected');
        
        // Show appropriate categories
        if (isPositive) {
            positiveCategories.style.display = 'flex';
            negativeCategories.style.display = 'none';
        } else {
            positiveCategories.style.display = 'none';
            negativeCategories.style.display = 'flex';
        }
        
        // Show feedback details
        feedbackDetails.classList.add('visible');
        
        // Update feedback data
        if (!this.feedbackData[messageId]) {
            this.feedbackData[messageId] = {};
        }
        this.feedbackData[messageId].isPositive = isPositive;
        this.feedbackData[messageId].categories = [];
        
        // Reset category selections
        message.querySelectorAll('.feedback-category').forEach(category => {
            category.classList.remove('selected');
        });
    }

    /**
     * Submit feedback for a message
     * @param {string} messageId - The message ID
     */
    submitFeedback(messageId) {
        const message = document.querySelector(`.message[data-message-id="${messageId}"]`);
        const feedbackData = this.feedbackData[messageId] || {};
        
        // Add message content to feedback data
        feedbackData.messageContent = message.querySelector('.message-content').textContent.trim();
        feedbackData.messageId = messageId;
        feedbackData.timestamp = new Date().toISOString();
        
        // Send feedback to server
        fetch('/api/feedback/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(feedbackData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success message
                const feedbackDetails = message.querySelector('.feedback-details');
                feedbackDetails.innerHTML = '<div class="alert alert-success">Thank you for your feedback!</div>';
                
                // Hide feedback details after a delay
                setTimeout(() => {
                    feedbackDetails.classList.remove('visible');
                }, 3000);
            } else {
                console.error('Error submitting feedback:', data.error);
            }
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
        });
    }
}

// Initialize feedback system
const feedbackSystem = new FeedbackSystem();
document.addEventListener('DOMContentLoaded', () => {
    feedbackSystem.init();
});
