"""
Filtre de template Django pour optimiser les images Cloudinary.
Injecte les transformations Cloudinary (resize, format WebP, qualité)
directement dans l'URL sans toucher au modèle ni à l'upload.
"""
from django import template
import re

register = template.Library()


@register.filter(name='cloudinary_optimized')
def cloudinary_optimized(url, dimensions="400x500"):
    """
    Transforme une URL Cloudinary pour servir une image optimisée.
    
    Usage dans un template :
        {{ teacher.photo_de_profil.url|cloudinary_optimized:"400x500" }}
    
    Résultat :
        Insère /upload/w_400,h_500,c_fill,g_face,f_auto,q_auto/ dans l'URL.
        - w_400,h_500 : resize exact aux dimensions de la carte
        - c_fill : crop intelligent pour remplir le cadre
        - g_face : centrage automatique sur le visage
        - f_auto : sert du WebP aux navigateurs compatibles, JPEG sinon
        - q_auto : qualité automatique optimale (bon compromis poids/qualité)
    """
    if not url:
        return url
    
    url = str(url)
    
    # Vérifier que c'est bien une URL Cloudinary
    if 'cloudinary' not in url and 'res.cloudinary.com' not in url:
        return url
    
    # Parser les dimensions
    try:
        width, height = dimensions.split('x')
    except ValueError:
        width, height = '400', '500'
    
    transformation = f"w_{width},h_{height},c_fill,g_face,f_auto,q_auto"
    
    # Insérer la transformation après /upload/
    # Pattern : .../upload/... → .../upload/<transformation>/...
    # Si des transformations existent déjà, on les remplace
    if '/upload/' in url:
        # Vérifier s'il y a déjà des transformations (pattern: /upload/v1234/ ou /upload/w_xxx/)
        url = re.sub(
            r'/upload/(?:v\d+/)?',
            f'/upload/{transformation}/',
            url,
            count=1
        )
    
    return url

@register.filter(name='cloudinary_og')
def cloudinary_og(url):
    """
    Transforme une URL Cloudinary pour servir une image Open Graph (Facebook, WhatsApp).
    Oblige le format JPEG (f_jpg) car Facebook gère mal les WebP.
    Centre sur le visage (g_face) avec une dimension carrée idéale (600x600).
    Force l'URL absolue HTTPS.
    """
    if not url:
        return url
    
    url = str(url)
    
    # Si c'est une URL Cloudinary, on force le HTTPS
    if 'res.cloudinary.com' in url:
        if url.startswith('//'):
            url = 'https:' + url
        elif url.startswith('http://'):
            url = url.replace('http://', 'https://')
            
    if 'cloudinary' not in url and 'res.cloudinary.com' not in url:
        return url
    
    transformation = "w_600,h_600,c_fill,g_face,f_jpg,q_auto"
    if '/upload/' in url:
        url = re.sub(
            r'/upload/(?:v\d+/)?',
            f'/upload/{transformation}/',
            url,
            count=1
        )
    
    # En plus, remplacer l'extension .webp par .jpg à la fin de l'URL pour plus de sécurité
    url = re.sub(r'\.webp$', '.jpg', url, flags=re.IGNORECASE)
    
    return url
