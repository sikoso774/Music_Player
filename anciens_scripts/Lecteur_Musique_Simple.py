from playsound3 import playsound
import sys

PISTE_AUDIO = "More Plastic - Rewind [NCS Release].mp3"
CONSIGNES = "Chargement de la musique..., Veuillez patienter quelques instants., Lecture de la musique..., [...]"
NOM = "Zoléni Kokolo Zassi"
ANNEE = 2025

def charger_musique(piste_audio=PISTE_AUDIO):
     """Charge une musique à partir d'un fichier audio."""
     print(f"\nPiste audio: \n{piste_audio}")
     # Simuler le chargement de la musique
     playsound(piste_audio)

# Afficher les consignes
print("Consignes :")
for consigne in CONSIGNES.split(", "):
     print(consigne)


# Présentation
print("Welcome to my music player!")
print("{nom_complet}\n{année}".format(nom_complet=NOM, année=str(ANNEE)))

ucl = charger_musique()
print("Merci ! ")
sys.exit()
