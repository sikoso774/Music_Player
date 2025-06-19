# scripts/player/pygame_setup.py
import pygame
import os

def initialize_pygame_mixer():
    """
    Initialise Pygame et son module mixer.
    Crée une fenêtre Pygame minimale et la cache.
    """
    pygame.mixer.init()
    # Positionne la fenêtre hors écran pour qu'elle ne soit pas visible
    os.environ['SDL_VIDEO_WINDOW_POS'] = "-1000,-1000"
    os.environ['SDL_VIDEO_CENTERED'] = "0"
    screen = pygame.display.set_mode((1, 1), pygame.NOFRAME)
    try:
        pygame.display.iconify() # Tente de minimiser la fenêtre
    except pygame.error:
        pass # Ignore l'erreur si elle ne peut pas être iconifiée
    print("Pygame et Pygame.mixer initialisés.")
    return screen

def quit_pygame_mixer():
    """
    Arrête le mixeur Pygame et quitte Pygame.
    """
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    pygame.quit()
    print("Nettoyage Pygame terminé.")