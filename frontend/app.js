// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();

// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';  // Change in production

// User data
let userData = null;

// Initialize app
async function initApp() {
    // Get user data from Telegram
    const initData = tg.initData;
    if (!initData) {
        console.error('No init data from Telegram');
        return;
    }

    try {
        // Authenticate user
        const response = await fetch(`${API_BASE_URL}/auth/telegram`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(initData),
        });

        if (!response.ok) {
            throw new Error('Authentication failed');
        }

        userData = await response.json();
        console.log('User authenticated:', userData);
    } catch (error) {
        console.error('Authentication error:', error);
        tg.showAlert('Failed to authenticate. Please try again.');
    }
}

// Screen navigation
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

// Start app
function startApp() {
    showScreen('mood-screen');
}

// Mood tracking
async function submitMood() {
    const moodLevel = document.querySelector('.mood-button.selected')?.dataset.mood;
    const comment = document.getElementById('mood-comment').value;

    if (!moodLevel) {
        tg.showAlert('Please select your mood');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/mood/track`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                telegram_id: userData.telegram_id,
                mood_level: parseInt(moodLevel),
                comment: comment
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to save mood');
        }

        const result = await response.json();
        tg.showAlert('Mood saved successfully!');
        
        // Clear form
        document.querySelectorAll('.mood-button').forEach(btn => btn.classList.remove('selected'));
        document.getElementById('mood-comment').value = '';
    } catch (error) {
        console.error('Error saving mood:', error);
        tg.showAlert('Failed to save mood. Please try again.');
    }
}

// Chat functionality
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';

    try {
        const response = await fetch(`${API_BASE_URL}/chat/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                telegram_id: userData.telegram_id,
                message: message
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to send message');
        }

        const result = await response.json();
        addMessageToChat(result.response, 'ai');
    } catch (error) {
        console.error('Error sending message:', error);
        tg.showAlert('Failed to send message. Please try again.');
    }
}

function addMessageToChat(message, type) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}-message`;
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Journal functionality
async function saveJournal() {
    const sleepStart = document.getElementById('sleep-start').value;
    const sleepEnd = document.getElementById('sleep-end').value;
    const nutritionNotes = document.getElementById('nutrition-notes').value;

    try {
        const response = await fetch(`${API_BASE_URL}/journal/entry`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                telegram_id: userData.telegram_id,
                sleep_start: sleepStart ? new Date(sleepStart).toISOString() : null,
                sleep_end: sleepEnd ? new Date(sleepEnd).toISOString() : null,
                nutrition_notes: nutritionNotes
            }),
        });

        if (!response.ok) {
            throw new Error('Failed to save journal entry');
        }

        const result = await response.json();
        tg.showAlert('Journal entry saved successfully!');
        
        // Clear form
        document.getElementById('sleep-start').value = '';
        document.getElementById('sleep-end').value = '';
        document.getElementById('nutrition-notes').value = '';
    } catch (error) {
        console.error('Error saving journal entry:', error);
        tg.showAlert('Failed to save journal entry. Please try again.');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize app
    initApp();

    // Mood button selection
    document.querySelectorAll('.mood-button').forEach(button => {
        button.addEventListener('click', () => {
            document.querySelectorAll('.mood-button').forEach(btn => btn.classList.remove('selected'));
            button.classList.add('selected');
        });
    });

    // Chat input enter key
    document.getElementById('message-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}); 