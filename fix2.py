def fix_mojibake(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    replacements = {
        'Ã©': 'é',
        'Ã¨': 'è',
        'Ãª': 'ê',
        'Ã«': 'ë',
        'Ã\xa0': 'à',
        'Ã¢': 'â',
        'Ã´': 'ô',
        'Ã¯': 'ï',
        'Ã§': 'ç',
        'Ã»': 'û',
        'Ã¹': 'ù',
        'â€™': '’',
        'â€œ': '“',
        'â€ ': '”',
        'Â«': '«',
        'Â»': '»',
        'Â': ' ',
        'Å“': 'œ',
        'Ã‰': 'É',
        'Ã€': 'À',
        'â€“': '–',
        'â€”': '—'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)

fix_mojibake('templates/core/components/engagement_modal.html')
fix_mojibake('templates/core/components/teacher_profile.html')
print('Done!')
