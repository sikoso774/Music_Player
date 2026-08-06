# src/player/vlc_setup.py

class VlcNotAvailableError(Exception):
    """Levée quand VLC/libVLC est introuvable ou ne peut pas être initialisé."""
    pass

def create_vlc_player():
    """
    Crée une nouvelle instance VLC et son lecteur média associé.
    L'import de `vlc` est fait ici (et non au niveau module) pour que l'échec
    de chargement de libVLC survienne à un point contrôlé, après que la
    fenêtre principale existe déjà et puisse afficher un message d'erreur.
    """
    try:
        import vlc
    except Exception as e:
        raise VlcNotAvailableError(
            "Impossible de charger la bibliothèque VLC (libVLC introuvable)."
        ) from e

    try:
        instance = vlc.Instance()
        if instance is None:
            raise VlcNotAvailableError("VLC n'a pas pu être initialisé (instance nulle).")
        media_player = instance.media_player_new()
    except VlcNotAvailableError:
        raise
    except Exception as e:
        raise VlcNotAvailableError(
            "Impossible d'initialiser VLC (instance ou lecteur média)."
        ) from e

    print("VLC initialisé.")
    return instance, media_player

def quit_vlc_player(instance, media_player):
    """Arrête et libère les ressources VLC données."""
    media_player.stop()
    media_player.release()
    instance.release()
    print("Nettoyage VLC terminé.")
