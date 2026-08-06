# scripts/gui/gui_logic.py
from scripts.time_format import format_time

def calculate_seek_position(event_x, progress_bar_widget, total_duration_ms):
    """
    Calcule la nouvelle position de la musique basée sur la position du clic/glissement
    sur la barre de progression.
    """
    if total_duration_ms == 0:
        return 0 # Retourne 0 si la durée est inconnue pour éviter une division par zéro

    # Calcule la position relative du clic sur la barre (de 0 à 1)
    # event.x est la position X du clic par rapport au widget
    # progress_bar_widget.winfo_width() est la largeur totale du widget
    bar_width = progress_bar_widget.winfo_width()
    if bar_width == 0: # Éviter une division par zéro si le widget n'est pas encore rendu
        return 0

    relative_position = event_x / bar_width

    # S'assurer que la position est entre 0 et 1
    relative_position = max(0.0, min(1.0, relative_position))

    # Calcule la nouvelle position en millisecondes
    new_position_ms = int(total_duration_ms * relative_position)
    return new_position_ms