# Mon lecteur de musique
# Zoléni KOKOLO ZASSI

# Importation de os pour explorer les fichiers
import os 
from scripts.instructions import INSTRUCTIONS, ANNEE, NOM

# Les constantes.
MUSICS_ABS = []

# Afficher les consignes
class Consignes:
    """ Affiche les consignes du lecteur de musique"""

    def __init__(self):
        self.instructions = INSTRUCTIONS.format(nom= input("Mettez votre nom: "),author= NOM)

    def afficher_consignes(self):
        print("Consignes : \n")
        for instruction in self.instructions.split(", "):
            print(instruction)
            print("-"*100)
        print("Ce projet est la propriété de : {nom}, fait en {année} ;)\n".format(nom=NOM, année =ANNEE))
        print("-"*100)


class Musiques:
    """ Cette classe est faite pour  trouver les musiques automatiqument """

    def __init__(self):
        self.MUSICS = None
        self.musics_all = None

    def find_musiques(self):
        """ Cette fonction va sur l'explorateur de fichiers afin de 
        trouver les musiques sans souci"""

        user_path = os.environ.get("USERPROFILE")

        if user_path:
            musics_path = os.path.join(user_path, "Music")

            if os.path.exists(musics_path):
                musics          = os.listdir(musics_path)
                self.musics_all = os.path.join(musics_path, musics[1])
                self.MUSICS     = os.listdir(self.musics_all)
            
            else: 
                print(f"Le dossier Musique n'a pas été trouvé à l'emplacement attendu : {musics_path}")
        else:
            print("Rien n'a fonctionné...")

        for musique in self.MUSICS:
            musique = os.path.join(self.musics_all, musique)
            musique = os.path.abspath(musique)
            musique = musique.replace("\\","/")
            MUSICS_ABS.append(musique)

        return MUSICS_ABS


#if __name__ == "__main__":

    #print(f"Les Instructions:\n")
    #MUSICS_ABS = find_musiques()
    #print(MUSICS_ABS[-2])
    #playsound3.playsound(f"{MUSICS_ABS[-2]}")