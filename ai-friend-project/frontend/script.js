let profileId = null;

// 1. Initial Profile Setup
async function createProfile() {
    const userName = document.getElementById('user-name').value;
    const botGender = document.getElementById('bot-gender').value; // MATCHED TO HTML
    const botName = document.getElementById('bot-name').value;

    if (!userName || !botName) {
        alert("Please enter both your name and a name for your AI friend!");
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:8000/create-profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                user_name: userName, 
                user_gender: botGender, // Backend expects 'user_gender'
                bot_name: botName 
            })
        });

        if (!response.ok) throw new Error("Backend connection failed");

        const data = await response.json();
        profileId = data.profile.id;

        // Switch screens
        document.getElementById('display-bot-name').innerText = botName;
        document.getElementById('setup-screen').classList.add('hidden');
        document.getElementById('chat-screen').classList.remove('hidden');

        appendMessage('bot', `Hey ${userName}! I'm ${botName}. I'm so glad we finally get to talk. What's on your mind?`);
    } catch (error) {
        console.error("Setup Error:", error);
        alert("Server error! Make sure your Python backend is running.");
    }
}

// 2. Send Message Logic
async function sendMessage() {
    const input = document.getElementById('message-input');
    const msg = input.value.trim();
    const botName = document.getElementById('display-bot-name').innerText;

    if (!msg || !profileId) return;

    appendMessage('user', msg);
    input.value = '';

    // Thinking indicator
    showThinking(botName);

    try {
        const response = await fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile_id: profileId, user_message: msg })
        });

        removeThinking();

        if (!response.ok) throw new Error("Busy");

        const data = await response.json();
        appendMessage('bot', data.bot_reply);

    } catch (error) {
        removeThinking();
        appendRetryButton("The AI is experiencing high traffic.", () => {
            input.value = msg;
            sendMessage();
        });
    }
}

// 3. UI Helpers
function appendMessage(sender, text) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = sender === 'user' ? 'text-right mb-4' : 'text-left mb-4';
    
    let bubbleClass = sender === 'user' ? 'bg-cyan-600 text-white' : 'bg-gray-800 text-gray-100';
    let actionButtons = '';
    
    if (sender === 'bot') {
        actionButtons = `<button onclick="generateScene(this)" data-reply="${text.replace(/"/g, '&quot;')}" class="block mt-2 text-xs italic text-gray-400 hover:text-cyan-400 transition-colors">✨ Generate Scene</button>`;
    }

    msgDiv.innerHTML = `
        <div class="inline-block max-w-[85%] p-3 rounded-2xl ${bubbleClass} shadow-lg border ${sender === 'user' ? 'border-cyan-500' : 'border-gray-700'}">
            ${text}
            ${actionButtons}
        </div>
    `;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showThinking(name) {
    const chatBox = document.getElementById('chat-box');
    const thinkingDiv = document.createElement('div');
    thinkingDiv.id = 'thinking-indicator';
    thinkingDiv.className = 'text-left mb-4 animate-pulse';
    thinkingDiv.innerHTML = `<span class="inline-block p-3 rounded-2xl bg-gray-800 text-gray-400 italic">${name} is typing...</span>`;
    chatBox.appendChild(thinkingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeThinking() {
    const indicator = document.getElementById('thinking-indicator');
    if (indicator) indicator.remove();
}

function appendRetryButton(errorText, retryFunc) {
    const chatBox = document.getElementById('chat-box');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-left mb-4';
    errorDiv.innerHTML = `
        <div class="inline-block p-3 rounded-2xl bg-red-900/20 border border-red-500/50 text-gray-200">
            <p class="text-sm">⚠️ ${errorText}</p>
            <button class="retry-btn mt-2 text-xs font-bold uppercase text-red-400 hover:text-red-300">🔄 Click to Retry</button>
        </div>
    `;
    errorDiv.querySelector('.retry-btn').onclick = () => {
        errorDiv.remove();
        retryFunc();
    };
    chatBox.appendChild(errorDiv);
}

// 4. Image Generation
async function generateScene(button) {
    const botReplyText = button.getAttribute('data-reply');
    button.innerText = "⏳ Painting...";
    button.disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:8000/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ profile_id: profileId, bot_reply: botReplyText })
        });

        if (!response.ok) throw new Error("Image Busy");

        const data = await response.json();
        appendImage(data.image_url);
        button.innerText = "Regenerate ✨";
        button.disabled = false;

    } catch (error) {
        button.innerText = "🔄 Busy. Retry?";
        button.disabled = false;
        button.classList.add("text-red-400");
    }
}

function appendImage(url) {
    const chatBox = document.getElementById('chat-box');
    const imgDiv = document.createElement('div');
    imgDiv.className = 'text-left mb-4';
    imgDiv.innerHTML = `<div class="p-1 bg-gray-800 rounded-xl border border-gray-700 shadow-2xl inline-block"><img src="${url}" class="w-64 h-auto rounded-lg"></div>`;
    chatBox.appendChild(imgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Enter Key Handler
function checkEnter(event) {
    if (event.key === "Enter") sendMessage();
}