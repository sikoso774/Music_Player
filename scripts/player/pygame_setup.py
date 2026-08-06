# scripts/player/pygame_setup.py
import pygame

def initialize_pygame_mixer():
    """
    Initialise le module mixer de Pygame.
    Le mixer est indépendant du module display : aucune fenêtre n'est nécessaire.
    """
    pygame.mixer.init()
    print("Pygame.mixer initialisé.")

def quit_pygame_mixer():
    """
    Arrête le mixeur Pygame et quitte Pygame.
    """
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    pygame.quit()
    print("Nettoyage Pygame terminé.")