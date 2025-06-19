# scripts/player/music_player_class.py
import pygame
from .audio_info import prepare_playlist_with_durations, get_audio_info
from .pygame_setup import initialize_pygame_mixer, quit_pygame_mixer
# Importe la fonction renommée ici
from .player_logic import load_and_play, pause_pygame_music, unpause_pygame_music, stop_current_music, \
    get_pygame_playback_time_ms
import os


class MusicPlayer:
    """
    Gère la lecture, la pause, la reprise et le changement de musiques
    en utilisant Pygame.mixer et en maintenant un état précis.
    """

    def __init__(self, playlist):
        self.screen = initialize_pygame_mixer()  # Initialise Pygame et le mixeur
        self.playlist = prepare_playlist_with_durations(playlist)

        self.current_track_index = 0
        self.is_paused = False  # Indique si le lecteur est en état de pause
        self.is_playing = False  # Indique si une musique est chargée et potentiellement en lecture/pause
        # Nouvelle variable pour la position de départ réelle
        self._start_position_ms_on_play = 0

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

        # Stocke la position de départ réelle
        self._start_position_ms_on_play = start_pos_ms

        # Passe la position en secondes à load_and_play
        if load_and_play(track_path, start_pos_ms / 1000.0):
            self.is_playing = True
            self.is_paused = False  # La musique est en lecture, pas en pause
        else:
            self.is_playing = False  # Échec du chargement/lecture
            self.is_paused = False

    def toggle_pause(self):
        """
        Bascule l'état de pause/lecture de la musique.
        Gère les variables d'état internes et appelle les fonctions Pygame appropriées.
        """
        if not self.is_playing:
            if self.playlist:
                self.load_and_play_music(self.current_track_index)
            return

        if self.is_paused:
            unpause_pygame_music()
            self.is_paused = False
        else:
            pause_pygame_music()
            self.is_paused = True

    def play_next_music(self):
        """Passe à la musique suivante dans la playlist."""
        print("Passage à la musique suivante.")
        if not self.playlist:
            return

        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        # Réinitialise la position de départ pour le nouveau morceau
        self._start_position_ms_on_play = 0
        self.load_and_play_music(self.current_track_index)

    def play_previous_music(self):
        """Revient à la musique précédente dans la playlist."""
        print("Passage à la musique précédente.")
        if not self.playlist:
            return

        self.current_track_index = (self.current_track_index - 1 + len(self.playlist)) % len(self.playlist)
        # Réinitialise la position de départ pour le nouveau morceau
        self._start_position_ms_on_play = 0
        self.load_and_play_music(self.current_track_index)

    def seek_music(self, position_ms):
        """
        Déplace la lecture à une position spécifique en millisecondes.
        Si la musique n'est pas en lecture, elle la charge et la lance à cette position.
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

        # La position de départ est maintenant new_position_ms
        self.load_and_play_music(track_index=self.current_track_index, start_pos_ms=new_position_ms)

    def get_current_time_ms(self):
        """
        Retourne le temps de lecture actuel en millisecondes, en tenant compte
        de la position de départ réelle.
        """
        if self.is_playing and not self.is_paused:
            # Temps écoulé depuis le dernier play() par Pygame
            pygame_pos = get_pygame_playback_time_ms()
            # Temps total = position de départ + temps écoulé depuis le dernier play()
            return self._start_position_ms_on_play + pygame_pos
        elif self.is_playing and self.is_paused:
            # Si en pause, la position est la dernière position connue
            # (get_pygame_playback_time_ms() donnera la position au moment de la pause + _start_position_ms_on_play)
            return self._start_position_ms_on_play + get_pygame_playback_time_ms()
        else:
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

    def format_time(self, ms):
        """
        Convertit les millisecondes en format de temps MM:SS.
        """
        total_seconds = int(ms / 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

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
        current_time_formatted = self.format_time(current_pos_abs_ms)
        total_time_formatted = self.format_time(total_duration_ms)
        # Utilise '\r' pour surécrire la ligne actuelle et '\n' pour un nouveau message
        print(f"Temps actuel: {current_time_formatted} / {total_time_formatted}", end='\r')

        if total_duration_ms > 0 and current_pos_abs_ms >= total_duration_ms - 50:  # 50ms de marge
            print("\nMusique terminée détectée par temps, passage à la suivante...")
            self.play_next_music()
            return True

        return False

    def quit(self):
        """Arrête le mixeur Pygame et libère les ressources."""
        stop_current_music()
        quit_pygame_mixer()