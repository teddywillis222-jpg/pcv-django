import os
import json

path = r"c:\Users\JGA'TIC BENIN\Documents\ProfChezVous\templates\core\prof_dashboard.html"
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<script>')
end = html.rfind('</script>')
js = html[start+8:end]

with open('test_js.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Extracted JS.")
