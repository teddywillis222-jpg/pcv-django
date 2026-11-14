import os
from cloudinary_storage.storage import MediaCloudinaryStorage

class DynamicMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Storage Cloudinary intelligent et robuste :
    Détermine dynamiquement le 'resource_type' de Cloudinary en fonction de l'extension
    du fichier afin d'éviter l'erreur 'Invalid image file' lors de l'upload d'audios
    ou de documents.
    """

    def _get_resource_type(self, name):
        name_lower = (name or '').lower()

        # Cloudinary classe impérativement tous les audios et vidéos sous resource_type='video'
        audio_video_exts = (
            '.webm', '.mp3', '.ogg', '.wav', '.m4a', '.aac', '.mp4', '.mov', '.flac', '.opus'
        )
        if any(name_lower.endswith(ext) for ext in audio_video_exts):
            return 'video'

        # Documents et archives bruts
        raw_exts = (
            '.pdf', '.doc', '.docx', '.zip', '.txt', '.xls', '.xlsx', '.csv', '.rar'
        )
        if any(name_lower.endswith(ext) for ext in raw_exts):
            return 'raw'

        # Par défaut : image
        return 'image'
