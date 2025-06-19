import pygame
import tkinter as tk
import PySide6

from scripts.start_up.instructions import InstructionsDisplay, NOM, ANNEE
from scripts.start_up.presentation import show_presentation_screen
from scripts.start_up.shearch_musics import MusicFinder
from scripts.gui.music_app_gui_class import MusicAppGUI

# ...
# Initialisation de Pygame au début de main.py si tu as une présentation Pygame
pygame.init()
pygame.mixer.init()
# ...

if __name__ == "__main__":
    # Afficher les instructions
    instructions_manager = InstructionsDisplay("Zoléni") # Utilise ton nom ou NOM
    instructions_manager.display_instructions()

    # Afficher l'écran de présentation (ajuste les chemins d'image et de police)
    # Les chemins sont maintenant relatifs à Music_Player_V2/
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
        root = tk.Tk()
        app = MusicAppGUI(root, found_musics)
        root.mainloop()
    else:
        print("Aucune musique trouvée, le lecteur ne peut pas démarrer.")
        pygame.quit() # S'assurer que Pygame est bien fermé si pas de GUI