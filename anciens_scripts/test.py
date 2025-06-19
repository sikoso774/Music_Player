# Mon lecteur de musique
# Zoléni KOKOLO ZASSI

# Imporatations de bibliothèques

import playsound3
import os
from random import randint
from Shearch_musics import Consignes, Musiques

MUSICS_ABS = None
music_file = None
CHOICES    = ["0", "-1","All musics", "Aléa"]


# Le programme :

if __name__ == "__main__":
    rules = Consignes()
    rules.afficher_consignes()
    MUSICS_ABS = Musiques()
    MUSICS_ABS = MUSICS_ABS.find_musiques()
    choix = input("Choose beetween 0, -1, All musics and Aléa : ")

    try:
        while choix not in CHOICES:
            print("Vous avez échoué !\n")
            print("-"*170)
            if not choix == "help":
                choix = input("Relisez la consigne...: ")
            else:
                print(f"Voici la liste des choix que vous pouvez faire : \n{CHOICES}\n")
                print(f"Toutes les musiques : ")
                for music in MUSICS_ABS:
                    print(f"{os.path.relpath(music)}")

                choix = input("\n Réeassayez...: ")

        if choix == "0":
            music_file = MUSICS_ABS[0]
            print(f"Musique choisie: {os.path.relpath(music_file)}")
            playsound3.playsound(music_file)

        elif choix == "-1":
            music_file = MUSICS_ABS[-1]
            print(f"Musique choisie: {os.path.relpath(music_file)}")
            playsound3.playsound(music_file)

        elif choix == "all musics".capitalize():
            print("\n<< All musics >>\n")
            try:
                for i in range(7):
                    music_file = MUSICS_ABS[i]
                    print(f"\nMusique {i+1}: {os.path.relpath(music_file)}")
                    playsound3.playsound(music_file)
            except:
                print("Echec")

        elif choix == "Aléa":
            print("\n<< Musique Aléatoire ... >>\n")
            music_file = MUSICS_ABS[randint(-3, -1)]
            print(f"Musique choisie aléatoirement: {os.path.relpath(music_file)}")
            playsound3.playsound(music_file)

    except:
        print("Echec du programme. Il y a eu une erreur quelque part...")
    finally:
        print("Merci ! ")

print("Copyright: {}".format("Zoléni KOKOLO ZASSI"))
quit()