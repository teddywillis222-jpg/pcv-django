/**
 * chat.js — ProfChezVous
 * Messagerie privée : envoi, polling, UI — Version refonte complète
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── Éléments DOM ────────────────────────────────────────
    const input        = document.getElementById('messageInput');
    const chatForm     = document.getElementById('chatForm');
    const fileInput    = document.getElementById('fileInput');
    const sendErrorBox = document.getElementById('chatSendError');
    const sendErrorTxt = document.getElementById('chatSendErrorText');
    const retryBtn     = document.getElementById('chatRetryBtn');
    const config       = window.chatConfig || {};
    let lastFailedPayload = null;

    // ── Hauteur dynamique viewport (clavier mobile) ──────────
    function setVh() {
        const vh = window.visualViewport
            ? window.visualViewport.height * 0.01
            : window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    setVh();
    window.addEventListener('resize', setVh);
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', setVh);
        window.visualViewport.addEventListener('scroll', setVh);
    }

    // ── Scroll au bas ────────────────────────────────────────
    scrollToBottom();

    // ── Feedback erreur envoi ────────────────────────────────
    function showSendError(msg) {
        if (!sendErrorBox || !sendErrorTxt) return;
        sendErrorTxt.textContent = msg;
        sendErrorBox.hidden = false;
    }
    function hideSendError() {
        if (sendErrorBox) sendErrorBox.hidden = true;
    }
    hideSendError();

    // ── Envoi de message ─────────────────────────────────────
    async function submitMessage(payload = null) {
        if (!chatForm || !input) return;
        const text = payload ? payload.text : input.value.trim();
        const file = payload ? payload.file : (fileInput ? fileInput.files[0] : null);
        if (!text && !file) return;

        const sendBtn = document.getElementById('sendBtn') || chatForm.querySelector('.btn-send');
        if (sendBtn) sendBtn.disabled = true;

        // Bulle optimiste (envoi immédiat)
        const tempId = 'temp-' + Date.now();
        appendSentBubble(tempId, text, file, '…');

        try {
            const fd = new FormData();
            if (text) fd.append('texte', text);
            if (file) fd.append('fichier', file);

            const res = await fetch(config.urls.sendMessage, {
                method: 'POST',
                body: fd,
                headers: { 'X-CSRFToken': config.csrfToken }
            });

            let data = {};
            try { data = await res.json(); } catch (_) {}

            if (res.ok) {
                // Mettre à jour la bulle optimiste avec l'ID réel
                const tmpBubble = document.querySelector(`[data-id="${tempId}"]`);
                if (tmpBubble) {
                    tmpBubble.setAttribute('data-id', data.message_id);
                    const timeEl = tmpBubble.querySelector('.msg-time');
                    if (timeEl) timeEl.textContent = data.date || new Date().toLocaleTimeString('fr-FR', {hour:'2-digit', minute:'2-digit'});
                    tmpBubble.style.opacity = '1';
                }
                if (data.message_id > config.lastMsgId) config.lastMsgId = data.message_id;
                hideSendError();
                lastFailedPayload = null;
                input.value = '';
                input.style.height = 'auto';
                if (fileInput) { fileInput.value = ''; input.placeholder = 'Écrivez un message…'; }
                scrollToBottom();
                return;
            }

            // Échec : retirer la bulle optimiste
            removeBubble(tempId);

            if (res.status === 402) {
                showPaymentModal();
                return;
            }

            lastFailedPayload = { text, file };
            showSendError(data.error || 'Envoi impossible pour le moment.');
        } catch (e) {
            console.error('[Chat] Erreur envoi:', e);
            removeBubble(tempId);
            lastFailedPayload = { text, file };
            showSendError('Erreur de connexion. Vérifiez le réseau puis renvoyez.');
        } finally {
            if (sendBtn) sendBtn.disabled = false;
        }
    }

    // ── Formulaire submit ────────────────────────────────────
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await submitMessage();
        });
    }

    if (retryBtn) {
        retryBtn.addEventListener('click', async () => {
            if (!lastFailedPayload) return;
            await submitMessage(lastFailedPayload);
        });
    }

    // ── Textarea auto-resize ─────────────────────────────────
    if (input) {
        input.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // Sur iOS : scroll to bottom quand le clavier apparaît
        input.addEventListener('focus', function () {
            setTimeout(() => scrollToBottom(), 200);
        });
    }

    // ── Fichier joint : feedback ─────────────────────────────
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            if (this.files.length > 0 && input) {
                input.placeholder = `📎 ${this.files[0].name} — Ajouter un message…`;
            } else if (input) {
                input.placeholder = 'Écrivez un message…';
            }
        });
    }

    // ── Polling AJAX avec pause si onglet inactif ────────────
    let pollingInterval = null;

    async function fetchNewMessages() {
        if (!config.urls?.fetchMessages) return;

        try {
            const unreadEls = document.querySelectorAll('.msg-sent .msg-status:not(.status-read)');
            const unreadIds = Array.from(unreadEls)
                .map(el => el.closest('.msg-bubble')?.getAttribute('data-id'))
                .filter(Boolean)
                .join(',');

            const url = `${config.urls.fetchMessages}?last_msg_id=${config.lastMsgId}&unread_ids=${unreadIds}`;
            const res = await fetch(url);
            if (!res.ok) return;
            const data = await res.json();

            // Nouveaux messages reçus
            if (data.messages?.length > 0) {
                let hasNew = false;
                const container = document.getElementById('messagesList');
                data.messages.forEach(msg => {
                    if (msg.id > config.lastMsgId) config.lastMsgId = msg.id;
                    if (document.querySelector(`.msg-bubble[data-id="${msg.id}"]`)) return;

                    const bubble = document.createElement('div');
                    bubble.className = 'msg-bubble msg-received';
                    bubble.setAttribute('data-id', msg.id);

                    let html = '';
                    if (msg.file_name) {
                        html += `<div class="msg-file">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                            ${msg.file_name}
                        </div>`;
                    }
                    if (msg.text) {
                        html += `<div class="msg-content">${escapeHtml(msg.text)}</div>`;
                    }
                    html += `<div class="msg-meta"><span class="msg-time">${msg.date}</span></div>`;
                    bubble.innerHTML = html;

                    if (container) container.appendChild(bubble);
                    hasNew = true;
                });
                if (hasNew) scrollToBottom();
            }

            // Mise à jour statut lu
            if (data.newly_read?.length > 0) {
                data.newly_read.forEach(id => {
                    const bubble = document.querySelector(`.msg-sent[data-id="${id}"]`);
                    if (!bubble) return;
                    const icon = bubble.querySelector('.msg-status');
                    if (icon && !icon.classList.contains('status-read')) {
                        icon.classList.add('status-read');
                        icon.innerHTML = `<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M18,7L16.59,5.58L10.24,11.93L11.66,13.34L18,7M16.59,15.41L12.41,11.24L11,12.66L16.59,18.25L22.25,12.59L20.84,11.17L16.59,15.41M1,12.59L6.59,18.18L8,16.77L2.41,11.17L1,12.59Z"/></svg>`;
                    }
                });
            }

            // Blocage activé dynamiquement
            if (data.is_blocked && !config.isBlocked) {
                location.reload();
            }

        } catch (e) {
            console.warn('[Chat] Erreur polling:', e);
        }
    }

    function startPolling() {
        if (pollingInterval) return;
        fetchNewMessages(); // fetch immédiat au retour
        pollingInterval = setInterval(fetchNewMessages, 5000);
    }

    function stopPolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }

    // Démarrage + pause selon visibilité de l'onglet
    startPolling();
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stopPolling();
        } else {
            startPolling();
        }
    });

    // ── Fermeture dropdown options au clic extérieur ─────────
    window.addEventListener('click', (e) => {
        if (!e.target.closest('#optionsBtn') && !e.target.closest('#optionsDropdown')) {
            const dd = document.getElementById('optionsDropdown');
            if (dd) dd.classList.remove('active');
        }
    });

    // ── Init listener mode visio ─────────────────────────────
    const revMode = document.getElementById('rev_mode');
    if (revMode) {
        revMode.addEventListener('change', function () {
            const c = document.getElementById('visio_platform_container');
            if (c) c.style.display = (this.value === 'EN_LIGNE') ? 'block' : 'none';
        });
    }

}); // end DOMContentLoaded


// ════════════════════════════════════════════════════════════
//  UTILITAIRES UI
// ════════════════════════════════════════════════════════════

function scrollToBottom() {
    const c = document.getElementById('messagesList');
    if (c) c.scrollTop = c.scrollHeight;
}

function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function appendSentBubble(id, text, file, time) {
    const container = document.getElementById('messagesList');
    if (!container) return;

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble msg-sent';
    bubble.setAttribute('data-id', id);
    bubble.style.opacity = '0.75';
    bubble.style.transition = 'opacity 0.2s';

    let html = '';
    if (file) {
        html += `<div class="msg-file">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
            ${escapeHtml(file.name)}
        </div>`;
    }
    if (text) {
        html += `<div class="msg-content">${escapeHtml(text)}</div>`;
    }
    html += `<div class="msg-meta">
        <span class="msg-time">${time}</span>
        <span class="msg-status">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z"/></svg>
        </span>
    </div>`;
    bubble.innerHTML = html;
    container.appendChild(bubble);
    scrollToBottom();
}

function removeBubble(id) {
    const b = document.querySelector(`[data-id="${id}"]`);
    if (b) b.remove();
}


// ════════════════════════════════════════════════════════════
//  GESTION DES MODALES / SHEETS
// ════════════════════════════════════════════════════════════

function toggleOptions(e) {
    if (e) e.stopPropagation();
    const dd = document.getElementById('optionsDropdown');
    if (dd) dd.classList.toggle('active');
}

function toggleSheet() {
    const overlay = document.getElementById('engSheetOverlay');
    const sheet   = document.getElementById('engSheet');
    if (overlay) overlay.classList.toggle('active');
    if (sheet)   sheet.classList.toggle('active');
}

function toggleEngRow(header) {
    const row = header.closest('.eng-row');
    if (row) row.classList.toggle('active');
}

function filterEngagements() {
    const childId = document.getElementById('childFilter')?.value;
    document.querySelectorAll('.eng-row').forEach(row => {
        row.style.display = (!childId || childId === 'all' || row.getAttribute('data-child-id') === childId)
            ? 'block' : 'none';
    });
}

// ── Modal Paiement ───────────────────────────────────────────
function showPaymentModal() {
    const overlay = document.getElementById('paymentModalOverlay');
    const modal   = document.getElementById('paymentModal');
    const sheet   = document.getElementById('paymentSheet');
    if (overlay) { overlay.classList.add('active'); overlay.style.display = 'flex'; }
    if (modal)   { modal.style.display = 'flex'; modal.style.pointerEvents = 'all'; }
    if (sheet)   { requestAnimationFrame(() => sheet.style.transform = 'translateY(0)'); }
}

function hidePaymentModal() {
    const overlay = document.getElementById('paymentModalOverlay');
    const modal   = document.getElementById('paymentModal');
    const sheet   = document.getElementById('paymentSheet');
    if (sheet) {
        sheet.style.transform = 'translateY(100%)';
        setTimeout(() => {
            if (modal) { modal.style.display = 'none'; modal.style.pointerEvents = 'none'; }
            if (overlay) { overlay.classList.remove('active'); overlay.style.display = 'none'; }
        }, 300);
    } else {
        if (modal) { modal.style.display = 'none'; }
        if (overlay) { overlay.classList.remove('active'); }
    }
}

// ── Modal Engagement ─────────────────────────────────────────
function showEngReviewModal() {
    const modal = document.getElementById('engReviewModal');
    if (modal) modal.classList.add('active');
}

function hideEngReviewModal() {
    const modal = document.getElementById('engReviewModal');
    if (modal) modal.classList.remove('active');
}

// ── Sélection du plan ────────────────────────────────────────
let selectedPlan = 'standard';
function selectPlan(plan) {
    selectedPlan = plan;
    const std = document.getElementById('planStandard');
    const prm = document.getElementById('planPremium');
    if (std) std.classList.toggle('selected', plan === 'standard');
    if (prm) prm.classList.toggle('selected', plan === 'premium');
}

// ── Paiement fictif ──────────────────────────────────────────
async function processFictionalPayment() {
    const btn = document.getElementById('confirmPaymentBtn');
    if (!btn) return;
    btn.disabled = true;
    btn.textContent = 'Traitement en cours…';

    try {
        const config = window.chatConfig;
        const res = await fetch(config.urls.fictionalPayment, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': config.csrfToken },
            body: JSON.stringify({ conversation_id: config.conversationId, payment_type: selectedPlan })
        });
        const data = await res.json();
        if (res.ok) {
            hidePaymentModal();
            location.reload();
        } else {
            alert(data.error || 'Erreur lors du paiement fictif');
            btn.disabled = false;
            btn.textContent = 'Continuer vers le paiement';
        }
    } catch (e) {
        console.error(e);
        alert('Erreur de connexion au serveur.');
        btn.disabled = false;
        btn.textContent = 'Continuer vers le paiement';
    }
}

// ── Finaliser engagement ─────────────────────────────────────
function finalizeEngagement(engId) {
    if (!engId) engId = document.getElementById('rev_id')?.value;
    if (!engId) return alert('Aucun engagement sélectionné.');
    if (!confirm('Voulez-vous finaliser cet engagement ? Cette action est irréversible.')) return;

    fetch(`/api/engagement/${engId}/finalize/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': window.chatConfig.csrfToken, 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) location.reload();
        else alert(data.error || 'Erreur lors de la finalisation.');
    })
    .catch(e => console.error(e));
}

// ── Mettre à jour engagement ─────────────────────────────────
function updateEngagement() {
    const engId = document.getElementById('rev_id')?.value;
    if (!engId) return alert('Aucun engagement sélectionné.');

    const get = id => document.getElementById(id)?.value ?? null;
    const payload = {
        enfant_id:  get('rev_enfant'),
        matiere:    get('rev_matiere'),
        classe:     get('rev_classe'),
        mode:       get('rev_mode'),
        budget:     get('rev_budget'),
        frequence:  get('rev_frequence'),
        duree_seance: get('rev_duree'),
        duree_mois: get('rev_duree_mois'),
        periode:    get('rev_periode'),
        localisation: get('rev_localisation'),
        visio:      get('rev_visio'),
    };

    fetch(`/api/engagement/${engId}/update/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': window.chatConfig.csrfToken, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) { hideEngReviewModal(); location.reload(); }
        else alert(data.error || 'Erreur lors de la mise à jour.');
    })
    .catch(e => console.error(e));
}

// ── Ouvrir modal édition engagement ─────────────────────────
function showEditProposal(engId, isOngoing = false) {
    const modal = document.getElementById('engReviewModal');
    if (!modal) return;

    const row = document.querySelector(`.eng-row[data-eng-json*='"id": ${engId},']`)
             || document.querySelector(`.eng-row[data-eng-json*='"id": ${engId}}']`);
    if (!row) return alert('Données introuvables.');

    const data = JSON.parse(row.getAttribute('data-eng-json'));

    document.getElementById('rev_id').value = engId;
    document.getElementById('rev_title').textContent = isOngoing
        ? "Détails de l'engagement"
        : "Modifier ma proposition";

    const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
    if (document.getElementById('rev_enfant'))         setVal('rev_enfant', data.enfant_id);
    else if (document.getElementById('rev_student_display')) setVal('rev_student_display', data.student_name || 'Non précisé');

    setVal('rev_matiere',    data.matiere);
    setVal('rev_classe',     data.classe);
    setVal('rev_mode',       data.mode_raw   || data.mode);
    setVal('rev_budget',     data.budget);
    setVal('rev_frequence',  data.frequence_raw || data.frequence);
    setVal('rev_duree',      data.duree_raw   || data.duree);
    setVal('rev_duree_mois', data.duree_mois);
    setVal('rev_periode',    data.periode_raw  || data.periode);
    setVal('rev_localisation', data.localisation || data.lieu);
    setVal('rev_visio',      data.visio || data.plateforme);

    const visioC = document.getElementById('visio_platform_container');
    if (visioC) visioC.style.display = (data.mode === 'EN_LIGNE') ? 'block' : 'none';

    const btnFin = document.getElementById('btn_modal_finalize');
    if (btnFin) {
        btnFin.style.display = isOngoing ? 'block' : 'none';
        if (isOngoing && window.chatConfig.isEligibleToFinalize === false) {
            btnFin.disabled = true;
            btnFin.classList.add('btn-dash-disabled');
        }
    }

    modal.classList.add('active');

    // Fermer la sidebar/sheet si ouverte
    const overlay = document.getElementById('engSheetOverlay');
    const sheet   = document.getElementById('engSheet');
    if (overlay) overlay.classList.remove('active');
    if (sheet)   sheet.classList.remove('active');
}
