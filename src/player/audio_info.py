# src/player/audio_info.py
import os
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
from mutagen.id3 import ID3NoHeaderError

AUDIO_FORMATS = ('.mp3', '.wav', '.ogg', '.flac')

def _extract_metadata(audio_info):
    """
    Extrait le titre, l'artiste et l'album des objets audio de mutagen.
    Retourne un dictionnaire avec les métadonnées.
    """
    title = ""
    artist = ""
    album = ""

    if isinstance(audio_info, MP3):
        title = audio_info.get('TIT2', [''])[0] if 'TIT2' in audio_info else ''
        artist = audio_info.get('TPE1', [''])[0] if 'TPE1' in audio_info else ''
        album = audio_info.get('TALB', [''])[0] if 'TALB' in audio_info else ''
    elif isinstance(audio_info, (WAVE, OggVorbis, FLAC)):
        # Pour d'autres formats, les tags sont souvent stockés différemment
        # Ces clés sont des exemples courants pour OGG/FLAC
        title = audio_info.get('title', [''])[0] if 'title' in audio_info else ''
        artist = audio_info.get('artist', [''])[0] if 'artist' in audio_info else ''
        album = audio_info.get('album', [''])[0] if 'album' in audio_info else ''

    # Retourne le nom du fichier comme titre par défaut si aucun tag n'est trouvé
    return {
        'title': title if title else "Titre inconnu",
        'artist': artist if artist else "Artiste inconnu",
        'album': album if album else "Album inconnu"
    }


def get_audio_info(filepath):
    """
    Tente d'obtenir la durée et les métadonnées (titre, artiste, album) d'un fichier audio.
    Retourne un dictionnaire avec 'duration_ms' et 'metadata' (un autre dict),
    ou None si le fichier n'est pas supporté/corrompu.
    """
    duration_ms = None
    metadata = {
        'title': "Titre inconnu",
        'artist': "Artiste inconnu",
        'album': "Album inconnu"
    }

    try:
        file_extension = os.path.splitext(filepath)[1].lower()
        audio_info_obj = None

        if file_extension == '.mp3':
            audio_info_obj = MP3(filepath)
        elif file_extension == '.wav':
            audio_info_obj = WAVE(filepath)
        elif file_extension == '.ogg':
            audio_info_obj = OggVorbis(filepath)
        elif file_extension == '.flac':
            audio_info_obj = FLAC(filepath)

        if audio_info_obj:
            # Extraire la durée
            if hasattr(audio_info_obj, 'info') and hasattr(audio_info_obj.info, 'length'):
                duration_ms = int(audio_info_obj.info.length * 1000)

            # Extraire les métadonnées
            metadata = _extract_metadata(audio_info_obj)
            # Si le titre est inconnu, utilise le nom du fichier
            if metadata['title'] == "Titre inconnu":
                metadata['title'] = os.path.splitext(os.path.basename(filepath))[0]

            return {
                'path': filepath,
                'duration_ms': duration_ms,
                'metadata': metadata
            }

        else:
            print(f"Avertissement: Format non supporté ou fichier non lisible : {os.path.basename(filepath)}")
            return None

    except ID3NoHeaderError:
        print(f"Info: Le fichier {os.path.basename(filepath)} est un MP3 sans tags ID3. La durée peut être correcte, le titre sera le nom de fichier.")
        try:
            audio_info_obj = MP3(filepath)
            if hasattr(audio_info_obj.info, 'length'):
                duration_ms = int(audio_info_obj.info.length * 1000)
            metadata['title'] = os.path.splitext(os.path.basename(filepath))[0]
            return {
                'path': filepath,
                'duration_ms': duration_ms,
                'metadata': metadata
            }
        except Exception as e:
            print(f"Erreur mutagen (ID3 ou autre) sur {os.path.basename(filepath)}: {e}")
            return None
    except Exception as e:
        print(f"Erreur mutagen sur {os.path.basename(filepath)}: {e}")
        return None

def prepare_playlist_with_durations(raw_playlist):
    """
    Prépare une playlist en y ajoutant la durée et les métadonnées de chaque morceau.
    Les morceaux dont la durée ne peut être obtenue sont ignorés.
    """
    prepared_list = []
    for path in raw_playlist:
        audio_data = get_audio_info(path)
        if audio_data and audio_data['duration_ms'] is not None:
            prepared_list.append(audio_data)
        else:
            print(f"Avertissement: Impossible d'obtenir la durée ou les infos de {os.path.basename(path)}. Le morceau sera ignoré ou sa barre de progression sera imprécise.")
    return prepared_list