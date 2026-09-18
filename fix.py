import sys

def modify_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'engagement_modal.html' in filepath:
        if 'function triggerEssaiModal' not in content:
            new_script = '''
function triggerEssaiModal(btn) {
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

    if 'teacher_profile.html' in filepath:
        old_onclick = "onclick=\"this.classList.add('loading'); setTimeout(() => this.classList.remove('loading'), 1000);\""
        new_onclick = "onclick=\"event.stopPropagation(); event.preventDefault(); this.classList.add('loading'); setTimeout(() => this.classList.remove('loading'), 1000); triggerEssaiModal(this);\""
        content = content.replace(old_onclick, new_onclick)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

modify_file('templates/core/components/engagement_modal.html')
modify_file('templates/core/components/teacher_profile.html')
print('Done!')
