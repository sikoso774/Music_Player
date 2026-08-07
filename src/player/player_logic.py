# src/player/player_logic.py

import os
import time

# --- Fonctions d'action de VLC ---
# Toutes prennent le lecteur (et l'instance, si besoin de créer un média) en
# paramètre explicite plutôt que de dépendre d'un état global.

def _wait_until_playing(media_player, timeout_s=2.0):
    """
    Attend que VLC ait effectivement démarré la lecture, pour qu'un set_time()
    juste après play() prenne bien effet (play() est asynchrone côté VLC).
    """
    import vlc
    deadline = time.monotonic() + timeout_s
    while media_player.get_state() not in (vlc.State.Playing, vlc.State.Error, vlc.State.Ended):
        if time.monotonic() > deadline:
            break
        time.sleep(0.01)

def load_and_play(instance, media_player, track_path, start_pos_ms=0):
    """
    Charge et lance la lecture d'un morceau avec VLC.
    """
    try:
        media = instance.media_new(track_path)
        media_player.set_media(media)
        media_player.play()
        if start_pos_ms > 0:
            _wait_until_playing(media_player)
            media_player.set_time(start_pos_ms)
        # Message pour le changement de musique/lecture
        print(f"\nLecture de : {os.path.basename(track_path)} depuis {start_pos_ms / 1000:.2f}s")
        return True
    except Exception as e:
        print(f"Erreur VLC lors du chargement ou de la lecture de '{os.path.basename(track_path)}': {e}")
        print("Assure-toi que le fichier est un format supporté et non corrompu.")
        return False

def pause_music(media_player):
    """Met la musique VLC en pause."""
    media_player.set_pause(1)
    print(f"Musique mise en pause à: {max(0, media_player.get_time()) / 1000:.2f}s")

def unpause_music(media_player):
    """Reprend la musique VLC."""
    media_player.set_pause(0)
    print(f"Musique reprise de: {max(0, media_player.get_time()) / 1000:.2f}s")

def stop_current_music(media_player):
    """Arrête la lecture de la musique VLC."""
    media_player.stop()
    print("Lecture stoppée.")

def seek_to(media_player, position_ms):
    """Déplace directement la tête de lecture à une position donnée, sans recharger le fichier."""
    media_player.set_time(position_ms)

def is_track_ended(media_player):
    """Indique si VLC a atteint la fin du morceau en cours de lecture."""
    import vlc
    return media_player.get_state() == vlc.State.Ended

def get_volume_percent(media_player):
    """Retourne le volume actuel (0-100)."""
    return media_player.audio_get_volume()

def set_volume_percent(media_player, volume_percent):
    """Définit le volume (0-100)."""
    media_player.audio_set_volume(int(volume_percent))

# --- Fonctions d'information sur le statut ---

def get_playback_time_ms(media_player):
    """
    Retourne la position de lecture actuelle en millisecondes.
    Renvoie 0 si rien n'est chargé/en cours.
    """
    return max(0, media_player.get_time())
