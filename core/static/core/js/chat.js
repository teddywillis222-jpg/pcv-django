/**
 * Fichier JS principal pour la page de messagerie privée (Conversation)
 */

document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('messageInput');
    const chatForm = document.getElementById('chatForm');
    const fileInput = document.getElementById('fileInput');
    const header = document.querySelector('.chat-header');
    const inputArea = document.querySelector('.chat-input-area');
    const sendErrorBox = document.getElementById('chatSendError');
    const sendErrorText = document.getElementById('chatSendErrorText');
    const retryBtn = document.getElementById('chatRetryBtn');
    const config = window.chatConfig || {};
    let lastFailedPayload = null;

    function updateViewportHeight() {
        const viewportHeight = window.visualViewport ? window.visualViewport.height : window.innerHeight;
        document.documentElement.style.setProperty('--chat-viewport-height', `${Math.round(viewportHeight)}px`);
    }

    function updateLayoutHeights() {
        if (header) {
            document.documentElement.style.setProperty('--chat-header-height', `${header.offsetHeight}px`);
        }
        if (inputArea) {
            document.documentElement.style.setProperty('--chat-input-height', `${inputArea.offsetHeight}px`);
        }
    }

    function showSendError(message) {
        if (!sendErrorBox || !sendErrorText) return;
        sendErrorText.textContent = message;
        sendErrorBox.hidden = false;
        updateLayoutHeights();
    }

    function hideSendError() {
        if (!sendErrorBox) return;
        sendErrorBox.hidden = true;
        updateLayoutHeights();
    }

    async function submitMessage(payload = null) {
        if (!chatForm || !input) return;
        const text = payload ? payload.text : input.value.trim();
        const file = payload ? payload.file : (fileInput ? fileInput.files[0] : null);
        if (text === '' && !file) return;

        const sendBtn = chatForm.querySelector('.btn-send');
        if (sendBtn) sendBtn.disabled = true;

        try {
            const formData = new FormData();
            if (text) formData.append('texte', text);
            if (file) formData.append('fichier', file);

            const response = await fetch(config.urls.sendMessage, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': config.csrfToken
                }
            });

            let data = {};
            try {
                data = await response.json();
            } catch (parseError) {
                data = {};
            }

            if (response.ok) {
                if (data.message_id > config.lastMsgId) config.lastMsgId = data.message_id;
                appendMessageBubble(data.message_id, text, file, data.date);
                hideSendError();
                lastFailedPayload = null;

                input.value = '';
                input.style.height = 'auto';
                if (fileInput) fileInput.value = '';
                scrollToBottom();
                updateLayoutHeights();
                return;
            }

            if (response.status === 402) {
                showPaymentModal();
                return;
            }

            lastFailedPayload = { text, file };
            showSendError(data.error || "Envoi impossible pour le moment.");
        } catch (error) {
            console.error("Error:", error);
            lastFailedPayload = { text, file };
            showSendError("Erreur de connexion. Vérifiez le réseau puis renvoyez.");
        } finally {
            if (sendBtn) sendBtn.disabled = false;
        }
    }

    // 1. Initialisation UI
    updateViewportHeight();
    updateLayoutHeights();
    scrollToBottom();
    if (input) input.focus();

    window.addEventListener('resize', function () {
        updateViewportHeight();
        updateLayoutHeights();
    });
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', function () {
            updateViewportHeight();
            updateLayoutHeights();
        });
    }

    // 2. Gestion du Formulaire d'envoi de message
    if (chatForm) {
        chatForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            await submitMessage();
        });
    }

    if (retryBtn) {
        retryBtn.addEventListener('click', async function () {
            if (!lastFailedPayload) return;
            await submitMessage(lastFailedPayload);
        });
    }

    // Auto-resize textarea
    if (input) {
        input.addEventListener('input', function () {
            this.style.height = 'auto';
            if (this.scrollHeight <= 120) {
                this.style.height = (this.scrollHeight) + 'px';
            } else {
                this.style.height = '120px';
            }
            updateLayoutHeights();
        });

        input.addEventListener('focus', function () {
            setTimeout(function () {
                updateViewportHeight();
                updateLayoutHeights();
                scrollToBottom();
            }, 100);
        });
    }

    // Afficher nom de fichier sélectionné
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                if (input) input.placeholder = `Fichier joint: ${fileName} - Tapez un message...`;
            } else {
                if (input) input.placeholder = "Écrivez votre message...";
            }
            updateLayoutHeights();
        });
    }

    // 3. Polling AJAX pour nouveaux messages
    async function fetchNewMessages() {
        if (!config.urls || !config.urls.fetchMessages) return;

        try {
            const unreadElements = document.querySelectorAll('.msg-sent .msg-status:not(.status-read)');
            const unreadIds = Array.from(unreadElements).map(el => el.closest('.msg-bubble').getAttribute('data-id')).filter(id => id).join(',');

            const response = await fetch(`${config.urls.fetchMessages}?last_msg_id=${config.lastMsgId}&unread_ids=${unreadIds}`);
            if (!response.ok) return;
            const data = await response.json();

            let hasNew = false;

            if (data.messages && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    if (msg.id > config.lastMsgId) config.lastMsgId = msg.id;
                    const exists = document.querySelector(`.msg-bubble[data-id="${msg.id}"]`);
                    if (exists) return;

                    let fileContent = msg.file_name ? `<div class="msg-file" style="margin-bottom: 0.25rem;">📎 ${msg.file_name}</div>` : '';
                    let textContent = msg.text ? `<div class="msg-content">${msg.text}</div>` : '';

                    const container = document.getElementById('messagesList');
                    const bubble = document.createElement('div');
                    bubble.className = `msg-bubble msg-received`;
                    bubble.setAttribute('data-id', msg.id);
                    bubble.innerHTML = `
                        ${fileContent}
                        ${textContent}
                        <div class="msg-meta">
                            <span class="msg-time">${msg.date}</span>
                        </div>
                    `;
                    if (container) container.appendChild(bubble);
                    hasNew = true;
                });
            }

            if (data.newly_read && data.newly_read.length > 0) {
                data.newly_read.forEach(id => {
                    const bubble = document.querySelector(`.msg-sent[data-id="${id}"]`);
                    if (bubble) {
                        const icon = bubble.querySelector('.msg-status');
                        if (icon && !icon.classList.contains('status-read')) {
                            icon.classList.add('status-read');
                            icon.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                                                <path d="M18,7L16.59,5.58L10.24,11.93L11.66,13.34L18,7M16.59,15.41L12.41,11.24L11,12.66L16.59,18.25L22.25,12.59L20.84,11.17L16.59,15.41M1,12.59L6.59,18.18L8,16.77L2.41,11.17L1,12.59Z"/>
                                              </svg>`;
                        }
                    }
                });
            }

            if (hasNew) scrollToBottom();
            
            if (data.is_blocked !== config.isBlocked) {
                location.reload();
            }

        } catch (e) {
            console.error("Erreur Polling:", e);
        }
    }

    setInterval(fetchNewMessages, 5000);

    // Initialisation listener visio
    const revMode = document.getElementById('rev_mode');
    if (revMode) {
        revMode.addEventListener('change', function() {
            const visioContainer = document.getElementById('visio_platform_container');
            if (visioContainer) {
                visioContainer.style.display = (this.value === 'EN_LIGNE') ? 'block' : 'none';
            }
        });
    }

    // Close options dropdown on outside click
    window.addEventListener('click', function (event) {
        if (!event.target.closest('.btn-icon')) {
            const dropdown = document.getElementById('optionsDropdown');
            if (dropdown) dropdown.classList.remove('active');
        }
    });

});

// === UTILITAIRES UI ===
function scrollToBottom() {
    const container = document.getElementById('messagesList');
    if (container) container.scrollTop = container.scrollHeight;
}

function appendMessageBubble(id, text, file, date) {
    const container = document.getElementById('messagesList');
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble msg-sent';
    bubble.setAttribute('data-id', id);

    let contentHtml = '';
    if (file) {
        contentHtml += `<div class="msg-file" style="margin-bottom: 0.25rem; font-weight: 600;">📎 ${file.name}</div>`;
    }
    if (text) {
        contentHtml += `<div class="msg-content">${text.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>`;
    }

    bubble.innerHTML = `
        ${contentHtml}
        <div class="msg-meta">
            <span class="msg-time">${date}</span>
            <span class="msg-status">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                    <path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/>
                </svg>
            </span>
        </div>
    `;
    if (container) container.appendChild(bubble);
}

// === GESTION DES MODALES / SHEETS ===
function toggleOptions(event) {
    if (event) {
        event.stopPropagation();
    }
    const dropdown = document.getElementById('optionsDropdown');
    if (dropdown) dropdown.classList.toggle('active');
}

function toggleSheet() {
    const overlay = document.getElementById('engSheetOverlay');
    const sheet = document.getElementById('engSheet');
    if (overlay) overlay.classList.toggle('active');
    if (sheet) sheet.classList.toggle('active');
}

function toggleEngRow(header) {
    const row = header.closest('.eng-row');
    if(row) row.classList.toggle('active');
}

function filterEngagements() {
    const childId = document.getElementById('childFilter').value;
    const rows = document.querySelectorAll('.eng-row');
    rows.forEach(row => {
        if (childId === 'all' || row.getAttribute('data-child-id') === childId) {
            row.style.display = 'block';
        } else {
            row.style.display = 'none';
        }
    });
}

function showPaymentModal() {
    const modal = document.getElementById('paymentModal');
    const sheet = document.getElementById('paymentSheet');
    if (modal) modal.classList.add('active');
    if (sheet) sheet.classList.add('active');
}

function hidePaymentModal() {
    const modal = document.getElementById('paymentModal');
    const sheet = document.getElementById('paymentSheet');
    if (modal) modal.classList.remove('active');
    if (sheet) sheet.classList.remove('active');
}

function showEngReviewModal() {
    const modal = document.getElementById('engReviewModal');
    if (modal) modal.style.display = 'flex';
}

function hideEngReviewModal() {
    const modal = document.getElementById('engReviewModal');
    if (modal) modal.style.display = 'none';
}

// === LOGIQUE METIER (Paiement, Engagements) ===
let selectedPlan = 'standard';
function selectPlan(plan) {
    selectedPlan = plan;
    const stdPlan = document.querySelector('[onclick="selectPlan(\'standard\')"]');
    const prmPlan = document.querySelector('[onclick="selectPlan(\'premium\')"]');
    
    if(stdPlan && prmPlan) {
        stdPlan.style.borderColor = (plan === 'standard') ? '#15803d' : '#e2e8f0';
        stdPlan.style.background = (plan === 'standard') ? '#f0fdf4' : 'white';
        prmPlan.style.borderColor = (plan === 'premium') ? '#15803d' : '#e2e8f0';
        prmPlan.style.background = (plan === 'premium') ? '#f0fdf4' : 'white';
    }
}

async function processFictionalPayment() {
    const btn = document.getElementById('confirmPaymentBtn');
    if(!btn) return;
    btn.disabled = true;
    btn.innerText = "Traitement en cours...";

    try {
        const config = window.chatConfig;
        const response = await fetch(config.urls.fictionalPayment, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': config.csrfToken
            },
            body: JSON.stringify({
                conversation_id: config.conversationId,
                payment_type: selectedPlan
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || "Paiement réussi !");
            location.reload();
        } else {
            alert(data.error || "Erreur lors du paiement fictif");
            btn.disabled = false;
            btn.innerText = "Continuer vers le paiement";
        }
    } catch (e) {
        console.error(e);
        alert("Erreur de connexion au serveur.");
        btn.disabled = false;
        btn.innerText = "Continuer vers le paiement";
    }
}

function finalizeEngagement(engId) {
    if (!engId) {
        engId = document.getElementById('rev_id').value;
    }
    if (!engId) return alert("Aucun engagement sélectionné.");

    if (!confirm("Voulez-vous finaliser cet engagement ? Cette action est irréversible.")) return;

    fetch(`/api/engagement/${engId}/finalize/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': window.chatConfig.csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.error || "Erreur lors de la finalisation.");
        }
    })
    .catch(err => console.error("Erreur:", err));
}

function updateEngagement() {
    const engId = document.getElementById('rev_id').value;
    if (!engId) return alert("Aucun engagement sélectionné.");

    const payload = {
        enfant_id: document.getElementById('rev_enfant') ? document.getElementById('rev_enfant').value : null,
        matiere: document.getElementById('rev_matiere').value,
        classe: document.getElementById('rev_classe').value,
        mode: document.getElementById('rev_mode').value,
        budget: document.getElementById('rev_budget').value,
        frequence: document.getElementById('rev_frequence').value,
        duree_seance: document.getElementById('rev_duree').value,
        duree_mois: document.getElementById('rev_duree_mois').value,
        periode: document.getElementById('rev_periode').value,
        localisation: document.getElementById('rev_localisation').value,
        visio: document.getElementById('rev_visio').value
    };

    fetch(`/api/engagement/${engId}/update/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': window.chatConfig.csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            hideEngReviewModal();
            location.reload();
        } else {
            alert(data.error || "Erreur lors de la mise à jour.");
        }
    })
    .catch(err => console.error("Erreur:", err));
}

function showEditProposal(engId, isOngoing = false) {
    const modal = document.getElementById('engReviewModal');
    if (!modal) return;

    const row = document.querySelector(`.eng-row[data-eng-json*='"id": ${engId},']`) || document.querySelector(`.eng-row[data-eng-json*='"id": ${engId}}']`);
    if (!row) return alert("Données introuvables.");

    const data = JSON.parse(row.getAttribute('data-eng-json'));
    
    document.getElementById('rev_id').value = engId;
    document.getElementById('rev_title').textContent = isOngoing ? "Détails de l'engagement" : "Modifier ma proposition";

    if (document.getElementById('rev_enfant')) {
        document.getElementById('rev_enfant').value = data.enfant_id || "";
    } else if (document.getElementById('rev_student_display')) {
        document.getElementById('rev_student_display').value = data.student_name || "Non précisé";
    }
    
    document.getElementById('rev_matiere').value = data.matiere;
    document.getElementById('rev_classe').value = data.classe;
    document.getElementById('rev_mode').value = data.mode_raw || data.mode;
    document.getElementById('rev_budget').value = data.budget;
    document.getElementById('rev_frequence').value = data.frequence_raw || data.frequence;
    document.getElementById('rev_duree').value = data.duree_raw || data.duree;
    document.getElementById('rev_duree_mois').value = data.duree_mois || "";
    document.getElementById('rev_periode').value = data.periode_raw || data.periode;
    document.getElementById('rev_localisation').value = data.localisation || data.lieu;
    document.getElementById('rev_visio').value = data.visio || data.plateforme;

    const visioContainer = document.getElementById('visio_platform_container');
    if (visioContainer) {
        visioContainer.style.display = (data.mode === 'EN_LIGNE') ? 'block' : 'none';
    }

    const btnFinalize = document.getElementById('btn_modal_finalize');
    if (isOngoing && btnFinalize) {
        btnFinalize.style.display = 'block';
        if (window.chatConfig.isEligibleToFinalize === false) {
            btnFinalize.disabled = true;
            btnFinalize.classList.add('btn-dash-disabled');
        }
    } else if (btnFinalize) {
        btnFinalize.style.display = 'none';
    }

    modal.style.display = 'flex';

    const sheetOverlay = document.getElementById('engSheetOverlay');
    const sheet = document.getElementById('engSheet');
    if (sheetOverlay) sheetOverlay.classList.remove('active');
    if (sheet) sheet.classList.remove('active');
}
