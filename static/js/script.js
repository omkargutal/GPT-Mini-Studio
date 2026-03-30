// ==========================================
// 1. Application State & Auth Logic
// ==========================================
let isGenerating = false;
let currentUser = null;
let currentSessionId = null;

// Guest gets 5 credits
let guestCredits = 5;

// ==========================================
// 2. DOM Elements Selection
// ==========================================
const chatMessages = document.getElementById('chatMessages');
const promptInput = document.getElementById('promptInput');
const sendBtn = document.getElementById('sendBtn');
const chatHistoryList = document.getElementById('chatHistoryList');

// Sliders (Hidden technically, but keep logic if they get re-enabled)
const maxTokensSlider = document.getElementById('maxTokens');
const temperatureSlider = document.getElementById('temperature');
const topKSlider = document.getElementById('topK');

// Auth Modals
const authModal = document.getElementById('authModal');
const emailInput = document.getElementById('emailInput');
const pinInput = document.getElementById('pinInput');
const firstNameInput = document.getElementById('firstNameInput');
const lastNameInput = document.getElementById('lastNameInput');
const mobileInput = document.getElementById('mobileInput');

// Sidebar toggle
const sidebarToggle = document.getElementById('sidebarToggle');
const appSidebar = document.getElementById('appSidebar');

if (sidebarToggle && appSidebar) {
    sidebarToggle.addEventListener('click', () => {
        appSidebar.classList.toggle('show');
    });
}

// ==========================================
// 3. Initial Load
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    // Check if logged in previously
    const savedUser = localStorage.getItem('gpt_user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        updateUserUI();
        loadChatHistory();
    } else {
        updateUserUI(); // Load guest UI
    }
});

// ==========================================
// 4. Event Listeners
// ==========================================
promptInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 200) + 'px';
    if (this.value.trim().length > 0 && !isGenerating) {
        sendBtn.disabled = false;
    } else {
        sendBtn.disabled = true;
    }
});

promptInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (this.value.trim() !== '' && !isGenerating) {
            handleSend();
        }
    }
});

sendBtn.addEventListener('click', handleSend);

// ==========================================
// 5. Auth & User UI Logic
// ==========================================
let currentAuthMode = 'login';

window.openModal = function (mode) {
    authModal.classList.add('active');
    switchAuthMode(mode || 'login');
}

window.closeModal = function () {
    authModal.classList.remove('active');
}

window.switchAuthMode = function (mode) {
    currentAuthMode = mode;
    const tabLogin = document.getElementById('tabLogin');
    const tabSignup = document.getElementById('tabSignup');
    const emailAuthBtn = document.getElementById('emailAuthBtn');
    const signupFields = document.querySelectorAll('.signup-field');

    if (mode === 'login') {
        tabLogin.classList.add('active');
        tabSignup.classList.remove('active');
        emailAuthBtn.innerText = "Log in";
        signupFields.forEach(f => f.style.display = 'none');
    } else {
        tabSignup.classList.add('active');
        tabLogin.classList.remove('active');
        emailAuthBtn.innerText = "Sign up";
        signupFields.forEach(f => f.style.display = 'block');
    }
}

window.handleEmailAuth = async function () {
    const email = emailInput.value.trim();
    const pin = pinInput.value.trim();

    if (!email || !pin) {
        alert("Please enter email and password.");
        return;
    }

    const emailAuthBtn = document.getElementById('emailAuthBtn');
    emailAuthBtn.innerText = "Loading...";
    emailAuthBtn.disabled = true;

    if (currentAuthMode === 'signup') {
        const first = firstNameInput.value.trim();
        const last = lastNameInput.value.trim();
        const mobile = mobileInput.value.trim();

        if (!first || !last) {
            alert("First Name and Last Name are required!");
            emailAuthBtn.innerText = "Sign up";
            emailAuthBtn.disabled = false;
            return;
        }

        try {
            const res = await fetch('/api/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    first_name: first,
                    last_name: last,
                    email: email,
                    password: pin,
                    mobile: mobile || null
                })
            });
            const data = await res.json();
            if (!res.ok) {
                let errMsg = "Signup failed";
                if (data.detail) errMsg = Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : data.detail;
                throw new Error(errMsg);
            }

            alert("Account created successfully! Logging you in...");
            switchAuthMode('login');
            handleEmailAuth(); // auto login
        } catch (e) {
            alert(e.message);
            emailAuthBtn.innerText = "Sign up";
            emailAuthBtn.disabled = false;
        }
    } else {
        // LOGIN
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, password: pin })
            });
            const data = await res.json();
            if (!res.ok) {
                let errMsg = "Login failed";
                if (data.detail) errMsg = Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : data.detail;
                throw new Error(errMsg);
            }

            currentUser = data;
            localStorage.setItem('gpt_user', JSON.stringify(currentUser));
            closeModal();
            updateUserUI();
            loadChatHistory();
            startNewChat();
        } catch (e) {
            alert(e.message);
            emailAuthBtn.innerText = "Log in";
            emailAuthBtn.disabled = false;
        }
    }
}

window.logout = function () {
    currentUser = null;
    currentSessionId = null;
    localStorage.removeItem('gpt_user');
    updateUserUI();
    // Clear history view
    chatHistoryList.innerHTML = `<div class="history-group"><i class="fa-solid fa-clock-rotate-left"></i> CHAT HISTORY</div>`;
    startNewChat();
}

function updateUserUI() {
    const headerAuth = document.getElementById('headerAuthButtons');
    const sidebarLoginPrompt = document.getElementById('sidebarLoginPrompt');
    const userProfile = document.getElementById('userProfile');

    if (currentUser) {
        headerAuth.classList.add('hidden');
        sidebarLoginPrompt.classList.add('hidden');
        userProfile.classList.remove('hidden');

        document.getElementById('displayEmail').innerText = currentUser.email;
        document.getElementById('displayCredits').innerText = currentUser.is_admin ? "Unlimited" : currentUser.credits;
        document.querySelector('.user-avatar').innerText = currentUser.first_name.charAt(0).toUpperCase();

        // Update profile menu details
        const fullName = (currentUser.first_name + (currentUser.last_name ? " " + currentUser.last_name : "")).toUpperCase();
        document.getElementById('dropdownUserName').innerText = fullName;
        document.getElementById('dropdownUserEmail').innerText = currentUser.email;
        document.querySelectorAll('.dropdown-header .user-avatar').forEach(av => av.innerText = currentUser.first_name.charAt(0).toUpperCase());
    } else {
        headerAuth.classList.remove('hidden');
        sidebarLoginPrompt.classList.remove('hidden');
        userProfile.classList.add('hidden');
    }
}

// ==========================================
// 6. History & Chat Session Load
// ==========================================
let currentUserSessions = []; // Global to store original list
let isSearchActive = false;

async function loadChatHistory() {
    if (!currentUser) return;
    try {
        const res = await fetch(`/api/users/${currentUser.user_id}/sessions`);
        currentUserSessions = await res.json();
        if (!isSearchActive) {
            renderHistoryList(currentUserSessions);
        }
    } catch (e) {
        console.error("Failed to load history", e);
    }
}

function renderHistoryList(sessions, isSearchResult = false) {
    chatHistoryList.innerHTML = `<div class="history-group"><i class="fa-solid fa-chevron-down" style="font-size: 10px;"></i> ${isSearchResult ? 'Search Results' : 'Your Chats'}</div>`;

    if (sessions.length === 0) {
        chatHistoryList.innerHTML += `<div style="padding:12px; font-size:12px; color:var(--text-muted); text-align:center;">No ${isSearchResult ? 'results' : 'chats'} found</div>`;
        return;
    }

    sessions.forEach(sess => {
        const div = document.createElement('div');
        div.className = 'history-item';
        if (sess.id === currentSessionId) div.classList.add('active');

        div.innerHTML = `
            <span class="item-text">${sess.is_pinned ? '<i class="fa-solid fa-thumbtack" style="font-size:10px; margin-right:6px; color:var(--primary);"></i>' : ''}${sess.title}</span>
            <div class="dots-btn" onclick="openContextMenu(event, ${sess.id})">
                <i class="fa-solid fa-ellipsis"></i>
            </div>
        `;

        div.onclick = (e) => {
            if (!e.target.closest('.dots-btn')) {
                loadSessionMessages(sess.id, div);
            }
        };
        chatHistoryList.appendChild(div);
    });
}

async function loadSessionMessages(sessionId, element) {
    if (!currentUser) return;
    currentSessionId = sessionId;

    // update active tab
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
    if (element) element.classList.add('active');

    chatMessages.innerHTML = ''; // clear current
    document.querySelector('.status-text').textContent = "Loading...";

    try {
        const res = await fetch(`/api/sessions/${sessionId}/messages`);
        const msgs = await res.json();

        msgs.forEach(m => {
            appendMessage(m.content, m.sender, false, m.tokens_used > 0 ? m.tokens_used : null);
        });
        document.querySelector('.status-text').textContent = "Model Ready";
        document.querySelector('.status-dot').style.backgroundColor = 'var(--success)';
    } catch (e) {
        console.error("Failed to load messages", e);
    }
}

window.startNewChat = function () {
    currentSessionId = null;
    document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));

    chatMessages.innerHTML = `
        <div class="message system-message fade-in-up">
            <div class="message-avatar">🤖</div>
            <div class="message-bubble system">Hello! I am GPT Mini. I'm ready for inference. What would you like me to generate today?</div>
        </div>
    `;

    document.querySelector('.status-text').textContent = "Model Ready";
    document.querySelector('.status-dot').style.backgroundColor = 'var(--success)';
}

// ==========================================
// 7. Generation API Call
// ==========================================
async function handleSend() {
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    // Credit enforcement logic
    if (currentUser && !currentUser.is_admin && currentUser.credits <= 0) {
        alert("You have run out of credits for today! Credits will refresh 24 hours after your last refresh.");
        return;
    } else if (!currentUser && guestCredits <= 0) {
        alert("Guest limit reached! Please Log in or Sign up to get 50 free credits daily.");
        openModal('signup');
        return;
    }

    const requestData = {
        prompt: prompt,
        max_new_tokens: maxTokensSlider ? parseInt(maxTokensSlider.value) : 1000,
        temperature: temperatureSlider ? parseFloat(temperatureSlider.value) : 0.7,
        top_k: topKSlider ? parseInt(topKSlider.value) : 50,
        user_id: currentUser ? currentUser.user_id : null,
        session_id: currentSessionId
    };

    promptInput.value = '';
    promptInput.style.height = 'auto';
    sendBtn.disabled = true;
    isGenerating = true;

    appendMessage(prompt, 'user');

    // Optimistic Guest Deduction
    if (!currentUser) guestCredits--;

    const loadingId = appendLoadingIndicator();

    try {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        statusText.textContent = "Generating...";
        statusDot.style.backgroundColor = 'var(--primary)';
        statusDot.style.boxShadow = 'none';

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        document.getElementById(loadingId).remove();

        if (!response.ok) {
            let errMsg = 'Failed to generate content.';
            if (data.detail) errMsg = Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : data.detail;
            appendMessage(`Error: ${errMsg}`, 'system', true);
            statusDot.classList.add('error');
            statusText.textContent = "Error";
        } else {
            appendMessage(data.generated_text, 'system', false, data.num_tokens);
            statusText.textContent = "Model Ready";
            statusDot.style.backgroundColor = 'var(--success)';
            statusDot.classList.remove('error');

            // If backend returned session/credits, update state
            if (currentUser && data.session_id) {
                const wasNewSession = !currentSessionId;
                currentSessionId = data.session_id;
                currentUser.credits = data.credits_remaining;
                localStorage.setItem('gpt_user', JSON.stringify(currentUser));
                updateUserUI();

                if (wasNewSession) {
                    // Update the sidebar history to show the new chat
                    setTimeout(loadChatHistory, 500);
                }
            }
        }

    } catch (error) {
        console.error("Fetch error:", error);
        document.getElementById(loadingId).remove();
        appendMessage(`Connection Error: Unable to reach the API.`, 'system', true);
    } finally {
        isGenerating = false;
        if (promptInput.value.trim() !== '') {
            sendBtn.disabled = false;
        }
    }
}

function appendMessage(text, sender, isError = false, numTokens = null) {
    const messageId = 'msg-' + Date.now();
    const div = document.createElement('div');
    div.className = `message ${sender}-message fade-in-up`;
    div.id = messageId;

    let contentHtml = text;
    if (contentHtml.includes('```')) { // Escape backticks
        contentHtml = contentHtml.replace(/```([\s\S]*?)```/g, '<pre style="background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;margin-top:8px;overflow-x:auto;"><code>$1</code></pre>');
    }

    let metaHtml = '';
    if (numTokens) {
        metaHtml = `<div class="message-meta"><i class="fa-solid fa-bolt"></i> Generated ${numTokens} tokens</div>`;
    }

    div.innerHTML = `
        <div class="message-avatar">
            ${sender === 'user' ? (currentUser ? currentUser.first_name.charAt(0).toUpperCase() : 'U') : '🤖'}
        </div>
        <div style="display:flex; flex-direction:column; max-width:calc(100% - 46px);">
            <div class="message-bubble ${sender}" ${isError ? 'style="border-color: var(--error);"' : ''}>${contentHtml}</div>
            ${metaHtml}
        </div>
    `;

    chatMessages.appendChild(div);
    scrollToBottom();
    return messageId;
}

function appendLoadingIndicator() {
    const loadingId = 'loading-' + Date.now();
    const div = document.createElement('div');
    div.className = `message system-message fade-in-up`;
    div.id = loadingId;

    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-bubble system">
            <div class="loading-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;

    chatMessages.appendChild(div);
    scrollToBottom();
    return loadingId;
}

function scrollToBottom() {
    const cContainer = document.querySelector('.chat-container');
    cContainer.scrollTo({ top: cContainer.scrollHeight, behavior: 'smooth' });
}

// ==========================================
// 8. New UI Features Logic
// ==========================================

window.toggleProfileMenu = function (event) {
    event.stopPropagation();
    const menu = document.getElementById('profileMenu');
    menu.classList.toggle('active');
}

// Close dropdown if clicking outside
document.addEventListener('click', () => {
    const menu = document.getElementById('profileMenu');
    if (menu) menu.classList.remove('active');
});

// Modals Logic
window.openUpgradeModal = () => document.getElementById('upgradeModal').classList.add('active');
window.closeUpgradeModal = () => document.getElementById('upgradeModal').classList.remove('active');

window.openSettingsModal = () => document.getElementById('settingsModal').classList.add('active');
window.closeSettingsModal = () => document.getElementById('settingsModal').classList.remove('active');

window.openHelpModal = () => document.getElementById('helpModal').classList.add('active');
window.closeHelpModal = () => document.getElementById('helpModal').classList.remove('active');

// Bug Report Submission
window.submitBugReport = async function () {
    const text = document.getElementById('bugReportText').value.trim();
    if (!text) {
        alert("Please describe the issue.");
        return;
    }

    const sendBtn = document.querySelector('.send-report-btn');
    sendBtn.innerText = "Sending...";
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_email: currentUser ? currentUser.email : "Guest",
                message: text,
                include_screenshot: document.getElementById('includeScreenshot').checked
            })
        });

        if (response.ok) {
            alert("Feedback sent! Thank you for helping us improve.");
            document.getElementById('bugReportText').value = '';
            closeHelpModal();
        } else {
            alert("Failed to send feedback. Please try again later.");
        }
    } catch (e) {
        alert("Connection error. Check your server status.");
    } finally {
        sendBtn.innerText = "Send";
        sendBtn.disabled = false;
    }
}

// Reset System
window.clearAppData = function () {
    if (confirm("This will log you out and clear all local session data. Continue?")) {
        localStorage.clear();
        window.location.reload();
    }
}

// Bug Report Char Count
const bugTextarea = document.getElementById('bugReportText');
if (bugTextarea) {
    bugTextarea.addEventListener('input', function () {
        const count = document.querySelector('.char-count');
        if (count) count.innerText = `${this.value.length} / 2000 characters used`;
    });
}
// Sidebar Toggle
window.toggleSidebar = function () {
    const sidebar = document.getElementById('appSidebar');
    sidebar.classList.toggle('closed');
}

// Chat Context Menu
let activeContextSessionId = null;

window.openContextMenu = function (event, sessionId) {
    event.preventDefault();
    event.stopPropagation();
    activeContextSessionId = sessionId;

    const menu = document.getElementById('chatContextMenu');
    menu.classList.add('active');

    // Position menu
    const rect = event.currentTarget.getBoundingClientRect();
    menu.style.top = `${rect.bottom + 5}px`;
    menu.style.left = `${rect.left - 130}px`;
};

// Close all menus when clicking outside
document.addEventListener('click', () => {
    const profileMenu = document.getElementById('profileMenu');
    if (profileMenu) profileMenu.classList.remove('active');

    const chatMenu = document.getElementById('chatContextMenu');
    if (chatMenu) chatMenu.classList.remove('active');
});

// Context Menu Actions (Placeholders for now)
// Context Menu Actions
window.shareChat = () => {
    const url = window.location.origin + "/api/sessions/" + activeContextSessionId;
    navigator.clipboard.writeText(url).then(() => {
        alert("Link copied to clipboard!\nNote: In production this would share a public view.");
    });
};

window.renameChatPrompt = async () => {
    const newName = prompt("Enter new name for chat:");
    if (!newName) return;

    try {
        const res = await fetch(`/api/sessions/${activeContextSessionId}/rename`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newName })
        });
        if (res.ok) {
            loadChatHistory();
        }
    } catch (e) { console.error(e); }
};

window.pinChat = async () => {
    try {
        const res = await fetch(`/api/sessions/${activeContextSessionId}/pin`, { method: 'POST' });
        if (res.ok) {
            loadChatHistory();
        }
    } catch (e) { console.error(e); }
};

window.deleteChat = async () => {
    if (!confirm("Are you sure you want to delete this chat?")) return;

    try {
        const res = await fetch(`/api/sessions/${activeContextSessionId}`, { method: 'DELETE' });
        if (res.ok) {
            if (currentSessionId === activeContextSessionId) {
                startNewChat();
            }
            loadChatHistory();
        }
    } catch (e) { console.error(e); }
};

// Search System Actions
window.toggleSearch = function () {
    const container = document.getElementById('searchContainer') || {};
    const input = document.getElementById('sidebarSearchInput') || {};
    isSearchActive = !isSearchActive;

    if (isSearchActive) {
        if (container.classList) container.classList.remove('hidden');
        if (input.focus) input.focus();
    } else {
        if (container.classList) container.classList.add('hidden');
        if (input) input.value = '';
        renderHistoryList(currentUserSessions); // Restore original list
    }
}

let searchTimeout;
window.handleSearch = function (query) {
    clearTimeout(searchTimeout);
    if (!query || query.trim().length === 0) {
        renderHistoryList(currentUserSessions);
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const res = await fetch(`/api/users/${currentUser.user_id}/search?q=${encodeURIComponent(query)}`);
            const results = await res.json();
            renderHistoryList(results, true);
        } catch (e) { console.error(e); }
    }, 300);
}
