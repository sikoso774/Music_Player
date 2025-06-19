# scripts/start_up/instructions.py
# Les instructions du programme.

# Constantes pour le copyright et l'auteur
NOM = "Zoléni KOKOLO ZASSI"
ANNEE = 2025

# Texte des instructions avec des placeholders
INSTRUCTIONS_TEXT = """
Bienvenue dans mon lecteur musical !

Ce lecteur permet de lire des fichiers audio au format MP3, WAV, OGG, et FLAC.

Fonctionnement :
1. Les musiques seront automatiquement recherchées dans un dossier "Musiques"
   situé au même endroit que le programme, ou si ce dossier est vide,
   dans le répertoire de l'utilisateur (dossier Musique par défaut).
2. L'interface graphique s'ouvrira et vous permettra de contrôler la lecture.

Contrôles :
- 'Play/Pause' : Lancer ou mettre en pause la musique.
- 'Précédent' : Revenir à la musique précédente.
- 'Suivant' : Passer à la musique suivante.
- 'Quitter' : Fermer l'application.

Profitez de votre musique !
Développé par {author_name} ({author_nickname})
"""

class InstructionsDisplay:
    def __init__(self, user_name="Utilisateur"):
        # Utilise les constantes NOM et ANNEE définies dans ce même fichier
        self.instructions_message = INSTRUCTIONS_TEXT.format(author_name=user_name, author_nickname=NOM)

    def display_instructions(self):
        """Affiche les instructions formatées dans le terminal."""
        print(self.instructions_message)
        print("-" * 50) # Ligne de séparation