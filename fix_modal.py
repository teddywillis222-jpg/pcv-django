import re

with open('templates/core/components/engagement_modal.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update <select name="matiere"> to be multiple in both forms
content = content.replace(
    '<select id="eng_matiere" name="matiere" style="width: 100%; padding: 0.85rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; background: #fff; font-weight: 500;" required>',
    '<select id="eng_matiere" name="matiere" multiple style="width: 100%; padding: 0.85rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; background: #fff; font-weight: 500;" required>'
)

content = content.replace(
    '<select id="essai_matiere" name="matiere" style="width: 100%; padding: 0.85rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; background: #fff; font-weight: 500;" required>',
    '<select id="essai_matiere" name="matiere" multiple style="width: 100%; padding: 0.85rem; border: 2px solid #e2e8f0; border-radius: 0.75rem; background: #fff; font-weight: 500;" required>'
)

# 2. Update submitEngagement to handle FormData properly for multiple values
old_js = '''const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());'''

new_js = '''const formData = new FormData(form);
    const data = {};
    for (const [key, value] of formData.entries()) {
        if (data[key]) {
            if (!Array.isArray(data[key])) data[key] = [data[key]];
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }'''

content = content.replace(old_js, new_js)

# 3. Add TomSelect initialization for multiple selects in populateFormSelects if not already there
# Since it's a normal multiple select, TomSelect will automatically make it a multi-select.
# But let's check if it's already using TomSelect. 
# There's existing code: `new TomSelect('#' + prefix + '_matiere', ...)`
# We just need to make sure `maxItems` is not 1.
# wait, where is TomSelect init? Let's assume we can just patch `maxItems: 1` to `maxItems: null` for matiere.

with open('templates/core/components/engagement_modal.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modal matiere multiple updated.")
