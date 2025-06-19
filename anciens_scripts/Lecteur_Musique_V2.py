# Mon lecteur de musique
# Zoléni KOKOLO ZASSI

# Imporatations de bibliothèques

import playsound3
import os
from anciens_scripts.Shearch_musics import Consignes, Musiques
                                                                                                              
MUSICS_ABS = None
music_file = None

if __name__ == "__main__":
    règles = Consignes()
    règles.afficher_consignes()
    MUSICS_ABS = Musiques()
    MUSICS_ABS = MUSICS_ABS.find_musiques()
    choix = input("Choose the  numbers  0 or -1: ")
    if choix == "0":
        music_file = MUSICS_ABS[0]
        print(f"Musique choisie : {os.path.relpath(MUSICS_ABS[0])}")
        playsound3.playsound(music_file)

    elif choix == "-1":
        music_file = MUSICS_ABS[-1]
        playsound3.playsound(music_file)

    else:
        print("Echec...")