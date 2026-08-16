"""
Filtre de template Django pour optimiser les images Cloudinary.
Injecte les transformations Cloudinary (resize, format WebP, qualité)
directement dans l'URL sans toucher au modèle ni à l'upload.
"""
from django import template
import re
import logging

logger = logging.getLogger(__name__)
register = template.Library()


def _inject_cloudinary_transformation(url, transformation):
    """
    Injecte une chaîne de transformation Cloudinary dans une URL
    en respectant le format officiel :
        /upload/<transformation>/v<version>/<public_id>.<ext>

    Cloudinary exige que les transformations soient placées AVANT
    le numéro de version (v1234...) pour que l'URL soit valide.
    """
    url = str(url)

    # Sécurité : ne rien faire si ce n'est pas une URL Cloudinary
    if 'res.cloudinary.com' not in url:
        return url

    # Forcer HTTPS
    if url.startswith('//'):
        url = 'https:' + url
    elif url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)

    if '/upload/' not in url:
        return url

    # Supprimer les transformations existantes (tout entre /upload/ et /v<digits>/ ou /media/)
    # Format Cloudinary : /upload/[transformations_existantes/]v<digits>/public_id
    # On remplace par :   /upload/<nouvelle_transformation>/v<digits>/public_id
    url = re.sub(
        r'/upload/(?:[^/]+/)*?(v\d+/)',
        f'/upload/{transformation}/\\1',
        url,
        count=1
    )

    # Si pas de version dans l'URL (ex: /upload/media/...), injecter avant le chemin
    if f'/upload/{transformation}/' not in url:
        url = url.replace('/upload/', f'/upload/{transformation}/', 1)

    return url


@register.filter(name='cloudinary_optimized')
def cloudinary_optimized(url, dimensions="400x500"):
    """
    Transforme une URL Cloudinary pour servir une image optimisée.

    Usage dans un template :
        {{ teacher.photo_de_profil.url|cloudinary_optimized:"400x500" }}
    """
    if not url:
        return url

    url = str(url)

    if 'cloudinary' not in url and 'res.cloudinary.com' not in url:
        return url

    try:
        width, height = dimensions.split('x')
    except ValueError:
        width, height = '400', '500'

    transformation = f"w_{width},h_{height},c_fill,g_face,f_auto,q_auto"
    return _inject_cloudinary_transformation(url, transformation)


@register.filter(name='cloudinary_og')
def cloudinary_og(url):
    """
    Transforme une URL Cloudinary pour servir une image Open Graph
    (Facebook, WhatsApp, LinkedIn).

    Standard Facebook 2025 :
    - Format JPEG obligatoire (f_jpg) — Facebook gère mal le WebP pour les aperçus
    - Dimensions 1200×630 px (ratio 1.91:1 — standard cross-platform)
    - Centrage sur le visage (g_face)
    - Qualité auto optimale (q_auto)
    - URL absolue HTTPS obligatoire
    """
    if not url:
        return url

    transformation = "w_1200,h_630,c_fill,g_face,f_jpg,q_auto"
    return _inject_cloudinary_transformation(url, transformation)
