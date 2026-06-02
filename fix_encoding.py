# -*- coding: utf-8 -*-
"""
Script de correction d'encodage pour views.py
Detecte et corrige les bytes Latin-1 isoles dans un fichier sinon UTF-8.
"""
import os
import shutil
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

target = os.path.join(os.getcwd(), 'core', 'views.py')

# 1. Backup
backup = target + '.bak_encoding2'
if not os.path.exists(backup):
    shutil.copy2(target, backup)
    print(f"[OK] Backup cree : {backup}")
else:
    print(f"[INFO] Backup existe deja : {backup}")

# 2. Lire le contenu brut
with open(target, 'rb') as f:
    raw = f.read()

print(f"[INFO] Taille brute : {len(raw)} bytes")

# 3. Scanner pour les bytes Latin-1 isoles (0x80-0xBF sans prefixe UTF-8 valide)
latin1_positions = []
i = 0
while i < len(raw):
    b = raw[i]
    if b < 0x80:
        i += 1
    elif 0xC2 <= b <= 0xDF and i + 1 < len(raw) and 0x80 <= raw[i+1] <= 0xBF:
        # Valid 2-byte UTF-8
        i += 2
    elif 0xE0 <= b <= 0xEF and i + 2 < len(raw) and 0x80 <= raw[i+1] <= 0xBF and 0x80 <= raw[i+2] <= 0xBF:
        # Valid 3-byte UTF-8
        i += 3
    elif 0xF0 <= b <= 0xF4 and i + 3 < len(raw) and all(0x80 <= raw[i+j] <= 0xBF for j in range(1, 4)):
        # Valid 4-byte UTF-8
        i += 4
    elif 0x80 <= b <= 0xFF:
        # Isolated non-ASCII byte = Latin-1
        latin1_positions.append(i)
        i += 1
    elif 0xC0 <= b <= 0xC1:
        # Overlong UTF-8, treat as Latin-1
        latin1_positions.append(i)
        i += 1
    else:
        i += 1

print(f"[INFO] Bytes Latin-1 isoles trouves : {len(latin1_positions)}")

if len(latin1_positions) == 0:
    print("[OK] Aucun byte Latin-1 isole. Le fichier est deja correctement encode.")
    if os.path.exists(backup):
        os.remove(backup)
    exit(0)

# 4. Show some examples
for pos in latin1_positions[:10]:
    b = raw[pos]
    char = bytes([b]).decode('latin-1')
    ctx_start = max(0, pos - 15)
    ctx_end = min(len(raw), pos + 15)
    # Only show ASCII context
    ctx = raw[ctx_start:ctx_end]
    ctx_str = ''.join(chr(c) if 32 <= c < 127 else f'[{hex(c)}]' for c in ctx)
    print(f"  Position {pos}: byte {hex(b)} = '{char}' | contexte: ...{ctx_str}...")

# 5. Reconstruct with proper UTF-8
result_bytes = bytearray()
i = 0
fixed = 0

while i < len(raw):
    b = raw[i]
    if b < 0x80:
        result_bytes.append(b)
        i += 1
    elif 0xC2 <= b <= 0xDF and i + 1 < len(raw) and 0x80 <= raw[i+1] <= 0xBF:
        result_bytes.extend(raw[i:i+2])
        i += 2
    elif 0xE0 <= b <= 0xEF and i + 2 < len(raw) and 0x80 <= raw[i+1] <= 0xBF and 0x80 <= raw[i+2] <= 0xBF:
        result_bytes.extend(raw[i:i+3])
        i += 3
    elif 0xF0 <= b <= 0xF4 and i + 3 < len(raw) and all(0x80 <= raw[i+j] <= 0xBF for j in range(1, 4)):
        result_bytes.extend(raw[i:i+4])
        i += 4
    elif 0x80 <= b <= 0xFF:
        # Convert Latin-1 byte to UTF-8
        char = bytes([b]).decode('latin-1')
        result_bytes.extend(char.encode('utf-8'))
        fixed += 1
        i += 1
    else:
        result_bytes.append(b)
        i += 1

# 6. Verify the result is valid UTF-8
try:
    content = result_bytes.decode('utf-8')
    print(f"[OK] Resultat decode en UTF-8 avec succes")
except UnicodeDecodeError as e:
    print(f"[ERREUR] Le resultat n'est pas du UTF-8 valide : {e}")
    exit(1)

# 7. Write back
with open(target, 'wb') as f:
    f.write(result_bytes)

print(f"[OK] {fixed} bytes Latin-1 convertis en UTF-8")
print(f"[OK] Fichier reecrit : {target}")

# 8. Quick verify
with open(target, 'r', encoding='utf-8') as f:
    verify = f.read()
accents = sum(1 for c in verify if ord(c) > 127)
print(f"[VERIF] {accents} caracteres non-ASCII (accents, emojis, etc.)")
print(f"[VERIF] Taille finale : {len(verify)} caracteres, {os.path.getsize(target)} bytes")
