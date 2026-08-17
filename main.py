import os
import sys

import customtkinter as ctk

# PyInstaller (mode --windowed) : sans console attachée, stdout/stderr peuvent
# être None, ce qui ferait planter le moindre print(). On les neutralise ici.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from src.search_musics import MusicFinder
from src.gui.music_app_gui import MusicAppGUI

if __name__ == "__main__":
    try:
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
    except KeyboardInterrupt:
        print("CTRL + C : Programme interrompu par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"Une erreur est survenue : {e}")