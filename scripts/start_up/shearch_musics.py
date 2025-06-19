# scripts/start_up/search_musics.py
# Gère la recherche de musiques.

import os
import sys

# Importation de AUDIO_FORMATS et des modules mutagen car ils étaient initialement ici
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import FLAC
from mutagen.id3 import ID3NoHeaderError


# --- Formats audio supportés (pour la recherche) ---
AUDIO_FORMATS = ('.mp3', '.wav', '.ogg', '.flac')


class MusicFinder:
    """
    Recherche les fichiers musicaux dans des chemins spécifiés.
    """
    def __init__(self):
        # Chemins potentiels pour trouver les musiques
        self.potential_music_paths = [
            os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), 'Musiques'),
            # Dossier Musiques à côté de l'exe ou du script
            os.path.join(os.path.expanduser("~"), "Music")  # Dossier Musique de l'utilisateur
        ]
        self.found_musics = []

    def find_music_files(self):
        """Recherche les fichiers musicaux dans les chemins potentiels et retourne la liste."""
        for path in self.potential_music_paths:
            if os.path.isdir(path):
                print(f"Recherche dans : {path}")
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(AUDIO_FORMATS):
                            full_path = os.path.join(root, file)
                            self.found_musics.append(full_path)

        if not self.found_musics:
            print("Aucune musique trouvée dans les chemins spécifiés.")
        else:
            print(f"Musiques trouvées ({len(self.found_musics)}):")
            # Affiche seulement les 5 premières pour ne pas spammer
            for i, music in enumerate(self.found_musics[:5]):
                print(f"- {os.path.basename(music)}")
            if len(self.found_musics) > 5:
                print(f"... et {len(self.found_musics) - 5} autres.")
        return self.found_musics

# Les fonctions _get_audio_duration et _prepare_playlist ont été déplacées
# dans scripts/player/audio_info.py, donc elles ne sont plus ici.