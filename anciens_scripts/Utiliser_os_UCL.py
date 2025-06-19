import os
import playsound3

# Récupérer le chemin du dossier utilisateur
chemin_utilisateur = os.environ.get("USERPROFILE")  # Pour Windows
# chemin_utilisateur = os.path.expanduser("~")  # Pour Linux/Mac
print(chemin_utilisateur)

if chemin_utilisateur:
    # Construire le chemin vers le dossier Musique (le nom exact peut varier)
    chemin_musique = os.path.join(chemin_utilisateur, "Music")  # Ou "Musique", selon la langue

    # Vérifier si le dossier existe
    if os.path.exists(chemin_musique):
        print(f"Le chemin vers le dossier Musique est : {chemin_musique}")
        # Maintenant, tu peux utiliser les fonctions de 'os' pour explorer ce dossier
        # Par exemple, lister les fichiers et dossiers à l'intérieur :
        contenu = os.listdir(chemin_musique)
        print(f"Contenu du dossier Musique : {contenu}")
        musiques = os.path.join(chemin_musique, contenu[1])
        print(musiques)
        uci_anthem = os.path.join(musiques, "UEFA Champions League Anthem (Full Version).mp3")
        print(uci_anthem)
        uci_anthem_avec_slash = uci_anthem.replace("\\", "/")
        print(f"Lancement de la musique : {uci_anthem_avec_slash}")
        # Joue le fichier audio
        playsound3.playsound(uci_anthem_avec_slash)
        
    else:
        print(f"Le dossier Musique n'a pas été trouvé à l'emplacement attendu : {chemin_musique}")
else:
    print("Impossible de déterminer le chemin du dossier utilisateur.")