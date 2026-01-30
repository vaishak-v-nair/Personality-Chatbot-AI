// ============================================
// MBTI Personality Chatbot - JavaScript
// ============================================

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInputField = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const sidebar = document.getElementById('sidebar');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');
const welcomeCard = document.getElementById('welcomeCard');
const chatCount = document.getElementById('chatCount');

// State
let messageCount = 0;
let isProcessing = false;

// ============================================
// INITIALIZATION
// ============================================

// Auto-resize textarea
userInputField.addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + 'px';
  sendBtn.disabled = this.value.trim() === '';
});

// Enter key handling
userInputField.addEventListener('keydown', function(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    if (!sendBtn.disabled && !isProcessing) {
      sendMessage();
    }
  }
});

// Initialize
sendBtn.disabled = true;

// ============================================
// SIDEBAR FUNCTIONS
// ============================================

function toggleSidebar() {
  sidebar.classList.toggle('open');
}

function startNewChat() {
  if (messageCount === 0) {
    showToast('Start chatting to begin!');
    return;
  }
  
  if (confirm('Start a new conversation? Current chat will be cleared.')) {
    chatMessages.innerHTML = '';
    welcomeCard.style.display = 'block';
    messageCount = 0;
    chatCount.textContent = '0';
    showToast('New conversation started');
  }
}

// ============================================
// TOAST NOTIFICATION
// ============================================

function showToast(message) {
  toastMessage.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// ============================================
// MESSAGE FUNCTIONS
// ============================================

// MBTI personality info
const personalityInfo = {
  'INTJ': { name: 'The Architect', color: '#667eea' },
  'INTP': { name: 'The Logician', color: '#764ba2' },
  'ENTJ': { name: 'The Commander', color: '#f093fb' },
  'ENTP': { name: 'The Debater', color: '#f5576c' },
  'INFJ': { name: 'The Advocate', color: '#4facfe' },
  'INFP': { name: 'The Mediator', color: '#00f2fe' },
  'ENFJ': { name: 'The Protagonist', color: '#43e97b' },
  'ENFP': { name: 'The Campaigner', color: '#38f9d7' },
  'ISTJ': { name: 'The Logistician', color: '#fa709a' },
  'ISFJ': { name: 'The Defender', color: '#fee140' },
  'ESTJ': { name: 'The Executive', color: '#30cfd0' },
  'ESFJ': { name: 'The Consul', color: '#a8edea' },
  'ISTP': { name: 'The Virtuoso', color: '#ff6e7f' },
  'ISFP': { name: 'The Adventurer', color: '#bfe9ff' },
  'ESTP': { name: 'The Entrepreneur', color: '#fbc2eb' },
  'ESFP': { name: 'The Entertainer', color: '#a6c1ee' }
};

function appendBotMessage(text, personalityType = null, isLoading = false) {
  // Hide welcome card on first message
  if (welcomeCard.style.display !== 'none') {
    welcomeCard.style.display = 'none';
  }

  const messageWrapper = document.createElement('div');
  messageWrapper.className = 'message-wrapper bot-message';

  let messageHTML = '';
  
  // Message Header
  messageHTML += `
    <div class="message-header">
      <div class="message-avatar">
        <span class="material-icons-round">smart_toy</span>
      </div>
      <span class="message-author">AI Assistant</span>
  `;
  
  if (personalityType && !isLoading) {
    const info = personalityInfo[personalityType] || { name: 'Unknown', color: '#667eea' };
    messageHTML += `
      <div class="personality-badge">
        <span class="material-icons-outlined" style="font-size: 12px;">auto_awesome</span>
        ${personalityType}
      </div>
    `;
  }
  
  messageHTML += `</div>`;

  // Message Bubble
  messageHTML += `<div class="message-bubble">`;
  
  if (isLoading) {
    messageHTML += `
      <div class="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;
  } else {
    messageHTML += escapeHtml(text);
  }
  
  messageHTML += `</div>`;

  // Message Actions (only if not loading)
  if (!isLoading) {
    const messageId = Date.now();
    messageHTML += `
      <div class="message-actions">
        <button class="action-btn" onclick="copyMessage(this, '${escapeForAttribute(text)}')" title="Copy">
          <span class="material-icons-outlined">content_copy</span>
        </button>
        <button class="action-btn" onclick="likeMessage(this, ${messageId}, true)" title="Helpful">
          <span class="material-icons-outlined">thumb_up</span>
        </button>
        <button class="action-btn" onclick="likeMessage(this, ${messageId}, false)" title="Not helpful">
          <span class="material-icons-outlined">thumb_down</span>
        </button>
      </div>
    `;
  }

  messageWrapper.innerHTML = messageHTML;
  chatMessages.appendChild(messageWrapper);
  scrollToBottom();
  
  return messageWrapper;
}

function appendUserMessage(text) {
  // Hide welcome card
  if (welcomeCard.style.display !== 'none') {
    welcomeCard.style.display = 'none';
  }

  const messageWrapper = document.createElement('div');
  messageWrapper.className = 'message-wrapper user-message';

  messageWrapper.innerHTML = `
    <div class="message-header">
      <span class="message-author">You</span>
      <div class="message-avatar">
        <span class="material-icons-round">person</span>
      </div>
    </div>
    <div class="message-bubble">${escapeHtml(text)}</div>
  `;

  chatMessages.appendChild(messageWrapper);
  scrollToBottom();
}

function scrollToBottom() {
  const container = document.querySelector('.chat-container');
  container.scrollTop = container.scrollHeight;
}

// ============================================
// SEND MESSAGE
// ============================================

async function sendMessage() {
  const text = userInputField.value.trim();
  if (text === '' || isProcessing) return;

  isProcessing = true;
  sendBtn.disabled = true;
  userInputField.disabled = true;

  // Add user message
  appendUserMessage(text);
  userInputField.value = '';
  userInputField.style.height = 'auto';

  // Show loading
  const loadingMessage = appendBotMessage(null, null, true);

  try {
    const response = await fetch('http://127.0.0.1:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text }),
    });

    if (!response.ok) throw new Error('Server error');
    const data = await response.json();

    // Remove loading message
    chatMessages.removeChild(loadingMessage);

    // Add bot response
    appendBotMessage(data.response, data.prediction);

    // Update stats
    messageCount++;
    chatCount.textContent = messageCount;

  } catch (error) {
    chatMessages.removeChild(loadingMessage);
    appendBotMessage(
      "I'm having trouble connecting to the server. Please make sure the backend is running on http://127.0.0.1:5000",
      null
    );
    console.error('Error:', error);
  } finally {
    isProcessing = false;
    userInputField.disabled = false;
    userInputField.focus();
  }
}

// Quick starter messages
function sendQuickMessage(message) {
  userInputField.value = message;
  sendBtn.disabled = false;
  sendMessage();
}

// ============================================
// MESSAGE ACTIONS
// ============================================

function copyMessage(button, text) {
  const decodedText = text.replace(/\\'/g, "'").replace(/\\"/g, '"');
  navigator.clipboard.writeText(decodedText).then(() => {
    showToast('Message copied to clipboard');
    
    // Visual feedback
    const originalHTML = button.innerHTML;
    button.innerHTML = '<span class="material-icons-outlined">check</span>';
    setTimeout(() => {
      button.innerHTML = originalHTML;
    }, 1500);
  }).catch(err => {
    console.error('Failed to copy:', err);
    showToast('Failed to copy message');
  });
}

function likeMessage(button, messageId, isLike) {
  const wasActive = button.classList.contains('active');
  
  // Remove active from both buttons in this group
  const actions = button.parentElement;
  actions.querySelectorAll('.action-btn').forEach(btn => {
    const icon = btn.querySelector('.material-icons-outlined');
    if (icon && (icon.textContent === 'thumb_up' || icon.textContent === 'thumb_down')) {
      btn.classList.remove('active');
    }
  });
  
  // Toggle active state
  if (!wasActive) {
    button.classList.add('active');
    showToast(isLike ? 'Thanks for your feedback!' : 'Feedback received');
  }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function escapeForAttribute(text) {
  return text
    .replace(/\\/g, '\\\\')
    .replace(/'/g, "\\'")
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n');
}

// ============================================
// PERSONALITY MODAL (Optional)
// ============================================

function showPersonalityModal(type) {
  const modal = document.getElementById('personalityModal');
  const info = personalityInfo[type];
  
  if (info) {
    document.getElementById('modalPersonalityType').textContent = type;
    document.getElementById('modalPersonalityName').textContent = info.name;
    modal.style.display = 'flex';
  }
}

function closePersonalityModal() {
  const modal = document.getElementById('personalityModal');
  modal.style.display = 'none';
}

// Close modal on outside click
window.addEventListener('click', function(event) {
  const modal = document.getElementById('personalityModal');
  if (event.target === modal) {
    closePersonalityModal();
  }
});

// Close sidebar on outside click (mobile)
document.addEventListener('click', function(event) {
  if (window.innerWidth <= 968) {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.querySelector('.btn-menu-toggle');
    
    if (sidebar.classList.contains('open') && 
        !sidebar.contains(event.target) && 
        !menuBtn.contains(event.target)) {
      sidebar.classList.remove('open');
    }
  }
});

// ============================================
// CONSOLE INFO
// ============================================

console.log('%c🎨 MBTI Personality Chatbot', 'color: #667eea; font-size: 20px; font-weight: bold;');
console.log('%cReady to chat! Type a message to get started.', 'color: #b4b4c8; font-size: 12px;');