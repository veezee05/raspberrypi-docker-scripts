const CONFIG = {
    pollingInterval: 500
};

const UI = {
    heading: document.getElementById('status-heading'),
    message: document.getElementById('status-message'),
    icon: document.getElementById('main-icon'),
    visual: document.getElementById('visual-container'),
    detailsCard: document.getElementById('details-card'),
    receiptCard: document.getElementById('receipt-card'),
    
    // User data fields
    userName: document.getElementById('user-name'),
    userEntitlement: document.getElementById('user-entitlement'),
    txId: document.getElementById('tx-id')
};

let lastStatus = "";

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        renderState(data);
    } catch (e) {
        console.error("Connection Error:", e);
    }
}

function renderState(data) {
    // Avoid re-rendering if status hasn't truly changed logic (optimization)
    // But we need to be careful about data updates within same status
    
    const { status, message, user_data, tx_id } = data;

    // Update Text
    UI.heading.innerText = getHeadingForStatus(status);
    UI.message.innerText = message;

    // Update Visuals
    updateVisuals(status);

    // Update Cards
    if (status === 'AUTH_SUCCESS' || status === 'DISPENSING') {
        UI.detailsCard.classList.remove('hidden');
        UI.receiptCard.classList.add('hidden');
        
        if (user_data) {
            UI.userName.innerText = user_data.name || 'Beneficiary';
            UI.userEntitlement.innerText = (user_data.entitlement || '--') + ' kg';
        }
    } else if (status === 'COMPLETED') {
        UI.detailsCard.classList.add('hidden');
        UI.receiptCard.classList.remove('hidden');
        if (tx_id) {
            UI.txId.innerText = tx_id;
        }
    } else {
        UI.detailsCard.classList.add('hidden');
        UI.receiptCard.classList.add('hidden');
    }
}

function getHeadingForStatus(status) {
    switch (status) {
        case 'IDLE': return "Welcome";
        case 'PROCESSING': return "Verifying...";
        case 'AUTH_SUCCESS': return "Authorized";
        case 'AUTH_FAILED': return "Access Denied";
        case 'DISPENSING': return "Dispensing";
        case 'COMPLETED': return "Success";
        case 'ERROR': return "System Error";
        default: return "System Status";
    }
}

function updateVisuals(status) {
    UI.visual.className = 'visual-container'; // reset
    
    switch (status) {
        case 'IDLE':
            UI.icon.innerText = "👋"; // Wave
            break;
        case 'PROCESSING':
            UI.icon.innerText = "⏳"; // Hourglass
            UI.visual.classList.add('processing');
            break;
        case 'AUTH_SUCCESS':
            UI.icon.innerText = "🔓"; // Unlock
            break;
        case 'AUTH_FAILED':
            UI.icon.innerText = "❌"; // Cross
            UI.visual.classList.add('error');
            break;
        case 'DISPENSING':
            UI.icon.innerText = "🌾"; // Grain
            UI.visual.classList.add('processing'); // Pulse while dispensing
            break;
        case 'COMPLETED':
            UI.icon.innerText = "✅"; // Check
            break;
        case 'ERROR':
            UI.icon.innerText = "⚠️"; // Warning
            UI.visual.classList.add('error');
            break;
    }
}

// Start Loop
setInterval(fetchStatus, CONFIG.pollingInterval);

// --- Keyboard Debug Trigger (Hidden feature for testing) ---
// Press 'F' to simulate fingerprint scan
document.addEventListener('keydown', (e) => {
    if (e.key === 'f' || e.key === 'F') {
        fetch('/api/trigger/fingerprint', { method: 'POST' });
    }
});
