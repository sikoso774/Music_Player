# scripts/player/player_logic.py

import os

import pygame

# --- Fonctions d'action de Pygame ---

def load_and_play(track_path, start_pos_s=0.0):
    """
    Charge et lance la lecture d'un morceau avec Pygame.mixer.music.
    """
    try:
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play(start=start_pos_s)
        # Message pour le changement de musique/lecture
        print(f"\nLecture de : {os.path.basename(track_path)} depuis {start_pos_s:.2f}s")
        return True
    except pygame.error as e:
        print(f"Erreur Pygame lors du chargement ou de la lecture de '{os.path.basename(track_path)}': {e}")
        print("Assure-toi que le fichier est un format supporté et non corrompu.")
        return False

def pause_pygame_music():
    """
    Met la musique Pygame en pause.
    Ne fait rien si la musique n'est pas en cours de lecture.
    """
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        # Message pour la pause
        print(f"Musique mise en pause à: {max(0, pygame.mixer.music.get_pos()) / 1000:.2f}s")

def unpause_pygame_music():
    """
    Reprend la musique Pygame.
    """
    pygame.mixer.music.unpause()
    # Message pour la reprise
    print(f"Musique reprise de: {max(0, pygame.mixer.music.get_pos()) / 1000:.2f}s")

def stop_current_music():
    """
    Arrête la lecture de la musique Pygame.
    """
    pygame.mixer.music.stop()
    # Message pour l'arrêt
    print("Lecture stoppée.")

# --- Fonctions d'information sur le statut ---

def get_pygame_playback_time_ms():
    """
    Retourne le temps de lecture actuel en millisecondes depuis le dernier appel à play()
    directement depuis Pygame. Renvoie 0 si rien n'est en lecture.
    """
    # get_pos() renvoie -1 si rien ne joue. On veut 0 dans ce cas.
    return max(0, pygame.mixer.music.get_pos())