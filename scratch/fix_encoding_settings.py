"""
Fix encoding issues in settings.py:
1. Read with latin-1 (which reads any byte)
2. Write back as UTF-8
"""
import os

settings_path = os.path.join('config', 'settings.py')

with open(settings_path, 'rb') as f:
    raw = f.read()

# Decode as latin-1 (will never fail, reads any byte value)
text = raw.decode('latin-1')

# Write back as UTF-8 (BOM-free)
with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("OK: settings.py re-encoded as UTF-8")
