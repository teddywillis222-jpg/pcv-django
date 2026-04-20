import os
import re

path = r"c:\Users\JGA'TIC BENIN\Documents\ProfChezVous\templates\core\parent_dashboard.html"
output_path = r"c:\Users\JGA'TIC BENIN\Documents\ProfChezVous\templates\core\parent_dashboard_fixed.html"

try:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip leading/trailing whitespace
    content = content.strip()
    
    # Simple formatting: add newlines after tags
    content = content.replace('>', '>\n')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed file created at {output_path}. Size: {len(content)} bytes.")
except Exception as e:
    print(f"Error: {e}")
