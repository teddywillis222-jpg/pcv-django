import os
import cloudinary
from cloudinary_storage.storage import MediaCloudinaryStorage

class DynamicMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Storage Cloudinary intelligent et robuste :
    Détermine dynamiquement le 'resource_type' de Cloudinary en fonction de l'extension
    ou du type du fichier (notamment pour les vocaux et vidéos) afin d'éviter
    l'erreur 'Invalid image file' lors de l'upload et de garantir la génération de la
    bonne URL de streaming (/video/upload/...webm) pour la lecture audio/vidéo côté client.
    """

    def _get_resource_type(self, name):
        name_lower = (name or '').lower()

        # Cloudinary classe impérativement tous les audios et vidéos sous resource_type='video'
        audio_video_exts = (
            '.webm', '.mp3', '.ogg', '.wav', '.m4a', '.aac', '.mp4', '.mov', '.flac', '.opus'
        )
        if any(ext in name_lower for ext in audio_video_exts) or 'vocal_' in name_lower or '/audio' in name_lower or 'messages/media/vocal' in name_lower:
            return 'video'

        # Documents et archives bruts
        raw_exts = (
            '.pdf', '.doc', '.docx', '.zip', '.txt', '.xls', '.xlsx', '.csv', '.rar',
            '.ppt', '.pptx', '.odt', '.rtf', '.7z', '.tar', '.gz'
        )
        if any(ext in name_lower for ext in raw_exts):
            return 'raw'

        # Par défaut : image
        return 'image'

    def _get_url(self, name):
        res_type = self._get_resource_type(name)
        name = self._prepend_prefix(name)

        # Pour les fichiers vidéo/audio (comme les notes vocales 'vocal_...'), Cloudinary
        # requiert l'extension (.webm) dans l'URL pour servir le bon header Content-Type de streaming
        if res_type == 'video' and not any(name.lower().endswith(ext) for ext in ('.webm', '.mp3', '.ogg', '.wav', '.m4a', '.mp4', '.aac')):
            name = name + '.webm'

        cloudinary_resource = cloudinary.CloudinaryResource(name, default_resource_type=res_type)
        return cloudinary_resource.url
