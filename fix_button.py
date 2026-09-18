def fix_button(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply changes to engagement_modal.html
    if 'engagement_modal.html' in filepath:
        if 'function triggerEssaiModal' not in content:
            new_script = '''
function triggerEssaiModal(btn) {
    btn.classList.add('loading');
    setTimeout(() => btn.classList.remove('loading'), 1000);
    const teacherId = btn.dataset.teacherId;
    const teacherName = btn.dataset.teacherName;
    const matiere = btn.dataset.matiere;
    const isParent = btn.dataset.isParent === 'True' || btn.dataset.isParent === 'true';
    const isPremium = btn.dataset.isPremium === 'True' || btn.dataset.isPremium === 'true';
    const essaiActif = btn.dataset.essaiActif === 'True' || btn.dataset.essaiActif === 'true';
    const classesStr = btn.dataset.classes || '';
    const children = window.currentChildren || [];
    const existingEng = window.currentExistingEngagement || null;
    openEssaiForm(teacherId, teacherName, matiere, isParent, isPremium, essaiActif, children, existingEng, classesStr);
}
'''
            content = content.replace('function openEssaiForm', new_script + '\nfunction openEssaiForm')

    # Apply changes to teacher_profile.html
    if 'teacher_profile.html' in filepath:
        old_onclick1 = "onclick=\"event.stopPropagation(); event.preventDefault(); this.classList.add('loading'); setTimeout(() => this.classList.remove('loading'), 1000); triggerEssaiModal(this);\""
        new_onclick = "onclick=\"triggerEssaiModal(this)\""
        content = content.replace(old_onclick1, new_onclick)
        
        old_onclick2 = "onclick=\"this.classList.add('loading'); setTimeout(() => this.classList.remove('loading'), 1000);\""
        content = content.replace(old_onclick2, new_onclick)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_button('templates/core/components/engagement_modal.html')
fix_button('templates/core/components/teacher_profile.html')
print('Done!')
