# src/resource_path.py
# Résout le chemin d'une ressource embarquée (assets), que l'app tourne
# depuis les sources ou depuis un exécutable PyInstaller.

import os
import sys

def resource_path(relative_path):
    """
    Retourne le chemin absolu vers une ressource (ex: "assets/icon/zkz_icon.ico").

    En développement, le chemin est résolu depuis la racine du projet.
    Une fois empaqueté avec PyInstaller, les fichiers de données sont extraits
    dans un dossier temporaire exposé via sys._MEIPASS (aussi bien en mode
    --onefile qu'en mode --onedir) ; on l'utilise comme base dans ce cas.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_path = getattr(sys, '_MEIPASS', project_root)
    return os.path.join(base_path, relative_path)
