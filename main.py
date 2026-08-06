import customtkinter as ctk

from src.search_musics import MusicFinder
from src.gui.music_app_gui import MusicAppGUI

if __name__ == "__main__":
    # Recherche des musiques
    music_finder = MusicFinder()
    found_musics = music_finder.find_music_files()

    if found_musics:
        root = ctk.CTk()
        app = MusicAppGUI(root, found_musics)
        if not getattr(app, "startup_failed", False):
            root.mainloop()
    else:
        print("Aucune musique trouvée, le lecteur ne peut pas démarrer.")