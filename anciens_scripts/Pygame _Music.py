import pygame
import os
import time

pygame.mixer.init()

music_file = os.path.abspath("More Plastic - Rewind [NCS Release].mp3").replace("\\", "/")
current_position = 0  # Variable pour stocker la position actuelle (en secondes)
is_paused = False     # Variable pour suivre l'état de la pause

try:
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play()
    print("La musique a commencé. Appuie sur 'p' pour mettre en pause/reprendre, 'q' pour quitter.")

    while pygame.mixer.music.get_busy() or is_paused:
        user_input = input()
        if user_input.lower() == 'p':
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                current_position = pygame.mixer.music.get_pos() / 1000.0
                is_paused = True
                print(f"Musique en pause à {current_position:.2f} secondes.")
            elif is_paused:
                pygame.mixer.music.unpause()
                print(f"Musique reprise à {current_position:.2f} secondes.")
                is_paused = False
            else:
                print("Aucune musique en cours de lecture.")
        elif user_input.lower() == 'q':
            pygame.mixer.music.stop()
            print("Lecture stoppée.")
            break
        time.sleep(0.1)

except pygame.error as e:
    print(f"Erreur de lecture avec pygame : {e}")
finally:
    pygame.mixer.quit()