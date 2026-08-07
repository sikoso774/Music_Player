# src/player/audio_info.py
import os

import mutagen

# Formats supportés pour la recherche de musiques. La lecture (VLC) et la
# lecture des tags (mutagen.File, auto-détection) supportent un éventail de
# formats bien plus large que ça ; cette liste ne filtre que la découverte.
AUDIO_FORMATS = ('.mp3', '.wav', '.ogg', '.opus', '.flac', '.m4a', '.aac', '.wma', '.aiff', '.aif')


def get_audio_info(filepath):
    """
    Tente d'obtenir la durée et les métadonnées (titre, artiste, album) d'un fichier audio.
    Retourne un dictionnaire avec 'duration_ms' et 'metadata' (un autre dict),
    ou None si le fichier n'est pas supporté/corrompu.
    """
    try:
        audio = mutagen.File(filepath, easy=True)

        if audio is None:
            print(f"Avertissement: Format non supporté ou fichier non lisible : {os.path.basename(filepath)}")
            return None

        duration_ms = None
        if hasattr(audio, 'info') and hasattr(audio.info, 'length'):
            duration_ms = int(audio.info.length * 1000)

        title = audio.get('title', [''])[0]
        artist = audio.get('artist', [''])[0]
        album = audio.get('album', [''])[0]

        metadata = {
            'title': title if title else os.path.splitext(os.path.basename(filepath))[0],
            'artist': artist if artist else "Artiste inconnu",
            'album': album if album else "Album inconnu",
        }

        return {
            'path': filepath,
            'duration_ms': duration_ms,
            'metadata': metadata
        }

    except Exception as e:
        print(f"Erreur mutagen sur {os.path.basename(filepath)}: {e}")
        return None


def get_cover_bytes(filepath):
    """
    Retourne les octets de la pochette intégrée au fichier audio, ou None si absente.
    Couvre les cas les plus courants : MP3 (APIC), FLAC (pictures), MP4/M4A (covr).
    """
    try:
        audio = mutagen.File(filepath)
        if audio is None:
            return None

        tags = audio.tags

        # MP3 / ID3 : frames APIC
        if tags is not None and hasattr(tags, 'getall'):
            apics = tags.getall('APIC')
            if apics:
                return apics[0].data

        # FLAC : liste de pictures
        pictures = getattr(audio, 'pictures', None)
        if pictures:
            return pictures[0].data

        # MP4 / M4A : atome 'covr'
        if tags is not None and 'covr' in tags:
            covers = tags['covr']
            if covers:
                return bytes(covers[0])

        return None
    except Exception:
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
