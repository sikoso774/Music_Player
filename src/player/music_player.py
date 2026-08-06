# src/player/music_player.py
from src.time_format import format_time

from .audio_info import prepare_playlist_with_durations
from .vlc_setup import create_vlc_player, quit_vlc_player
from .player_logic import load_and_play, pause_music, unpause_music, stop_current_music, \
    seek_to, is_track_ended, get_playback_time_ms, get_volume_percent, set_volume_percent


class MusicPlayer:
    """
    Gère la lecture, la pause, la reprise et le changement de musiques
    en utilisant VLC et en maintenant un état précis.
    """

    def __init__(self, playlist):
        # Instance VLC et lecteur média dédiés à ce MusicPlayer (pas d'état global).
        self._vlc_instance, self._media_player = create_vlc_player()
        self.playlist = prepare_playlist_with_durations(playlist)

        self.current_track_index = 0
        self.is_paused = False  # Indique si le lecteur est en état de pause
        self.is_playing = False  # Indique si une musique est chargée et potentiellement en lecture/pause

        if not self.playlist:
            print("Attention : La playlist est vide. Aucune musique ne pourra être jouée.")

    def load_and_play_music(self, track_index=None, start_pos_ms=0):
        """
        Charge et lance une musique à partir d'un index donné (ou l'index actuel)
        et une position de départ.
        """
        if not self.playlist:
            print("La playlist est vide, impossible de charger une musique.")
            return

        if track_index is not None:
            if not (0 <= track_index < len(self.playlist)):
                print(f"Index de morceau invalide: {track_index}")
                return
            self.current_track_index = track_index
        elif self.current_track_index >= len(self.playlist):
            self.current_track_index = 0

        track_info = self.playlist[self.current_track_index]
        track_path = track_info['path']

        if load_and_play(self._vlc_instance, self._media_player, track_path, start_pos_ms):
            self.is_playing = True
            self.is_paused = False  # La musique est en lecture, pas en pause
        else:
            self.is_playing = False  # Échec du chargement/lecture
            self.is_paused = False

    def toggle_pause(self):
        """
        Bascule l'état de pause/lecture de la musique.
        Gère les variables d'état internes et appelle les fonctions VLC appropriées.
        """
        if not self.is_playing:
            if self.playlist:
                self.load_and_play_music(self.current_track_index)
            return

        if self.is_paused:
            unpause_music(self._media_player)
            self.is_paused = False
        else:
            pause_music(self._media_player)
            self.is_paused = True

    def play_next_music(self):
        """Passe à la musique suivante dans la playlist."""
        print("Passage à la musique suivante.")
        if not self.playlist:
            return

        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.load_and_play_music(self.current_track_index)

    def play_previous_music(self):
        """Revient à la musique précédente dans la playlist."""
        print("Passage à la musique précédente.")
        if not self.playlist:
            return

        self.current_track_index = (self.current_track_index - 1 + len(self.playlist)) % len(self.playlist)
        self.load_and_play_music(self.current_track_index)

    def seek_music(self, position_ms):
        """
        Déplace la lecture à une position spécifique en millisecondes.
        Si la musique n'est pas déjà chargée, elle la charge et la lance à cette position.
        """
        print(f"Déplacement à {position_ms / 1000.0:.2f}s.")
        if not self.playlist:
            print("Impossible de faire un seek : la playlist est vide.")
            return

        current_duration_ms = self.get_current_track_duration_ms()
        if current_duration_ms == 0:
            print("Impossible de faire un seek : durée du morceau inconnue.")
            return

        new_position_ms = max(0, min(position_ms, current_duration_ms - 100))  # 100ms de marge

        if self.is_playing:
            # Le morceau est déjà chargé : VLC permet de sauter directement,
            # sans recharger le fichier.
            seek_to(self._media_player, new_position_ms)
        else:
            self.load_and_play_music(track_index=self.current_track_index, start_pos_ms=new_position_ms)

    def get_current_time_ms(self):
        """Retourne le temps de lecture actuel en millisecondes."""
        if self.is_playing:
            return get_playback_time_ms(self._media_player)
        return 0 # Si pas en lecture du tout

    def get_current_track_duration_ms(self):
        """Retourne la durée totale du morceau en cours en millisecondes."""
        if self.playlist and 0 <= self.current_track_index < len(self.playlist):
            return self.playlist[self.current_track_index].get('duration_ms', 0)
        return 0

    def get_current_track_metadata(self):
        """Retourne le dictionnaire de métadonnées du morceau en cours."""
        if self.playlist and 0 <= self.current_track_index < len(self.playlist):
            return self.playlist[self.current_track_index].get('metadata', {
                'title': "Titre inconnu",
                'artist': "Artiste inconnu",
                'album': "Album inconnu"
            })
        return {
            'title': "Aucune musique",
            'artist': "",
            'album': ""
        }

    def get_current_track_info(self):
        """Retourne les informations (métadonnées) de la piste actuelle."""
        if 0 <= self.current_track_index < len(self.playlist):
            return self.playlist[self.current_track_index]
        return None

    def get_volume(self):
        """Retourne le volume actuel (0-100)."""
        return get_volume_percent(self._media_player)

    def set_volume(self, volume_percent):
        """Définit le volume (0-100)."""
        set_volume_percent(self._media_player, volume_percent)

    def update(self):
        """
        Vérifie si la musique actuelle est terminée et passe à la suivante si nécessaire.
        Cette méthode est appelée périodiquement par l'interface graphique.
        Affiche également le temps actuel en console.
        """
        if not self.is_playing and not self.is_paused:
            return False

        current_pos_abs_ms = self.get_current_time_ms()
        total_duration_ms = self.get_current_track_duration_ms()

        # Affichage du temps en console
        current_time_formatted = format_time(current_pos_abs_ms)
        total_time_formatted = format_time(total_duration_ms)
        # Utilise '\r' pour surécrire la ligne actuelle et '\n' pour un nouveau message
        print(f"Temps actuel: {current_time_formatted} / {total_time_formatted}", end='\r')

        if is_track_ended(self._media_player):
            print("\nMusique terminée, passage à la suivante...")
            self.play_next_music()
            return True

        return False

    def quit(self):
        """Arrête le lecteur VLC et libère les ressources."""
        stop_current_music(self._media_player)
        quit_vlc_player(self._vlc_instance, self._media_player)
