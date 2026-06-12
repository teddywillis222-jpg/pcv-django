import codecs

with codecs.open('templates/core/prof_create_profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize newlines to avoid mismatch on Windows
content = content.replace('\r\n', '\n')

new_style = '''
    /* Stepper UI */
    .stepper-container { margin-bottom: 3rem; padding: 0 1rem; }
    .stepper { display: flex; justify-content: space-between; position: relative; max-width: 600px; margin: 0 auto; }
    .stepper::before { content: ''; position: absolute; top: 20px; left: 0; width: 100%; height: 4px; background: var(--border-color); z-index: 1; border-radius: 4px; }
    .stepper-progress { position: absolute; top: 20px; left: 0; height: 4px; background: var(--primary); z-index: 2; border-radius: 4px; transition: width 0.4s ease; width: 0%; }
    .step-item { position: relative; z-index: 3; display: flex; flex-direction: column; align-items: center; width: 33.33%; }
    .step-circle { width: 44px; height: 44px; border-radius: 50%; background: var(--card-bg); border: 4px solid var(--border-color); display: flex; align-items: center; justify-content: center; font-weight: 800; color: var(--text-gray); transition: all 0.4s ease; }
    .step-title { margin-top: 0.8rem; font-size: 0.85rem; font-weight: 700; color: var(--text-gray); text-align: center; transition: color 0.4s ease; }
    .step-item.active .step-circle { border-color: var(--primary); background: var(--primary); color: white; }
    .step-item.active .step-title { color: var(--primary); }
    .step-item.completed .step-circle { border-color: var(--primary); background: var(--primary); color: white; }
    .form-step { display: none; animation: fadeIn 0.4s ease; }
    .form-step.active { display: block; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .form-actions { display: flex; justify-content: space-between; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px dashed var(--border-color); gap: 1rem; }
    .btn-action { padding: 1rem 2rem; border-radius: 14px; font-size: 1rem; font-weight: 800; cursor: pointer; transition: all 0.2s; border: none; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }
    .btn-prev { background: #f1f5f9; color: #475569; }
    .btn-prev:hover { background: #e2e8f0; }
    .btn-next, .btn-submit { background: var(--primary); color: white; flex: 1; max-width: 250px; box-shadow: 0 8px 16px rgba(22, 163, 74, 0.2); }
    .btn-next:hover, .btn-submit:hover { transform: translateY(-2px); background: #15803d; }
    .form-section { border: none; padding-bottom: 0; margin-bottom: 0; }
    .section-title { font-size: 1.4rem; text-align: center; margin-bottom: 2rem; color: var(--text-dark); }
    .invalid-field { border-color: #ef4444 !important; background-color: #fef2f2 !important; }
    .error-msg { color: #ef4444; font-size: 0.8rem; margin-top: 0.3rem; font-weight: 600; display: none; }
'''

content = content.replace('.alert-error {', new_style + '\n    .alert-error {')

old_form_start = '    <form id="profileCreationForm" method="post" enctype="multipart/form-data">\n        {% csrf_token %}'

new_form_start = '''    <form id="profileCreationForm" method="post" enctype="multipart/form-data" novalidate>
        {% csrf_token %}
        <div class="stepper-container">
            <div class="stepper">
                <div class="stepper-progress" id="stepperProgress"></div>
                <div class="step-item active" id="step-nav-1">
                    <div class="step-circle">1</div>
                    <div class="step-title">Identité</div>
                </div>
                <div class="step-item" id="step-nav-2">
                    <div class="step-circle">2</div>
                    <div class="step-title">Expertise</div>
                </div>
                <div class="step-item" id="step-nav-3">
                    <div class="step-circle">3</div>
                    <div class="step-title">Validation</div>
                </div>
            </div>
        </div>
'''

content = content.replace(old_form_start, new_form_start)

content = content.replace('<!-- 1. IDENTITE -->', '<!-- 1. IDENTITE -->\n        <div class="form-step active" id="step-1">')

old_step_2 = '<!-- 2. EXPERTISE & LOGISTIQUE -->'
new_step_2 = '''            <div class="form-actions">
                <div></div>
                <button type="button" class="btn-action btn-next" onclick="nextStep(1)">Suivant ➔</button>
            </div>
        </div>
        <!-- 2. EXPERTISE & LOGISTIQUE -->
        <div class="form-step" id="step-2">'''
content = content.replace(old_step_2, new_step_2)

old_step_3 = '<!-- 3. GESTION DES DIPLOMES -->'
new_step_3 = '''            <div class="form-actions">
                <button type="button" class="btn-action btn-prev" onclick="prevStep(2)">⬅ Retour</button>
                <button type="button" class="btn-action btn-next" onclick="nextStep(2)">Suivant ➔</button>
            </div>
        </div>
        <!-- 3. GESTION DES DIPLOMES -->
        <div class="form-step" id="step-3">'''
content = content.replace(old_step_3, new_step_3)

old_submit = '''            <button type="submit" class="submit-btn" id="mainSubmitBtn" style="margin-top: 2rem;">
                Soumettre pour validation ➔
            </button>
        </div>

    </form>'''

new_submit = '''            <div class="form-actions">
                <button type="button" class="btn-action btn-prev" onclick="prevStep(3)">⬅ Retour</button>
                <button type="submit" class="btn-action btn-submit" id="mainSubmitBtn">
                    Soumettre le dossier ➔
                </button>
            </div>
        </div>
    </form>'''

content = content.replace(old_submit, new_submit)

js_logic = '''
    // Stepper Logic
    let currentStep = 1;
    const totalSteps = 3;

    window.nextStep = function(step) {
        if (!validateStep(step)) return;
        
        document.getElementById(`step-${step}`).classList.remove('active');
        document.getElementById(`step-${step + 1}`).classList.add('active');
        
        document.getElementById(`step-nav-${step}`).classList.add('completed');
        document.getElementById(`step-nav-${step}`).classList.remove('active');
        document.getElementById(`step-nav-${step + 1}`).classList.add('active');
        
        updateProgress(step + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    window.prevStep = function(step) {
        document.getElementById(`step-${step}`).classList.remove('active');
        document.getElementById(`step-${step - 1}`).classList.add('active');
        
        document.getElementById(`step-nav-${step}`).classList.remove('active');
        document.getElementById(`step-nav-${step - 1}`).classList.add('active');
        document.getElementById(`step-nav-${step - 1}`).classList.remove('completed');
        
        updateProgress(step - 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function updateProgress(step) {
        const progress = document.getElementById('stepperProgress');
        const percentage = ((step - 1) / (totalSteps - 1)) * 100;
        progress.style.width = percentage + '%';
    }

    function validateStep(step) {
        let isValid = true;
        const stepContainer = document.getElementById(`step-${step}`);
        const inputs = stepContainer.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            // Remove previous error styling
            input.classList.remove('invalid-field');
            const errorMsg = input.parentNode.querySelector('.error-msg');
            if(errorMsg) errorMsg.remove();

            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('invalid-field');
                
                // Add error message text
                const msg = document.createElement('div');
                msg.className = 'error-msg';
                msg.textContent = 'Ce champ est requis.';
                msg.style.display = 'block';
                input.parentNode.appendChild(msg);
            }
        });
        
        // Special validation for file inputs
        if(step === 1) {
            const photoInput = document.querySelector('input[name="photo_de_profil"]');
            const cniInput = document.querySelector('input[name="fichier_cni"]');
            
            if(photoInput && photoInput.hasAttribute('required') && !photoInput.value) {
                isValid = false;
                photoInput.parentNode.classList.add('invalid-field');
            }
            if(cniInput && cniInput.hasAttribute('required') && !cniInput.value) {
                isValid = false;
                cniInput.parentNode.classList.add('invalid-field');
            }
        }

        if(!isValid) {
            const toast = document.createElement('div');
            toast.style.position = 'fixed';
            toast.style.bottom = '20px';
            toast.style.right = '20px';
            toast.style.background = '#ef4444';
            toast.style.color = 'white';
            toast.style.padding = '1rem 2rem';
            toast.style.borderRadius = '12px';
            toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.1)';
            toast.style.zIndex = '9999';
            toast.textContent = 'Veuillez remplir tous les champs obligatoires en rouge.';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
        }

        return isValid;
    }
'''

content = content.replace('// Soumission asynchrone avec compression et barre de progression', js_logic + '\n    // Soumission asynchrone avec compression et barre de progression')

with codecs.open('templates/core/prof_create_profile.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
