import pygame
import customtkinter as ctk

from scripts.start_up.instructions import InstructionsDisplay
from scripts.start_up.presentation import show_presentation_screen
from scripts.start_up.search_musics import MusicFinder
from scripts.gui.music_app_gui import MusicAppGUI

pygame.init()

if __name__ == "__main__":
    # Afficher les instructions
    instructions_manager = InstructionsDisplay("Zoléni") # Utilise ton nom ou NOM
    instructions_manager.display_instructions()

    # Afficher l'écran de présentation (ajuste les chemins d'image et de police)
    # Les chemins sont relatifs à la racine du projet
    show_presentation_screen(
        image_path='assets/images/Zoléni_Cyberpunk.jpg', # Exemple de chemin depuis la racine du projet
        font_path_name='assets/fonts/MINDCONTROL.ttf',
        font_path_project='assets/fonts/MINDCONTROL.ttf', # Exemple
        project_name="Mon Lecteur Musical",
        duration_ms=3000
    )

    # Recherche des musiques
    music_finder = MusicFinder()
    found_musics = music_finder.find_music_files()

    if found_musics:
        root = ctk.CTk()
        app = MusicAppGUI(root, found_musics)
        root.mainloop()
    else:
        print("Aucune musique trouvée, le lecteur ne peut pas démarrer.")
        pygame.quit() # S'assurer que Pygame est bien fermé si pas de GUI