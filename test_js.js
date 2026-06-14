
    // Share Options Toggle Logic
    function toggleShareOptions() {
        const container = document.getElementById('share-options-container');
        const chevron = document.getElementById('share-chevron');
        if (container.style.display === 'none' || container.style.display === '') {
            container.style.display = 'flex';
            chevron.style.transform = 'rotate(90deg)';
        } else {
            container.style.display = 'none';
            chevron.style.transform = 'rotate(0deg)';
        }
    }

    // Section Switching Logic
    function showSection(sectionId, btn) {
        // Hide all sections
        document.querySelectorAll('.dash-section').forEach(s => s.style.display = 'none');
        // Show target section
        document.getElementById(sectionId).style.display = 'block';
        
        // Update nav active states
        document.querySelectorAll('.dash-sidebar nav a, .dash-bottom-nav .nav-item').forEach(a => {
            a.classList.remove('active');
            if (a.getAttribute('onclick') && a.getAttribute('onclick').includes(sectionId)) {
                a.classList.add('active');
            }
        });

        // Close sidebar on mobile if needed (optional)
    }

    async function toggleEssai() {
        const container = document.getElementById('btnToggleEssaiContainer');
        const txt = document.getElementById('txtToggleEssai');
        if (container.dataset.loading === 'true') return;

        container.dataset.loading = 'true';
        container.style.opacity = '0.7';

        try {
            const response = await fetch("{% url 'api_toggle_essai' %}", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            if (data.success) {
                if (data.actif) {
                    txt.textContent = "Désactiver l'essai gratuit";
                } else {
                    txt.textContent = "Activer l'essai gratuit";
                }
            } else {
                alert(data.error || "Une erreur est survenue");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Erreur de connexion.");
        } finally {
            container.dataset.loading = 'false';
            container.style.opacity = '1';
        }
    }


    // Tab Switching Logic
    function switchTab(evt, tabId) {
        // Hide all contents
        const contents = document.querySelectorAll('.tab-content');
        contents.forEach(content => {
            content.style.display = 'none';
            content.classList.remove('active');
        });

        // Deactivate all buttons
        const buttons = document.querySelectorAll('.tab-btn');
        buttons.forEach(btn => btn.classList.remove('active'));

        // Show active content
        const activeContent = document.getElementById(tabId);
        activeContent.style.display = 'block';
        activeContent.classList.add('active');

        // Activate button
        evt.currentTarget.classList.add('active');
    }

    // Modal Logic
    async function openEngModal(id) {
        const modal = document.getElementById('engModal');
        const content = document.getElementById('modalContent');
        modal.style.display = 'flex';
        content.innerHTML = `
            <div style="text-align:center; padding: 3rem 1rem;">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite; color: #16a34a; margin-bottom: 1rem;">
                    <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                </svg>
                <p style="color: #64748b; font-weight: 500; margin: 0;">Chargement des informations...</p>
            </div>
            <style>@keyframes spin { 100% { transform: rotate(360deg); } }</style>
        `;
        
        try {
            const response = await fetch(`/api/engagement/${id}/details/`);
            const data = await response.json();
            
            if (data.success) {
                const eng = data.engagement;
                const isTrial = eng.type === 'ESSAI';
                let actionsHtml = '';
                
                if (eng.status === 'EN_ATTENTE' || eng.status === 'ESSAI_PROGRAMME') {
                    actionsHtml = `
                        <div style="display:flex; gap:0.75rem; margin-top: 1.5rem;">
                            <button class="btn-dash btn-dash-primary" style="flex:1" onclick="handleEngAction(${id}, 'accepter', ${isTrial}, '${eng.client_role || 'PARENT'}', this)">Confirmer</button>
                            <button class="btn-dash btn-dash-outline" style="flex:1; color:#ef4444; border-color:#ef4444;" onclick="handleEngAction(${id}, 'refuser')">Refuser</button>
                        </div>
                    `;
                } else if (eng.status === 'REFUSE') {
                    actionsHtml = `<div style="text-align: center; padding: 1rem; background: #fee2e2; color: #b91c1c; border-radius: 12px; font-weight: 700; margin-top:1rem;">${isTrial ? 'Essai refusé' : 'Proposition refusée'}</div>`;
                } else {
                    actionsHtml = `<div style="text-align: center; padding: 1rem; background: #f0fdf4; color: #16a34a; border-radius: 12px; font-weight: 700; margin-top:1rem;">${isTrial ? 'Essai déjà accepté' : 'Demande déjà acceptée'}</div>`;
                }
                
                let trialInfoHtml = '';
                if (isTrial) {
                    trialInfoHtml = `
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Matière</span>
                            <span style="font-weight: 700;">${eng.matiere}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Classe</span>
                            <span style="font-weight: 700;">${eng.classe}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Mode</span>
                            <span style="font-weight: 700;">${eng.mode}</span>
                        </div>
                        ${eng.mode_raw === 'ONLINE' && eng.plateforme ? `
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Plateforme</span>
                            <span style="font-weight: 700;">${eng.plateforme}</span>
                        </div>` : ''}
                        ${eng.mode_raw !== 'ONLINE' ? `
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Lieu</span>
                            <span style="font-weight: 700;">${eng.lieu || 'Non précisé'}</span>
                        </div>` : ''}
                        ${eng.mode_raw !== 'ONLINE' && eng.indications_geographiques ? `
                        <div style="margin-bottom: 0.5rem;">
                            <span style="display: block; color: #64748b; font-size: 0.82rem; margin-bottom: 4px;">📍 Indications pour trouver la maison</span>
                            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 0.6rem 0.85rem; font-size: 0.88rem; font-style: italic; color: #1e293b; max-height: 100px; overflow-y: auto;">
                                ${eng.indications_geographiques}
                            </div>
                        </div>` : ''}
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Date d'essai</span>
                            <span style="font-weight: 700;">${eng.date_essai}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Heures</span>
                            <span style="font-weight: 700;">${eng.heure_debut}${eng.heure_fin ? ' - ' + eng.heure_fin : ''}</span>
                        </div>
                    `;
                    if (eng.description_essai) {
                        trialInfoHtml += `
                            <div style="margin-top: 0.5rem;">
                                <span style="display: block; color: #64748b; margin-bottom: 2px;">Description / Instructions</span>
                                <div style="background: #fff; padding: 0.75rem; border-radius: 8px; border: 1px solid #e2e8f0; font-style: italic;">
                                    ${eng.description_essai}
                                </div>
                            </div>
                        `;
                    }
                }

                content.innerHTML = `
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800;">${isTrial ? "Demande de Cours d'Essai" : "Proposition d'Engagement"}</h3>
                        <p style="font-size: 0.85rem; color: #64748b;">Détails envoyés par le client</p>
                    </div>

                    <div style="background: #f8fafc; padding: 1.25rem; border-radius: 16px; font-size: 0.9rem; line-height: 1.8;">
                        ${!isTrial ? `
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Matière</span>
                            <span style="font-weight: 700;">${eng.matiere}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Classe</span>
                            <span style="font-weight: 700;">${eng.classe}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Mode</span>
                            <span style="font-weight: 700;">${eng.mode}</span>
                        </div>
                        ${eng.mode_raw === 'ONLINE' && eng.plateforme ? `
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Plateforme</span>
                            <span style="font-weight: 700;">${eng.plateforme}</span>
                        </div>` : ''}
                        ${eng.mode_raw !== 'ONLINE' ? `
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Lieu</span>
                            <span style="font-weight: 700;">${eng.lieu || 'Non précisé'}</span>
                        </div>` : ''}
                        ${eng.mode_raw !== 'ONLINE' && eng.indications_geographiques ? `
                        <div style="margin-bottom: 0.5rem;">
                            <span style="display: block; color: #64748b; font-size: 0.82rem; margin-bottom: 4px;">📍 Indications pour trouver la maison</span>
                            <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 0.6rem 0.85rem; font-size: 0.88rem; font-style: italic; color: #1e293b;">${eng.indications_geographiques}</div>
                        </div>` : ''}
                        ${!isTrial ? `
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Budget</span>
                            <span style="font-weight: 800; color: #16a34a;">${eng.budget || 'À négocier'} FCFA/séance</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Durée d'une séance</span>
                            <span style="font-weight: 700;">${eng.duree || 'Non précisée'}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Fréquence par semaine</span>
                            <span style="font-weight: 700;">${eng.frequence || 'Non précisée'}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Élève / Enfant</span>
                            <span style="font-weight: 700;">${eng.student_name || 'Non précisé'}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="color: #64748b;">Durée souhaitée</span>
                            <span style="font-weight: 700;">${eng.duree_mois ? eng.duree_mois + ' mois' : 'Non précisée'}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #64748b;">Début souhaité</span>
                            <span style="font-weight: 700;">${eng.date_debut || 'À convenir'}</span>
                        </div>` : trialInfoHtml}
                    </div>
                    ${actionsHtml}
                `;
            } else {
                content.innerHTML = `<p style="color:red; text-align:center;">Erreur: ${data.error}</p>`;
            }
        } catch (error) {
            content.innerHTML = '<p style="color:red; text-align:center;">Erreur lors du chargement.</p>';
        }
    }

    function toggleOptions(btn) {
        const menu = btn.parentElement.querySelector('.options-menu');
        document.querySelectorAll('.options-menu').forEach(m => {
            if (m !== menu) m.classList.remove('active');
        });
        if (menu) menu.classList.toggle('active');
    }



    let pendingRefuseId = null;

    function openRefuseModal(id, clientRole = 'PARENT') {
        pendingRefuseId = id;
        
        const pDesc = document.querySelector('#refuseConfirmModal p');
        if (pDesc) {
            const roleTxt = (clientRole === 'APPRENANT') ? 'l\'apprenant' : 'le parent';
            pDesc.textContent = `Cette action est irréversible. ${roleTxt.charAt(0).toUpperCase() + roleTxt.slice(1)} sera notifié de votre refus.`;
        }
        
        document.getElementById('refuseConfirmModal').style.display = 'flex';
        
        const confirmBtn = document.getElementById('confirmRefuseBtn');
        confirmBtn.onclick = async function() {
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<span class="loader" style="width:16px;height:16px;border:2px solid #fff;border-bottom-color:transparent;border-radius:50%;display:inline-block;animation:spin 1s linear infinite;"></span>';
            await processEngAction(pendingRefuseId, 'refuser');
            closeRefuseModal();
        };
    }

    function closeRefuseModal() {
        pendingRefuseId = null;
        document.getElementById('refuseConfirmModal').style.display = 'none';
        const confirmBtn = document.getElementById('confirmRefuseBtn');
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = 'Confirmer le refus';
    }

    async function handleEngAction(id, action, isTrial = false, clientRole = 'PARENT', btnContext = null) {
        if (action === 'accepter') {
            if (btnContext) {
                btnContext.disabled = true;
                btnContext.innerHTML = '<span class="loader" style="width:16px;height:16px;border:2px solid currentColor;border-bottom-color:transparent;border-radius:50%;display:inline-block;animation:spin 1s linear infinite;"></span> Traitement...';
            }
            await processEngAction(id, 'accepter');
            closeEngModal();
            return;
        } else if (action === 'refuser') {
            closeEngModal();
            openRefuseModal(id, clientRole);
            return;
        }
        
        if (!confirm(`Voulez-vous vraiment ${action}er cet engagement ?`)) return;
        await processEngAction(id, action);
    }

    async function processEngAction(id, action) {
        try {
            const response = await fetch(`/api/engagement/${id}/action/`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({ action: action })
            });
            const data = await response.json();
            if (data.success) {
                if (action === 'accepter' && data.conversation_id) {
                    document.body.insertAdjacentHTML('beforeend', `
                        <div id="ephemeral-success-alert" style="position: fixed; top: 20px; right: 20px; background: #10b981; color: white; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 9999; font-weight: 500; opacity: 0; transition: opacity 0.3s; display: flex; align-items: center; gap: 0.75rem;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                            <div>
                                <strong style="display:block; font-size:1.05rem; margin-bottom:0.1rem;">Confirmation réussie !</strong>
                                <span style="font-size: 0.85rem; opacity:0.9;">Vous allez être redirigé vers la messagerie avec ce parent/apprenant...</span>
                            </div>
                        </div>
                    `);
                    setTimeout(() => document.getElementById('ephemeral-success-alert').style.opacity = '1', 10);
                    setTimeout(() => {
                        window.location.href = `/messagerie/${data.conversation_id}/`;
                    }, 2500);
                } else {
                    window.location.reload();
                }
            } else {
                alert(data.error || "Une erreur est survenue");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Une erreur de communication est survenue.");
        }
    }

    async function masquerEngagementProf(id, btn) {
        if (!confirm("Masquer cet engagement de votre liste ?")) return;
        try {
            const response = await fetch(`/api/engagement/${id}/masquer-prof/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': '{{ csrf_token }}' }
            });
            if (response.ok) {
                const card = btn.closest('.engagement-card');
                if (card) {
                    card.style.opacity = '0';
                    setTimeout(() => card.remove(), 300);
                }
            }
        } catch (e) { console.error(e); }
    }

    function closeEngModal() {
        document.getElementById('engModal').style.display = 'none';
    }

    // Fermer les menus au clic extérieur
    window.onclick = function(event) {
        if (!event.target.closest('.options-btn')) {
            document.querySelectorAll('.options-menu').forEach(menu => menu.classList.remove('active'));
        }
        if (event.target.classList.contains('modal-overlay')) {
            closeEngModal();
        }
    }

    function copyProfileLink(link) {
        navigator.clipboard.writeText(link).then(() => {
            const textEl = document.getElementById('copy-link-text');
            const originalText = textEl.textContent;
            textEl.textContent = "Lien copié ! ✓";
            textEl.style.color = "#16a34a";
            setTimeout(() => {
                textEl.textContent = originalText;
                textEl.style.color = "";
            }, 2000);
        });
    }

    function dismissAnnouncement(id) {
        const card = document.getElementById('announcement-card');
        if (card) {
            card.style.opacity = '0';
            setTimeout(() => {
                card.style.display = 'none';
            }, 300);
        }
        
        fetch(`/api/announcement/${id}/dismiss/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        }).catch(e => console.warn(e));
    }
    
    // Fonction helper si getCookie n'est pas définie
    if (typeof getCookie !== 'function') {
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    }
