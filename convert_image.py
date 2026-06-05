import os
from PIL import Image

image_path = r"c:\Users\JGA'TIC BENIN\Documents\ProfChezVous\core\static\core\images\hero_prof_benin.png"
output_path = r"c:\Users\JGA'TIC BENIN\Documents\ProfChezVous\core\static\core\images\hero_prof_benin.webp"

if os.path.exists(image_path):
    with Image.open(image_path) as img:
        img.save(output_path, "WEBP", quality=80)
    print(f"Image saved to {output_path}")
else:
    print(f"File not found: {image_path}")
