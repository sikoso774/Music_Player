# scripts/start_up/presentation.py
# Gère l'écran de présentation au démarrage.

import pygame
import os
# Importe NOM depuis le fichier où il est défini (maintenant dans start_up/instructions)
from .instructions import NOM


def show_presentation_screen(image_path, font_path_name, font_path_project,
                             project_name="Mon Lecteur Musical", duration_ms=3000):
    """
    Affiche un écran de présentation avec une image et des textes,
    et gère le fondu.

    Args:
        image_path (str): Le chemin de l'image de présentation (ta PP).
        font_path_name (str): Le chemin de la police pour le nom de l'auteur.
        font_path_project (str): Le chemin de la police pour le nom du projet.
        project_name (str): Le nom du projet (par défaut "Mon Lecteur Musical").
        duration_ms (int): La durée totale de l'écran de présentation en millisecondes.
    """
    # Utilise l'écran Pygame déjà initialisé ou en crée un temporaire si nécessaire
    try:
        screen = pygame.display.get_surface()
        if screen is None:
            print("Aucun écran Pygame trouvé, en créant un temporaire pour la présentation.")
            screen = pygame.display.set_mode((800, 600), pygame.HIDDEN) # Utilise HIDDEN pour ne pas afficher la fenêtre
            pygame.display.set_caption(project_name)
    except pygame.error:
        print("Erreur Pygame lors de la récupération/création de l'écran pour la présentation.")
        return

    pygame.display.set_mode((800, 600)) # Définit la taille visible après la présentation
    pygame.display.set_caption(project_name)

    white = (255, 255, 255)
    black = (0, 0, 0)

    screen_width, screen_height = screen.get_size()

    # --- Chargement de l'image ---
    try:
        # Chemin relatif : depuis scripts/start_up/ presentation.py vers le dossier racine du projet
        base_path = os.path.dirname(os.path.abspath(__file__))
        # Remonte deux niveaux pour aller de scripts/start_up à Music_Player_V2
        image_full_path = os.path.join(base_path, '..', '..', image_path)

        image = pygame.image.load(image_full_path).convert_alpha()

        target_width = screen_width // 2
        target_height = screen_height // 2
        image = pygame.transform.scale(image, (target_width, target_height))
        image_rect = image.get_rect(center=(screen_width // 2, screen_height // 2))

    except pygame.error as e:
        print(f"Erreur de chargement de l'image de présentation ({image_full_path}): {e}")
        return

    # --- Chargement des polices ---
    try:
        font_path_name_full = os.path.join(base_path, '..', '..', font_path_name)
        font_path_project_full = os.path.join(base_path, '..', '..', font_path_project)

        font_name = pygame.font.Font(font_path_name_full, 36)
        font_project = pygame.font.Font(font_path_project_full, 36)
    except Exception as e:
        print(f"Erreur de chargement des polices de présentation : {e}")
        font_name = pygame.font.SysFont("Arial", 36)
        font_project = pygame.font.SysFont("Arial", 36)

    text_author_name = font_name.render(NOM, True, white)
    text_author_name_rect = text_author_name.get_rect(center=(screen_width // 2, image_rect.bottom + 30))

    text_project_name = font_project.render(project_name, True, white)
    text_project_name_rect = text_project_name.get_rect(center=(screen_width // 2, text_author_name_rect.bottom + 30))

    start_time = pygame.time.get_ticks()

    alpha_image = 0
    alpha_text_author_name = 0
    alpha_text_project_name = 0

    fade_in_duration = duration_ms * 0.3
    hold_duration = duration_ms * 0.4
    fade_out_duration = duration_ms * 0.3

    clock = pygame.time.Clock()

    running_presentation = True
    while running_presentation and (pygame.time.get_ticks() - start_time < duration_ms):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_presentation = False # Permet de sortir proprement de la boucle
                pygame.quit()
                exit() # Termine l'application

        screen.fill(black)

        elapsed_time = pygame.time.get_ticks() - start_time

        if elapsed_time < fade_in_duration:
            alpha_val = int(255 * (elapsed_time / fade_in_duration))
        elif elapsed_time < fade_in_duration + hold_duration:
            alpha_val = 255
        else:
            alpha_val = int(255 * (1 - (elapsed_time - (fade_in_duration + hold_duration)) / fade_out_duration))
            if alpha_val < 0: # S'assurer que l'alpha ne descend pas en dessous de 0
                alpha_val = 0

        image.set_alpha(alpha_val)
        text_author_name.set_alpha(alpha_val)
        text_project_name.set_alpha(alpha_val)

        screen.blit(image, image_rect)
        screen.blit(text_author_name, text_author_name_rect)
        screen.blit(text_project_name, text_project_name_rect)

        pygame.display.flip()
        clock.tick(60)

    # Ferme complètement l'affichage Pygame : la suite de l'app est pilotée par
    # CustomTkinter et n'a plus besoin d'une fenêtre Pygame. Le module mixer
    # (audio) est indépendant et continue de fonctionner normalement.
    pygame.display.quit()