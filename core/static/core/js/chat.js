/**
 * chat.js — ProfChezVous
 * Messagerie privée : envoi, polling, UI — Version refonte complète
 */

// ── Utilitaires Audio & Lightbox ─────────────────────────────
function formatAudioTime(sec) {
    if (!sec || isNaN(sec)) return "0:00";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
}

window.initAudioDuration = function(audio) {
    if (!audio) return;
    const player = audio.closest('.chat-audio-player');
    if (!player) return;
    const durEl = player.querySelector('.audio-duration');
    if (!durEl) return;

    function setDurDisplay(d) {
        durEl.textContent = formatAudioTime(d);
    }

    const d = audio.duration;
    if (d && !isNaN(d) && isFinite(d) && d > 0) {
        // Durée immédiatement disponible (fichier mp3 ou fichier déjà bufferisé)
        setDurDisplay(d);
        return;
    }

    // Pour les fichiers webm/MediaRecorder : duration = Infinity ou NaN
    // Technique "seek-to-end" : le navigateur ajuste currentTime à la vraie durée
    if (!isFinite(d)) {
        const savedTime = audio.currentTime;
        // Désactiver les événements pendant le seek
        audio._seekingForDuration = true;
        audio.currentTime = 1e101; // Seek à "l'infini" → le navigateur se cale à la fin réelle

        const onTimeUpdate = function() {
            if (audio._seekingForDuration) {
                audio._seekingForDuration = false;
                const realDur = audio.currentTime;
                if (realDur > 0) {
                    setDurDisplay(realDur);
                }
                // Remettre au début sans déclencher l'animation de progression
                audio.removeEventListener('timeupdate', onTimeUpdate);
                setTimeout(() => { audio.currentTime = 0; }, 0);
            }
        };
        audio.addEventListener('timeupdate', onTimeUpdate);
        // Timeout de sécurité si le seek échoue
        setTimeout(() => {
            if (audio._seekingForDuration) {
                audio._seekingForDuration = false;
                audio.removeEventListener('timeupdate', onTimeUpdate);
                try { audio.currentTime = 0; } catch(e) {}
            }
        }, 2000);
    }
};

window.toggleAudio = function(btn) {
    const player = btn.closest('.chat-audio-player');
    if (!player) return;
    const audio = player.querySelector('audio');
    if (!audio) return;

    const playIcon = btn.querySelector('.icon-play');
    const pauseIcon = btn.querySelector('.icon-pause');

    if (audio.paused) {
        // Stopper tous les autres audios qui tournent
        document.querySelectorAll('.chat-audio-player audio').forEach(a => {
            if (a !== audio && !a.paused) {
                a.pause();
                const otherBtn = a.closest('.chat-audio-player')?.querySelector('.audio-play-btn');
                if (otherBtn) {
                    const p = otherBtn.querySelector('.icon-play');
                    const pa = otherBtn.querySelector('.icon-pause');
                    if (p) p.style.display = 'block';
                    if (pa) pa.style.display = 'none';
                }
            }
        });

        audio.play().then(() => {
            if (playIcon) playIcon.style.display = 'none';
            if (pauseIcon) pauseIcon.style.display = 'block';
        }).catch(e => console.error('[Audio] Erreur lecture:', e));
    } else {
        audio.pause();
        if (playIcon) playIcon.style.display = 'block';
        if (pauseIcon) pauseIcon.style.display = 'none';
    }
};

window.updateAudioProgress = function(audio) {
    // Ne pas mettre à jour pendant le seek interne pour calcul de durée
    if (audio._seekingForDuration) return;
    const player = audio.closest('.chat-audio-player');
    if (!player) return;
    const prog = player.querySelector('.audio-progress');
    const durEl = player.querySelector('.audio-duration');
    const dur = audio.duration;
    if (dur && !isNaN(dur) && isFinite(dur)) {
        const pct = (audio.currentTime / dur) * 100;
        if (prog) prog.style.width = pct + '%';
        if (durEl) durEl.textContent = `${formatAudioTime(audio.currentTime)} / ${formatAudioTime(dur)}`;
    } else {
        // Durée toujours inconnue pendant lecture : afficher le temps courant seul
        if (durEl && audio.currentTime > 0) {
            durEl.textContent = formatAudioTime(audio.currentTime);
        }
    }
};

window.onAudioEnded = function(audio) {
    const player = audio.closest('.chat-audio-player');
    if (!player) return;
    const prog = player.querySelector('.audio-progress');
    const durEl = player.querySelector('.audio-duration');
    const btn = player.querySelector('.audio-play-btn');
    if (prog) prog.style.width = '0%';
    if (durEl) {
        const dur = audio.duration;
        if (dur && !isNaN(dur) && isFinite(dur)) {
            durEl.textContent = formatAudioTime(dur);
        }
    }
    if (btn) {
        const playIcon = btn.querySelector('.icon-play');
        const pauseIcon = btn.querySelector('.icon-pause');
        if (playIcon) playIcon.style.display = 'block';
        if (pauseIcon) pauseIcon.style.display = 'none';
    }
};

window.seekAudio = function(e, bar) {
    const player = bar.closest('.chat-audio-player');
    if (!player) return;
    const audio = player.querySelector('audio');
    if (!audio || !audio.duration) return;
    const rect = bar.getBoundingClientRect();
    const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    audio.currentTime = pos * audio.duration;
};

window.openLightbox = function(src) {
    const box = document.getElementById('imageLightbox');
    const img = document.getElementById('lightboxImg');
    if (box && img) {
        img.src = src;
        box.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
};

window.closeLightbox = function(e) {
    const box = document.getElementById('imageLightbox');
    if (box) {
        box.style.display = 'none';
        document.body.style.overflow = '';
    }
};

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') window.closeLightbox();
});

// ── Compression d'image Haute Fidélité (Client) ──────────────
async function compressImage(file, maxDim = 1920, quality = 0.88) {
    if (!file || !file.type || !file.type.startsWith('image/')) return file;
    if (file.type === 'image/gif' || file.type === 'image/svg+xml') return file;
    if (file.size < 300 * 1024) return file; // Moins de 300 Ko = déjà optimal

    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                let width = img.width;
                let height = img.height;

                if (width > maxDim || height > maxDim) {
                    if (width > height) {
                        height = Math.round((height * maxDim) / width);
                        width = maxDim;
                    } else {
                        width = Math.round((width * maxDim) / height);
                        height = maxDim;
                    }
                }

                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = 'high';
                ctx.drawImage(img, 0, 0, width, height);

                const mimeType = 'image/webp';
                canvas.toBlob((blob) => {
                    if (!blob || blob.size >= file.size) {
                        resolve(file);
                    } else {
                        const newName = file.name.replace(/\.[^/.]+$/, "") + ".webp";
                        const compressedFile = new File([blob], newName, {
                            type: mimeType,
                            lastModified: Date.now()
                        });
                        resolve(compressedFile);
                    }
                }, mimeType, quality);
            };
            img.onerror = () => resolve(file);
            img.src = e.target.result;
        };
        reader.onerror = () => resolve(file);
        reader.readAsDataURL(file);
    });
}


document.addEventListener('DOMContentLoaded', function () {
    console.log('[Chat] Initialisation...');

    // ── Éléments DOM ────────────────────────────────────────
    const input        = document.getElementById('messageInput');
    const chatForm     = document.getElementById('chatForm');
    const fileInput    = document.getElementById('fileInput');
    const sendErrorBox = document.getElementById('chatSendError');
    const sendErrorTxt = document.getElementById('chatSendErrorText');
    const retryBtn     = document.getElementById('chatRetryBtn');
    const scrollBtn    = document.getElementById('scrollBottomBtn');
    const badge        = document.getElementById('unreadBadge');
    const messagesList = document.getElementById('messagesList');
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

    // ── Logique de la flèche flottante ───────────────────────
    if (messagesList && scrollBtn) {
        messagesList.addEventListener('scroll', () => {
            // Tolérance de 150px pour déterminer si on est "en bas"
            const isNearBottom = messagesList.scrollHeight - messagesList.scrollTop - messagesList.clientHeight < 150;
            if (isNearBottom) {
                scrollBtn.style.display = 'none';
                if (badge) {
                    badge.style.display = 'none';
                    badge.textContent = '0';
                }
            } else {
                scrollBtn.style.display = 'flex';
            }
        });

        scrollBtn.addEventListener('click', () => {
            scrollToBottom();
            // L'événement de scroll masquer automatiquement le bouton
        });
    }

    // ── Feedback erreur envoi ────────────────────────────────
    function showSendError(msg) {
        if (!sendErrorBox || !sendErrorTxt) return;
        sendErrorTxt.textContent = msg;
        sendErrorBox.style.display = 'flex';
    }
    function hideSendError() {
        if (sendErrorBox) sendErrorBox.style.display = 'none';
    }
    hideSendError();

    // ── Gestion de la sélection multiple de photos (max 5) ──
    let selectedPhotos = [];

    window.clearPhotoSelection = function() {
        selectedPhotos = [];
        const bar = document.getElementById('photoPreviewBar');
        if (bar) bar.style.display = 'none';
        if (fileInput) fileInput.value = '';
        const list = document.getElementById('photoPreviewList');
        if (list) list.innerHTML = '';
    };

    window.removeSelectedPhoto = function(idx) {
        if (idx >= 0 && idx < selectedPhotos.length) {
            selectedPhotos.splice(idx, 1);
            if (selectedPhotos.length === 0) {
                clearPhotoSelection();
            } else {
                renderPhotoPreviews();
            }
        }
    };

    function renderPhotoPreviews() {
        const bar = document.getElementById('photoPreviewBar');
        const list = document.getElementById('photoPreviewList');
        const countEl = document.getElementById('photoPreviewCount');
        if (!bar || !list) return;

        if (selectedPhotos.length === 0) {
            bar.style.display = 'none';
            list.innerHTML = '';
            return;
        }

        bar.style.display = 'block';
        if (countEl) countEl.textContent = `Photos sélectionnées (${selectedPhotos.length}/5)`;
        list.innerHTML = '';

        selectedPhotos.forEach((file, index) => {
            const item = document.createElement('div');
            item.className = 'photo-preview-item';
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.alt = file.name;

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'photo-preview-remove';
            removeBtn.innerHTML = '×';
            removeBtn.title = 'Retirer cette photo';
            removeBtn.onclick = (e) => {
                e.stopPropagation();
                removeSelectedPhoto(index);
            };

            item.appendChild(img);
            item.appendChild(removeBtn);
            list.appendChild(item);
        });

        if (selectedPhotos.length < 5) {
            const addMoreBtn = document.createElement('button');
            addMoreBtn.type = 'button';
            addMoreBtn.className = 'photo-preview-add-more';
            addMoreBtn.innerHTML = '+';
            addMoreBtn.title = 'Ajouter d\'autres photos (max 5)';
            addMoreBtn.onclick = () => {
                if (fileInput) fileInput.click();
            };
            list.appendChild(addMoreBtn);
        }
    }

    if (fileInput) {
        fileInput.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                const newFiles = Array.from(this.files).filter(f => f.type.startsWith('image/'));
                if (newFiles.length === 0) {
                    alert("Veuillez sélectionner uniquement des fichiers image (photos).");
                    return;
                }

                newFiles.forEach(f => {
                    if (selectedPhotos.length < 5) {
                        const exists = selectedPhotos.some(p => p.name === f.name && p.size === f.size);
                        if (!exists) selectedPhotos.push(f);
                    }
                });

                if (this.files.length > 5 || selectedPhotos.length >= 5) {
                    if (this.files.length > 5) {
                        alert("Vous ne pouvez sélectionner que 5 photos maximum par envoi.");
                    }
                }

                renderPhotoPreviews();
                if (input) input.focus();
                fileInput.value = '';
            }
        });
    }

    // ── Envoi de message ─────────────────────────────────────
    async function submitMessage(payload = null) {
        if (!chatForm || !input) return;
        const text = payload ? payload.text : input.value.trim();
        const singleFile = payload ? payload.file : null;
        const photosToSend = (payload && payload.files) ? payload.files : (singleFile ? [singleFile] : [...selectedPhotos]);

        if (!text && photosToSend.length === 0) return;

        const sendBtn = document.getElementById('sendBtn') || chatForm.querySelector('.btn-send');
        if (sendBtn) sendBtn.disabled = true;

        // Vider la sélection photo et masquer la prévisualisation immédiatement
        clearPhotoSelection();

        // Vider l'input texte immédiatement (UX optimiste)
        if (!payload) {
            input.value = '';
            input.style.height = 'auto';
        }

        // Cacher le placeholder vide s'il existe
        const emptyPlaceholder = document.getElementById('empty-chat-placeholder');
        if (emptyPlaceholder) {
            emptyPlaceholder.style.display = 'none';
        }

        // Créer les bulles optimistes
        const tempIds = [];
        if (photosToSend.length > 0) {
            photosToSend.forEach((file, idx) => {
                const tempId = 'temp-' + Date.now() + '-' + idx;
                tempIds.push(tempId);
                const bubbleText = (idx === 0) ? text : '';
                appendSentBubble(tempId, bubbleText, file, '…');
            });
        } else {
            const tempId = 'temp-' + Date.now();
            tempIds.push(tempId);
            appendSentBubble(tempId, text, null, '…');
        }

        try {
            const fd = new FormData();
            if (text) fd.append('texte', text);

            if (photosToSend.length > 0) {
                // Compression haute fidélité pour les images
                const processedFiles = await Promise.all(
                    photosToSend.map(async (file) => {
                        if (file.type && file.type.startsWith('image/')) {
                            return await compressImage(file, 1920, 0.88);
                        }
                        return file;
                    })
                );

                processedFiles.forEach(file => {
                    fd.append('fichiers', file);
                });
                fd.append('fichier', processedFiles[0]);
            }

            const res = await fetch(config.urls.sendMessage, {
                method: 'POST',
                body: fd,
                headers: { 'X-CSRFToken': config.csrfToken }
            });

            let data = {};
            try { data = await res.json(); } catch (_) {}

            if (res.ok) {
                // Mettre à jour les bulles optimistes avec les IDs réels
                if (data.messages && Array.isArray(data.messages)) {
                    data.messages.forEach((m, idx) => {
                        const tempId = tempIds[idx];
                        const tmpBubble = document.querySelector(`[data-id="${tempId}"]`);
                        if (tmpBubble) {
                            tmpBubble.setAttribute('data-id', m.id);
                            const timeEl = tmpBubble.querySelector('.msg-time');
                            if (timeEl) timeEl.textContent = m.date || new Date().toLocaleTimeString('fr-FR', {hour:'2-digit', minute:'2-digit'});
                            tmpBubble.style.opacity = '1';
                        }
                        if (m.id > config.lastMsgId) config.lastMsgId = m.id;
                    });
                } else if (tempIds.length > 0) {
                    const tmpBubble = document.querySelector(`[data-id="${tempIds[0]}"]`);
                    if (tmpBubble) {
                        tmpBubble.setAttribute('data-id', data.message_id);
                        const timeEl = tmpBubble.querySelector('.msg-time');
                        if (timeEl) timeEl.textContent = data.date || new Date().toLocaleTimeString('fr-FR', {hour:'2-digit', minute:'2-digit'});
                        tmpBubble.style.opacity = '1';
                    }
                    if (data.message_id > config.lastMsgId) config.lastMsgId = data.message_id;
                }

                hideSendError();
                lastFailedPayload = null;
                scrollToBottom();
                return;
            }

            // Échec : retirer les bulles optimistes
            tempIds.forEach(id => removeBubble(id));

            if (res.status === 402) {
                showPaymentModal();
                return;
            }

            lastFailedPayload = { text, files: photosToSend };
            showSendError(data.error || 'Envoi impossible pour le moment.');
        } catch (e) {
            console.error('[Chat] Erreur envoi:', e);
            tempIds.forEach(id => removeBubble(id));
            lastFailedPayload = { text, files: photosToSend };
            showSendError('Erreur de connexion. Vérifiez le réseau puis renvoyez.');
        } finally {
            if (sendBtn) sendBtn.disabled = false;
        }
    }

    // ── Formulaire submit ────────────────────────────────────
    if (chatForm) {
        chatForm.onsubmit = async (e) => {
            e.preventDefault();
            await submitMessage();
        };
    }

    if (retryBtn) {
        retryBtn.addEventListener('click', async () => {
            if (!lastFailedPayload) return;
            await submitMessage(lastFailedPayload);
        });
    }

    // ── Textarea auto-resize et soumission ───────────────────
    if (input) {
        input.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        input.addEventListener('focus', function () {
            setTimeout(() => scrollToBottom(), 200);
        });
    }

    // ── Enregistreur Audio (Notes Vocales) ─────────────────────
    let mediaRecorder = null;
    let audioChunks = [];
    let recTimerInterval = null;
    let recSeconds = 0;
    let activeStream = null;

    const audioBtn = document.getElementById('audioBtn');
    const recordBar = document.getElementById('audioRecordBar');
    const recTimerEl = document.getElementById('recTimer');
    const cancelRecBtn = document.getElementById('cancelRecBtn');
    const sendRecBtn = document.getElementById('sendRecBtn');

    function formatTimer(sec) {
        const m = Math.floor(sec / 60);
        const s = sec % 60;
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    }

    function stopMediaTracks() {
        if (activeStream) {
            activeStream.getTracks().forEach(t => t.stop());
            activeStream = null;
        }
        if (recTimerInterval) {
            clearInterval(recTimerInterval);
            recTimerInterval = null;
        }
        recSeconds = 0;
    }

    async function startAudioRecording() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("L'enregistrement vocal requiert l'accès au micro et une connexion sécurisée (HTTPS).");
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            activeStream = stream;
            audioChunks = [];

            let mimeType = 'audio/webm;codecs=opus';
            if (!window.MediaRecorder || !MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = MediaRecorder.isTypeSupported('audio/mp4') ? 'audio/mp4' : (MediaRecorder.isTypeSupported('audio/ogg') ? 'audio/ogg' : '');
            }

            const options = mimeType ? { mimeType } : {};
            mediaRecorder = new MediaRecorder(stream, options);

            mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };

            mediaRecorder.start(250);

            // Basculer l'UI vers le mode enregistrement
            if (chatForm) chatForm.style.display = 'none';
            if (recordBar) recordBar.style.display = 'flex';

            recSeconds = 0;
            if (recTimerEl) recTimerEl.textContent = '0:00';
            recTimerInterval = setInterval(() => {
                recSeconds++;
                if (recTimerEl) recTimerEl.textContent = formatTimer(recSeconds);
            }, 1000);

        } catch (err) {
            console.error('[Audio] Erreur accès micro:', err);
            alert("Impossible d'accéder au microphone. Veuillez autoriser l'accès au micro dans votre navigateur.");
        }
    }

    if (audioBtn) {
        audioBtn.addEventListener('click', (e) => {
            e.preventDefault();
            startAudioRecording();
        });
    }

    if (cancelRecBtn) {
        cancelRecBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.onstop = null;
                mediaRecorder.stop();
            }
            stopMediaTracks();
            audioChunks = [];
            if (recordBar) recordBar.style.display = 'none';
            if (chatForm) chatForm.style.display = 'contents';
        });
    }

    if (sendRecBtn) {
        sendRecBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (!mediaRecorder || mediaRecorder.state === 'inactive') return;

            mediaRecorder.onstop = async () => {
                const mime = mediaRecorder.mimeType || 'audio/webm';
                const blob = new Blob(audioChunks, { type: mime });
                const ext = mime.includes('mp4') ? '.m4a' : (mime.includes('ogg') ? '.ogg' : '.webm');
                const audioFile = new File([blob], `vocal_${Date.now()}${ext}`, { type: mime });

                stopMediaTracks();
                audioChunks = [];
                if (recordBar) recordBar.style.display = 'none';
                if (chatForm) chatForm.style.display = 'contents';

                if (blob.size > 0) {
                    await submitMessage({ file: audioFile, text: '' });
                }
            };

            mediaRecorder.stop();
        });
    }

    // ── Polling AJAX avec pause si onglet inactif ────────────
    let pollingInterval = null;

    async function fetchNewMessages() {
        if (!config.urls || !config.urls.fetchMessages) return;

        try {
            const unreadEls = document.querySelectorAll('.sent .msg-tick:not(.read)');
            const unreadIds = Array.from(unreadEls)
                .map(el => {
                    const bubble = el.closest('.msg-bubble');
                    return bubble ? bubble.getAttribute('data-id') : null;
                })
                .filter(Boolean)
                .join(',');

            const url = `${config.urls.fetchMessages}?last_msg_id=${config.lastMsgId}&unread_ids=${unreadIds}`;
            const res = await fetch(url);
            if (!res.ok) return;
            const data = await res.json();

            // Nouveaux messages reçus
            if (data.messages && data.messages.length > 0) {
                let hasNew = false;
                const container = document.getElementById('messagesList');
                const emptyPlaceholder = document.getElementById('empty-chat-placeholder');
                if (emptyPlaceholder) emptyPlaceholder.style.display = 'none';
                data.messages.forEach(msg => {
                    if (msg.id > config.lastMsgId) config.lastMsgId = msg.id;
                    if (document.querySelector(`.msg-bubble[data-id="${msg.id}"]`)) return;

                    // AUDIO a la priorité absolue pour éviter le conflit avec les URLs Cloudinary
                    // (les anciens audios uploadés avec resource_type='image' ont /image/ dans leur URL)
                    const isAud = msg.fichier_url && (msg.type_message === 'AUDIO' || /\.(webm|ogg|mp3|m4a|wav|aac)(\?|$)/i.test(msg.fichier_url));
                    const isImg = !isAud && msg.fichier_url && (msg.type_message === 'IMAGE' || msg.fichier_url.includes('/image/') || /\.(jpg|jpeg|png|webp|gif)(\?|$)/i.test(msg.fichier_url));

                    let bubbleClasses = 'msg-bubble received';
                    if (msg.fichier_url) {
                        bubbleClasses += ' has-media';
                        if (isImg) bubbleClasses += ' has-image';
                        if (isAud) bubbleClasses += ' has-audio';
                        if (!msg.text) bubbleClasses += ' media-only';
                    }

                    const bubble = document.createElement('div');
                    bubble.className = bubbleClasses;
                    bubble.setAttribute('data-id', msg.id);

                    let html = '';
                    if (msg.fichier_url) {
                        if (isImg) {
                            html += `<div class="msg-image-wrap">
                                <img src="${msg.fichier_url}" class="chat-img-thumb" alt="Photo" loading="lazy" onclick="openLightbox(this.src)">
                                ${!msg.text ? `<div class="msg-meta msg-meta-overlay">
                                    <span class="msg-time">${msg.date}</span>
                                </div>` : ''}
                            </div>`;
                        } else if (isAud) {
                            html += `<div class="chat-audio-player" data-src="${msg.fichier_url}">
                                <button type="button" class="audio-play-btn" aria-label="Écouter" onclick="toggleAudio(this)">
                                    <svg class="icon-play" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                                    <svg class="icon-pause" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="display:none;"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                                </button>
                                <div class="audio-track-wrap">
                                    <div class="audio-waveform-bar" onclick="seekAudio(event, this)">
                                        <div class="audio-progress"></div>
                                    </div>
                                    <span class="audio-duration">--:--</span>
                                </div>
                                <audio src="${msg.fichier_url}" preload="metadata" onloadedmetadata="initAudioDuration(this)" ontimeupdate="updateAudioProgress(this)" onended="onAudioEnded(this)"></audio>
                            </div>`;
                        } else {
                            html += `<div class="msg-file">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                                <a href="${msg.fichier_url}" target="_blank" style="color:inherit; text-decoration:none;">${msg.fichier_nom || 'Fichier joint'}</a>
                            </div>`;
                        }
                    }
                    if (msg.is_locked) {
                        const paymentLink = config.urls && config.urls.paymentUrl ? `<a href="${config.urls.paymentUrl}" style="color:var(--c-accent); font-weight:600; text-decoration: none;">Procéder au paiement</a>` : `<button type="button" onclick="showPaymentModal()" style="color:var(--c-accent); font-weight:600; background:none; border:none; padding:0; cursor:pointer; font-size: inherit; font-family: inherit;">Procéder au paiement</button>`;
                        html += `<div style="opacity: 0.9; font-style: italic; margin-bottom: 0.5rem;">
                            Ce message est verrouillé. Veuillez ${paymentLink} ou <a href="/mon-plan/" style="color:var(--c-accent); font-weight:600; text-decoration: none;">Gérer mon plan</a> pour débloquer la discussion.
                        </div>`;
                    } else if (msg.text) {
                        html += `<div class="msg-content">${escapeHtml(msg.text)}</div>`;
                    }
                    if (msg.text || isAud || !isImg) {
                        html += `<div class="msg-meta"><span class="msg-time">${msg.date}</span></div>`;
                    }
                    bubble.innerHTML = html;

                    if (container) container.appendChild(bubble);

                    // Après injection dans le DOM, forcer le chargement audio
                    // (innerHTML ne déclenche pas automatiquement le chargement des ressources audio)
                    const audioEl = bubble.querySelector('audio');
                    if (audioEl) {
                        audioEl.load();
                        // Initialiser la durée après chargement des métadonnées
                        audioEl.addEventListener('loadedmetadata', function() {
                            initAudioDuration(this);
                        }, { once: true });
                    }

                    hasNew = true;
                });
                
                if (hasNew) {
                    const c = document.getElementById('messagesList');
                    if (c) {
                        const isNearBottom = c.scrollHeight - c.scrollTop - c.clientHeight < 200;
                        if (isNearBottom) {
                            scrollToBottom();
                        } else if (scrollBtn && badge) {
                            scrollBtn.style.display = 'flex';
                            badge.style.display = 'flex';
                            let currentVal = parseInt(badge.textContent) || 0;
                            badge.textContent = currentVal + data.messages.length;
                        }
                    }
                }
            }

            // Mise à jour statut lu
            if (data.newly_read && data.newly_read.length > 0) {
                data.newly_read.forEach(id => {
                    const bubble = document.querySelector(`.sent[data-id="${id}"]`);
                    if (!bubble) return;
                    const icon = bubble.querySelector('.msg-tick');
                    if (icon && !icon.classList.contains('read')) {
                        icon.outerHTML = `<svg class="msg-tick read" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M18 6 7 17l-5-5"/><path d="m22 10-7.5 7.5L13 16"/>
                        </svg>`;
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

    let isImg = false;
    let isAud = false;
    let bubbleClasses = 'msg-bubble sent';
    if (file) {
        bubbleClasses += ' has-media';
        isImg = file.type && file.type.startsWith('image/');
        isAud = (file.type && file.type.startsWith('audio/')) || /\.(webm|ogg|mp3|m4a|wav|aac)$/i.test(file.name);
        if (isImg) bubbleClasses += ' has-image';
        if (isAud) bubbleClasses += ' has-audio';
        if (!text) bubbleClasses += ' media-only';
    }

    const bubble = document.createElement('div');
    bubble.className = bubbleClasses;
    bubble.setAttribute('data-id', id);
    bubble.style.opacity = '0.75';
    bubble.style.transition = 'opacity 0.2s';

    let html = '';
    if (file) {
        if (isImg) {
            const blobUrl = URL.createObjectURL(file);
            html += `<div class="msg-image-wrap">
                <img src="${blobUrl}" class="chat-img-thumb" alt="Photo" onclick="openLightbox(this.src)">
                ${!text ? `<div class="msg-meta msg-meta-overlay">
                    <span class="msg-time">${time}</span>
                    <svg class="msg-tick" viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 6 9 17l-5-5"/>
                    </svg>
                </div>` : ''}
            </div>`;
        } else if (isAud) {
            const blobUrl = URL.createObjectURL(file);
            html += `<div class="chat-audio-player" data-src="${blobUrl}">
                <button type="button" class="audio-play-btn" aria-label="Écouter" onclick="toggleAudio(this)">
                    <svg class="icon-play" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    <svg class="icon-pause" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="display:none;"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                </button>
                <div class="audio-track-wrap">
                    <div class="audio-waveform-bar" onclick="seekAudio(event, this)">
                        <div class="audio-progress"></div>
                    </div>
                    <span class="audio-duration">--:--</span>
                </div>
                <audio src="${blobUrl}" preload="metadata" onloadedmetadata="initAudioDuration(this)" ontimeupdate="updateAudioProgress(this)" onended="onAudioEnded(this)"></audio>
            </div>`;
        } else {
            html += `<div class="msg-file">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
                ${escapeHtml(file.name)}
            </div>`;
        }
    }
    if (text) {
        html += `<div class="msg-content">${escapeHtml(text)}</div>`;
    }
    if (text || isAud || !isImg) {
        html += `<div class="msg-meta">
            <span class="msg-time">${time}</span>
            <svg class="msg-tick" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 6 9 17l-5-5"/>
            </svg>
        </div>`;
    }
    bubble.innerHTML = html;
    container.appendChild(bubble);

    // Forcer le chargement audio après injection pour que le play fonctionne immédiatement
    const sentAudioEl = bubble.querySelector('audio');
    if (sentAudioEl) {
        sentAudioEl.load();
        sentAudioEl.addEventListener('loadedmetadata', function() {
            initAudioDuration(this);
        }, { once: true });
    }

    scrollToBottom();
}

function removeBubble(id) {
    const b = document.querySelector(`[data-id="${id}"]`);
    if (b) b.remove();
}


// Note: Les fonctions toggleSheet, toggleOptions, etc. sont gérées 
// directement dans le template pour une meilleure réactivité avec les IDs locaux.

function filterEngagements() {
    const childId = document.getElementById('childFilter')?.value;
    document.querySelectorAll('.eng-row, .c-eng-card').forEach(row => {
        if (!childId || childId === 'all') {
            row.style.display = '';
            return;
        }
        // Trim chaque ID pour éviter les espaces/retours à la ligne du template Django
        const rawIds = (row.getAttribute('data-child-ids') || row.getAttribute('data-child-id') || '').trim();
        if (!rawIds) {
            // Engagement sans enfant lié → toujours visible (cas apprenant direct)
            row.style.display = '';
            return;
        }
        const childIds = rawIds.split(',').map(s => s.trim()).filter(Boolean);
        row.style.display = childIds.includes(String(childId)) ? '' : 'none';
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
