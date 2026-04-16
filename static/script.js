const sessionId = crypto.randomUUID();
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const resetBtn = document.getElementById('reset-btn');

// Analysis Dashboard Elements
const sessionDisplay = document.getElementById('session-display');
const statusDisplay = document.getElementById('status-display');
const upiDisplay = document.getElementById('upi-display');
const phoneDisplay = document.getElementById('phone-display');
const bankDisplay = document.getElementById('bank-display');
const linkDisplay = document.getElementById('link-display');
const amountDisplay = document.getElementById('amount-display');
const nameDisplay = document.getElementById('name-display');
const addressDisplay = document.getElementById('address-display');
const reportBtn = document.getElementById('report-btn');

// Set Session ID
if (sessionDisplay) sessionDisplay.textContent = sessionId;

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    userInput.value = '';
    userInput.disabled = true;

    const typingId = addTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                message: text
            })
        });

        const data = await response.json();
        removeMessage(typingId);

        // 1. Show AI Response
        if (data.response) {
            addMessage(data.response, 'assistant');
        }

        // 2. Update Dashboard
        try {
            updateDashboard(data);
        } catch (dashError) {
            console.warn("Dashboard update failed:", dashError);
        }

    } catch (error) {
        console.error("Chat Error:", error);
        removeMessage(typingId);
        let errorMsg = "System Error: Connection unstable.";
        if (error.message) errorMsg += ` (${error.message})`;
        addMessage(errorMsg, "system");
    } finally {
        userInput.disabled = false;
        userInput.focus();
    }
}

function updateDashboard(data) {
    if (!upiDisplay) return; // Safety check

    const updateList = (element, items) => {
        if (!items || items.length === 0) {
            element.textContent = "-";
            element.classList.add('empty');
        } else {
            // Render as a clean list without bullets, just breaks
            element.innerHTML = items.map(i => `<div>${i}</div>`).join('');
            element.classList.remove('empty');
        }
    };

    if (data.extracted_info) {
        updateList(upiDisplay, data.extracted_info.upi_ids);
        updateList(phoneDisplay, data.extracted_info.phone_numbers);
        updateList(bankDisplay, data.extracted_info.bank_accounts);
        updateList(linkDisplay, data.extracted_info.sus_links);
        updateList(amountDisplay, data.extracted_info.amounts);
        updateList(nameDisplay, data.extracted_info.scammer_name);
        updateList(addressDisplay, data.extracted_info.scammer_address);
    }

    // Update Status
    if (statusDisplay) {
        statusDisplay.textContent = data.risk_level || "Monitoring...";
        if (data.risk_level === 'HIGH' || data.risk_level === 'CRITICAL') {
            statusDisplay.style.color = '#ef4444';
        } else {
            statusDisplay.style.color = '#00cc66';
        }
    }
}

// Generate Hackathon JSON
reportBtn.addEventListener('click', async () => {
    try {
        reportBtn.textContent = 'Generating...';
        const response = await fetch(`/api/results/${sessionId}`);
        if (!response.ok) throw new Error("Could not fetch json");
        const jsonOutput = await response.json();

        const jsonContainer = document.getElementById('json-output-containter');
        const jsonPre = document.getElementById('json-output');

        jsonPre.textContent = JSON.stringify(jsonOutput, null, 2);
        jsonContainer.style.display = 'block';

        reportBtn.textContent = '📄 Generate Hackathon JSON';
    } catch (e) {
        alert("Wait for the message to process before generating report.");
        reportBtn.textContent = '📄 Generate Hackathon JSON';
    }
});

resetBtn.addEventListener('click', async () => {
    if (confirm("Are you sure you want to clear this evidence?")) {
        await fetch(`/api/reset/${sessionId}`, { method: 'DELETE' });
        location.reload();
    }
});

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Reset button removed

function addMessage(text, role) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    div.innerHTML = `<div class="message-content">${text}</div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message assistant';
    div.innerHTML = `<div class="message-content">...</div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}
