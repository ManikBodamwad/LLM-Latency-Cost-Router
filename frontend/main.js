const chatMessages = document.getElementById('chat-messages');
const promptInput = document.getElementById('prompt-input');
const sendBtn = document.getElementById('send-btn');

// Metrics DOM elements
const elStatus = document.querySelector('.id-status');
const elLatency = document.querySelector('.id-latency');
const elCost = document.querySelector('.id-cost');
const elTier = document.querySelector('.id-tier');
const elModel = document.querySelector('.id-model');

// Cards
const cardStatus = document.getElementById('card-status');
const cardLatency = document.getElementById('card-latency');
const cardCost = document.getElementById('card-cost');
const cardTier = document.getElementById('card-tier');
const cardModel = document.getElementById('card-model');

const API_URL = "http://localhost:8000/api/v1/chat/completions";

function addMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.innerHTML = role === 'user' ? '<i class="ph-fill ph-user"></i>' : '<i class="ph-fill ph-robot"></i>';
    
    const textContent = document.createElement('div');
    textContent.className = 'content';
    // Use marked library to parse markdown cleanly into HTML
    textContent.innerHTML = typeof marked !== 'undefined' ? marked.parse(content) : content;
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(textContent);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return msgDiv;
}

function updateTelemetry(data) {
    const isCacheHit = data.used_model === 'cache';
    
    // Update Text
    elStatus.textContent = isCacheHit ? 'CACHE HIT (0ms Network)' : 'LIVE QUERY';
    elStatus.style.color = isCacheHit ? '#10B981' : '#38BDF8';
    
    elLatency.textContent = data.latency;
    elCost.textContent = data.cost_usd.toFixed(6);
    elTier.textContent = data.tier.toUpperCase();
    elModel.textContent = data.used_model;
    
    // Trigger Card Animations
    const cards = [cardStatus, cardLatency, cardCost, cardTier, cardModel];
    cards.forEach(card => {
        card.classList.remove('card-flash', 'success-border');
        // trigger reflow
        void card.offsetWidth;
        card.classList.add('card-flash');
        if (isCacheHit) card.classList.add('success-border');
    });
}

async function handleSend() {
    const text = promptInput.value.trim();
    if (!text) return;
    
    // Add user message
    addMessage('user', text);
    promptInput.value = '';
    
    // Show typing
    const typingMsg = addMessage('assistant', '<div class="typing-indicator"><span></span><span></span><span></span></div>');
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': 'demo_super_secret_key'
            },
            body: JSON.stringify({ prompt: text, stream: false })
        });
        
        if (!response.ok) {
            if (response.status === 429) {
                throw new Error("Rate Limit Exceeded (HTTP 429). Blocked by Redis Token Bucket.");
            }
            throw new Error(`HTTP Error ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove typing indicator & show actual text
        typingMsg.remove();
        addMessage('assistant', data.response);
        
        // Update the SRE Dashboard!
        updateTelemetry(data);
        
    } catch (error) {
        typingMsg.remove();
        addMessage('assistant', `<span style="color: #ef4444;">Gateway Error: ${error.message}</span>`);
    }
}

sendBtn.addEventListener('click', handleSend);
promptInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
});
