# src/player/vlc_setup.py
import vlc

def create_vlc_player():
    """Crée une nouvelle instance VLC et son lecteur média associé."""
    instance = vlc.Instance()
    media_player = instance.media_player_new()
    print("VLC initialisé.")
    return instance, media_player

def quit_vlc_player(instance, media_player):
    """Arrête et libère les ressources VLC données."""
    media_player.stop()
    media_player.release()
    instance.release()
    print("Nettoyage VLC terminé.")
