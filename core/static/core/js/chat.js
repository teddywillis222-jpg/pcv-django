/**
 * chat.js — ProfChezVous
 * Messagerie privée : envoi, polling, UI — Version refonte complète
 */

// ── Utilitaires Audio & Lightbox ─────────────────────────────
function formatAudioTime(sec) {
    if (!sec || isNaN(sec) || !isFinite(sec)) return "0:00";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
}

function formatFileSize(bytes) {
    if (!bytes || isNaN(bytes)) return '';
    if (bytes < 1024) return bytes + ' octets';
    if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' Ko';
    return (bytes / (1024 * 1024)).toFixed(1) + ' Mo';
}
window.formatFileSize = formatFileSize;

window.initAudioDuration = function(audio) {
    if (!audio) return;
    const player = audio.closest('.chat-audio-player');
    if (!player) return;
    const durEl = player.querySelector('.audio-duration');
    if (!durEl) return;

    // 1. Extraire la durée depuis le nom du fichier ou l'URL (ex: vocal_123456_8s.webm)
    const src = audio.src || audio.getAttribute('src') || '';
    const match = src.match(/_(\d+)s(?:\.|\/|$|\?)/i);
    if (match) {
        durEl.textContent = formatAudioTime(parseInt(match[1], 10));
        return;
    }

    // 2. Si audio.duration est déjà fini et valide
    const d = audio.duration;
    if (d && !isNaN(d) && isFinite(d) && d > 0) {
        durEl.textContent = formatAudioTime(d);
        return;
    }

    // 3. Écouter les événements natifs de chargement
    const onLoaded = function() {
        if (audio.duration && !isNaN(audio.duration) && isFinite(audio.duration) && audio.duration > 0) {
            durEl.textContent = formatAudioTime(audio.duration);
        }
    };
    audio.addEventListener('loadedmetadata', onLoaded, { once: true });
    audio.addEventListener('durationchange', onLoaded);
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

        // Si l'audio est arrivé au bout ou anormalement positionné, repartir du début
        if (audio.ended || (audio.duration && isFinite(audio.duration) && audio.currentTime >= audio.duration) || audio.currentTime > 9999) {
            audio.currentTime = 0;
        }

        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                if (playIcon) playIcon.style.display = 'none';
                if (pauseIcon) pauseIcon.style.display = 'block';
            }).catch(e => {
                console.warn('[Audio] Première tentative de lecture échouée, reset et retry...', e);
                audio.currentTime = 0;
                audio.play().then(() => {
                    if (playIcon) playIcon.style.display = 'none';
                    if (pauseIcon) pauseIcon.style.display = 'block';
                }).catch(err => {
                    console.error('[Audio] Échec lecture audio:', err);
                    if (playIcon) playIcon.style.display = 'block';
                    if (pauseIcon) pauseIcon.style.display = 'none';
                });
            });
        }
    } else {
        audio.pause();
        if (playIcon) playIcon.style.display = 'block';
        if (pauseIcon) pauseIcon.style.display = 'none';
    }
};

window.updateAudioProgress = function(audio) {
    const player = audio.closest('.chat-audio-player');
    if (!player) return;
    const prog = player.querySelector('.audio-progress');
    const durEl = player.querySelector('.audio-duration');
    const dur = audio.duration;

    let totalDur = null;
    const src = audio.src || audio.getAttribute('src') || '';
    const match = src.match(/_(\d+)s(?:\.|\/|$|\?)/i);
    if (match) {
        totalDur = parseInt(match[1], 10);
    } else if (dur && !isNaN(dur) && isFinite(dur) && dur > 0) {
        totalDur = dur;
    }

    if (totalDur && totalDur > 0) {
        const pct = Math.min(100, (audio.currentTime / totalDur) * 100);
        if (prog) prog.style.width = pct + '%';
        if (durEl) durEl.textContent = `${formatAudioTime(audio.currentTime)} / ${formatAudioTime(totalDur)}`;
    } else {
        if (prog && audio.currentTime > 0) prog.style.width = '30%';
        if (durEl && audio.currentTime > 0) durEl.textContent = formatAudioTime(audio.currentTime);
    }
};

window.onAudioEnded = function(audio) {
    const player = audio.closest('.chat-audio-player');
    if (!player) return;
    const prog = player.querySelector('.audio-progress');
    const durEl = player.querySelector('.audio-duration');
    const btn = player.querySelector('.audio-play-btn');
    if (prog) prog.style.width = '0%';

    const src = audio.src || audio.getAttribute('src') || '';
    const match = src.match(/_(\d+)s(?:\.|\/|$|\?)/i);
    if (match) {
        if (durEl) durEl.textContent = formatAudioTime(parseInt(match[1], 10));
    } else if (audio.duration && !isNaN(audio.duration) && isFinite(audio.duration)) {
        if (durEl) durEl.textContent = formatAudioTime(audio.duration);
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
    if (!audio) return;

    let totalDur = null;
    const src = audio.src || audio.getAttribute('src') || '';
    const match = src.match(/_(\d+)s(?:\.|\/|$|\?)/i);
    if (match) {
        totalDur = parseInt(match[1], 10);
    } else if (audio.duration && !isNaN(audio.duration) && isFinite(audio.duration)) {
        totalDur = audio.duration;
    }

    if (!totalDur || totalDur <= 0) return;

    const rect = bar.getBoundingClientRect();
    const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    audio.currentTime = pos * totalDur;
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
    const docInput     = document.getElementById('docInput');
    const docBtn       = document.getElementById('docBtn');
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

    // ── Gestion de la sélection multiple de documents (max 5, max 10 Mo) ──
    let selectedDocs = [];

    window.clearDocSelection = function() {
        selectedDocs = [];
        const bar = document.getElementById('docPreviewBar');
        if (bar) bar.style.display = 'none';
        if (docInput) docInput.value = '';
        const list = document.getElementById('docPreviewList');
        if (list) list.innerHTML = '';
    };

    window.removeSelectedDoc = function(idx) {
        if (idx >= 0 && idx < selectedDocs.length) {
            selectedDocs.splice(idx, 1);
            if (selectedDocs.length === 0) {
                clearDocSelection();
            } else {
                renderDocPreviews();
            }
        }
    };

    function renderDocPreviews() {
        const bar = document.getElementById('docPreviewBar');
        const list = document.getElementById('docPreviewList');
        const countEl = document.getElementById('docPreviewCount');
        if (!bar || !list) return;

        if (selectedDocs.length === 0) {
            bar.style.display = 'none';
            list.innerHTML = '';
            return;
        }

        bar.style.display = 'block';
        if (countEl) countEl.textContent = `Documents sélectionnés (${selectedDocs.length}/5)`;
        list.innerHTML = '';

        selectedDocs.forEach((file, index) => {
            const item = document.createElement('div');
            item.className = 'doc-preview-item';

            const ext = (file.name || '').split('.').pop().toLowerCase();
            let iconClass = '';
            if (ext === 'pdf') iconClass = 'pdf';
            else if (['doc', 'docx', 'odt'].includes(ext)) iconClass = 'word';
            else if (['xls', 'xlsx', 'csv'].includes(ext)) iconClass = 'excel';

            const icon = document.createElement('div');
            icon.className = `doc-preview-icon ${iconClass}`;
            icon.textContent = ext.substring(0, 4) || 'DOC';

            const details = document.createElement('div');
            details.className = 'doc-preview-details';
            const name = document.createElement('span');
            name.className = 'doc-preview-name';
            name.textContent = file.name;
            const size = document.createElement('span');
            size.className = 'doc-preview-size';
            size.textContent = formatFileSize(file.size);
            details.appendChild(name);
            details.appendChild(size);

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'doc-preview-remove';
            removeBtn.innerHTML = '×';
            removeBtn.title = 'Retirer ce document';
            removeBtn.onclick = (e) => {
                e.stopPropagation();
                removeSelectedDoc(index);
            };

            item.appendChild(icon);
            item.appendChild(details);
            item.appendChild(removeBtn);
            list.appendChild(item);
        });

        if (selectedDocs.length < 5) {
            const addMoreBtn = document.createElement('button');
            addMoreBtn.type = 'button';
            addMoreBtn.className = 'doc-preview-add-more';
            addMoreBtn.innerHTML = '+ Ajouter';
            addMoreBtn.title = 'Ajouter d\'autres documents (max 5)';
            addMoreBtn.onclick = () => {
                if (docInput) docInput.click();
            };
            list.appendChild(addMoreBtn);
        }
    }

    if (docInput) {
        docInput.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                const MAX_DOC_SIZE = 10 * 1024 * 1024; // 10 Mo
                let oversized = [];
                Array.from(this.files).forEach(f => {
                    if (f.size > MAX_DOC_SIZE) {
                        oversized.push(`« ${f.name} » (${(f.size / (1024*1024)).toFixed(1)} Mo)`);
                    } else if (selectedDocs.length < 5) {
                        const exists = selectedDocs.some(d => d.name === f.name && d.size === f.size);
                        if (!exists) selectedDocs.push(f);
                    }
                });

                if (oversized.length > 0) {
                    alert("Limite de taille dépassée (max 10 Mo par fichier) :\n" + oversized.join('\n'));
                }
                if (this.files.length > 5 || selectedDocs.length >= 5) {
                    if (this.files.length > 5) {
                        alert("Vous ne pouvez sélectionner que 5 documents maximum par envoi.");
                    }
                }

                renderDocPreviews();
                if (input) input.focus();
                docInput.value = '';
            }
        });
    }

    // ── Envoi de message ─────────────────────────────────────
    async function submitMessage(payload = null) {
        if (!chatForm || !input) return;
        const text = payload ? payload.text : input.value.trim();
        const singleFile = payload ? payload.file : null;
        const photosToSend = (payload && payload.files) ? payload.files : (singleFile ? [singleFile] : [...selectedPhotos, ...selectedDocs]);

        if (!text && photosToSend.length === 0) return;

        const sendBtn = document.getElementById('sendBtn') || chatForm.querySelector('.btn-send');
        if (sendBtn) sendBtn.disabled = true;

        // Vider la sélection photo et document et masquer les prévisualisations immédiatement
        clearPhotoSelection();
        clearDocSelection();

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

        // Créer les bulles optimistes (sécurisé)
        const tempIds = [];
        if (photosToSend.length > 0) {
            photosToSend.forEach((file, idx) => {
                const tempId = 'temp-' + Date.now() + '-' + idx;
                tempIds.push(tempId);
                const bubbleText = (idx === 0) ? text : '';
                try {
                    appendSentBubble(tempId, bubbleText, file, '…', payload ? payload.duration : null);
                } catch (errBubble) {
                    console.error('[Chat] Erreur création bulle optimiste:', errBubble);
                }
            });
        } else {
            const tempId = 'temp-' + Date.now();
            tempIds.push(tempId);
            try {
                appendSentBubble(tempId, text, null, '…');
            } catch (errBubble) {
                console.error('[Chat] Erreur création bulle optimiste:', errBubble);
            }
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

                            // Rendre la carte document immédiatement cliquable et téléchargeable
                            if (m.fichier_url) {
                                const card = tmpBubble.querySelector('.msg-file-card');
                                if (card && card.tagName !== 'A') {
                                    const a = document.createElement('a');
                                    a.className = card.className;
                                    a.href = m.fichier_url;
                                    a.target = '_blank';
                                    a.setAttribute('download', '');
                                    a.innerHTML = card.innerHTML + `<div class="msg-file-download-btn" title="Télécharger">
                                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                                    </div>`;
                                    card.parentNode.replaceChild(a, card);
                                }
                            }
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
                const durSeconds = Math.max(1, recSeconds);
                const audioFile = new File([blob], `vocal_${Date.now()}_${durSeconds}s${ext}`, { type: mime });

                stopMediaTracks();
                audioChunks = [];
                if (recordBar) recordBar.style.display = 'none';
                if (chatForm) chatForm.style.display = 'contents';

                if (blob.size > 0) {
                    await submitMessage({ file: audioFile, text: '', duration: durSeconds });
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
                    const isDoc = !isAud && !isImg && msg.fichier_url;

                    let bubbleClasses = 'msg-bubble received';
                    if (msg.fichier_url) {
                        bubbleClasses += ' has-media';
                        if (isImg) bubbleClasses += ' has-image';
                        if (isAud) bubbleClasses += ' has-audio';
                        if (isDoc) bubbleClasses += ' has-document';
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
                            const fname = msg.fichier_nom || 'Document joint';
                            const ext = fname.split('.').pop().toLowerCase();
                            let iconClass = '';
                            if (ext === 'pdf') iconClass = 'pdf';
                            else if (['doc', 'docx', 'odt'].includes(ext)) iconClass = 'word';
                            else if (['xls', 'xlsx', 'csv'].includes(ext)) iconClass = 'excel';

                            html += `<a href="${msg.fichier_url}" target="_blank" download class="msg-file-card">
                                <div class="msg-file-icon ${iconClass}">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                                </div>
                                <div class="msg-file-info">
                                    <span class="msg-file-name">${escapeHtml(fname)}</span>
                                    <span class="msg-file-meta">Document joint</span>
                                </div>
                                <div class="msg-file-download-btn" title="Télécharger">
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                                </div>
                            </a>`;
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

function appendSentBubble(id, text, file, time, durationSec) {
    const container = document.getElementById('messagesList');
    if (!container) return;

    let isImg = false;
    let isAud = false;
    let isDoc = false;
    let bubbleClasses = 'msg-bubble sent';
    if (file) {
        bubbleClasses += ' has-media';
        isImg = file.type && file.type.startsWith('image/');
        isAud = (file.type && file.type.startsWith('audio/')) || /\.(webm|ogg|mp3|m4a|wav|aac)$/i.test(file.name);
        isDoc = !isImg && !isAud;
        if (isImg) bubbleClasses += ' has-image';
        if (isAud) bubbleClasses += ' has-audio';
        if (isDoc) bubbleClasses += ' has-document';
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
            const durText = durationSec ? formatAudioTime(durationSec) : '--:--';
            html += `<div class="chat-audio-player" data-src="${blobUrl}">
                <button type="button" class="audio-play-btn" aria-label="Écouter" onclick="toggleAudio(this)">
                    <svg class="icon-play" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    <svg class="icon-pause" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="display:none;"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                </button>
                <div class="audio-track-wrap">
                    <div class="audio-waveform-bar" onclick="seekAudio(event, this)">
                        <div class="audio-progress"></div>
                    </div>
                    <span class="audio-duration">${durText}</span>
                </div>
                <audio src="${blobUrl}" preload="metadata" onloadedmetadata="initAudioDuration(this)" ontimeupdate="updateAudioProgress(this)" onended="onAudioEnded(this)"></audio>
            </div>`;
        } else {
            const ext = (file.name || '').split('.').pop().toLowerCase();
            let iconClass = '';
            if (ext === 'pdf') iconClass = 'pdf';
            else if (['doc', 'docx', 'odt'].includes(ext)) iconClass = 'word';
            else if (['xls', 'xlsx', 'csv'].includes(ext)) iconClass = 'excel';
            const sizeStr = formatFileSize(file.size);

            html += `<div class="msg-file-card">
                <div class="msg-file-icon ${iconClass}">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                </div>
                <div class="msg-file-info">
                    <span class="msg-file-name">${escapeHtml(file.name)}</span>
                    <span class="msg-file-meta">${sizeStr ? sizeStr + ' • ' : ''}Document</span>
                </div>
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
