# Création de la classe MusicAppGUI
import tkinter as tk
import os
import pygame

# Importe les classes et fonctions refactorisées
from scripts.player.music_player_class import MusicPlayer
from scripts.gui.gui_elements import (
    create_main_window, create_track_label, create_time_frame, create_time_labels,
    create_progress_bar, create_control_buttons_frame, create_control_buttons,
    create_volume_slider, create_copyright_label,
    create_playlist_frame, create_playlist_listbox,
    create_album_label,create_artist_label
)
# Utilise la fonction format_time de gui_logic.py pour l'affichage GUI
from scripts.gui.gui_logic import format_time, calculate_seek_position
from scripts.start_up.instructions import NOM, ANNEE # Importe les constantes pour le copyright


class MusicAppGUI:
    def __init__(self, master, found_musics):
        self.master = master
        create_main_window(master)

        self.player = MusicPlayer(found_musics)

        if not self.player.playlist:
            print("Erreur: La playlist est vide. L'application GUI ne démarrera pas correctement.")
            master.destroy()
            return

        self.current_track_name = tk.StringVar(value="Aucune musique chargée")
        self.current_time_str = tk.StringVar(value="00:00")
        self.total_time_str = tk.StringVar(value="00:00")
        self.current_artist_name = tk.StringVar(value="Artiste inconnu")
        self.current_album_name = tk.StringVar(value="Album inconnu")
        self.update_interval = 100

        # --- Widgets de l'interface ---
        self.track_label = create_track_label(master, self.current_track_name)
        self.artist_label = create_artist_label(master, self.current_artist_name)
        self.album_label = create_album_label(master, self.current_album_name)

        time_frame = create_time_frame(master)
        self.time_label, self.total_time_label = create_time_labels(
            time_frame, self.current_time_str, self.total_time_str
        )
        self.progress_bar = create_progress_bar(time_frame)
        self.progress_bar.bind("<Button-1>", self.on_progress_bar_click)
        self.progress_bar.bind("<B1-Motion>", self.on_progress_bar_drag)

        control_frame = create_control_buttons_frame(master)
        self.prev_button, self.play_pause_button, self.next_button = create_control_buttons(
            control_frame, self.play_previous, self.toggle_play_pause, self.play_next
        )

        self.volume_slider = create_volume_slider(master, self.set_volume,
                                                  initial_volume=int(pygame.mixer.music.get_volume() * 100))

        playlist_frame = create_playlist_frame(master)
        self.playlist_listbox = create_playlist_listbox(playlist_frame, self.on_playlist_select)
        self._populate_playlist_listbox()

        self.copyright_label = create_copyright_label(master, "", NOM, ANNEE)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Démarrer la lecture de la première musique
        if self.player.playlist:
            self.player.load_and_play_music(0)
            self._update_ui_for_new_track()
            self._highlight_current_track()
            # Démarrer la boucle de mise à jour de l'UI
            self.master.after(self.update_interval, self.update_player_status)
        else:
            self.current_track_name.set("Aucune musique trouvée. Veuillez relancer.")


    def _populate_playlist_listbox(self):
        """Remplit la Listbox avec les noms des morceaux de la playlist."""
        self.playlist_listbox.delete(0, tk.END) # Efface le contenu existant
        for index, track_info in enumerate(self.player.playlist):
            track_name = os.path.basename(track_info['path'])
            self.playlist_listbox.insert(tk.END, f"{index + 1}. {track_name}")

    def on_playlist_select(self, event):
        """Gère la sélection d'un morceau dans la Listbox (double-clic)."""
        selected_indices = self.playlist_listbox.curselection()
        if selected_indices:
            selected_index = selected_indices[0] # Récupère l'index de l'élément sélectionné
            print(f"Morceau sélectionné dans la liste : {selected_index}")
            self.player.load_and_play_music(selected_index)
            self._update_ui_for_new_track()
            self._highlight_current_track() # Met en surbrillance le morceau nouvellement joué

    def _highlight_current_track(self):
        """Met en surbrillance le morceau actuellement joué dans la Listbox."""
        self.playlist_listbox.selection_clear(0, tk.END) # Efface toute sélection précédente
        if 0 <= self.player.current_track_index < len(self.player.playlist):
            self.playlist_listbox.selection_set(self.player.current_track_index)
            self.playlist_listbox.activate(self.player.current_track_index)
            self.playlist_listbox.see(self.player.current_track_index) # S'assure que le morceau est visible

    def on_progress_bar_click(self, event):
        """Gère le clic initial sur la barre de progression."""
        self._set_music_position_from_progressbar(event.x)

    def on_progress_bar_drag(self, event):
        """Gère le glissement (drag) sur la barre de progression."""
        self._set_music_position_from_progressbar(event.x)

    def _set_music_position_from_progressbar(self, click_x):
        """
        Calcule la nouvelle position de la musique basée sur la position du clic/glissement
        sur la barre de progression et appelle la fonction seek.
        """
        total_duration_ms = self.player.get_current_track_duration_ms()
        new_position_ms = calculate_seek_position(click_x, self.progress_bar, total_duration_ms)

        if total_duration_ms == 0:
            return

        # Met à jour l'affichage du temps immédiatement pour un retour visuel
        self.current_time_str.set(format_time(new_position_ms))
        self.progress_bar["value"] = new_position_ms

        # Demande au MusicPlayer de se positionner
        self.player.seek_music(new_position_ms)

        # Force le bouton Play/Pause à afficher "Pause" si le seek a démarré la lecture
        if self.player.is_playing:
            self.play_pause_button.config(text="⏯️ Pause")
        else:
            self.play_pause_button.config(text="▶️ Play")

    def _update_ui_for_new_track(self):
        """Met à jour tous les éléments de l'UI liés au morceau actuel."""
        if self.player.playlist and 0 <= self.player.current_track_index < len(self.player.playlist):
            track_info = self.player.playlist[self.player.current_track_index]
            metadata = track_info.get('metadata', {})
            duration_ms = track_info.get('duration_ms', 0)

            # Mise à jour des labels de texte
            # Si le titre est "Titre inconnu", utilise le nom du fichier.
            display_title = metadata.get('title', "Titre inconnu")
            if display_title == "Titre inconnu" and 'path' in track_info:
                display_title = os.path.splitext(os.path.basename(track_info['path']))[0]

            self.current_track_name.set(display_title)
            self.current_artist_name.set(metadata.get('artist', "Artiste inconnu"))
            self.current_album_name.set(metadata.get('album', "Album inconnu"))
            # Utilise la fonction format_time de gui_logic.py pour l'affichage de l'UI
            self.total_time_str.set(format_time(duration_ms))

            if duration_ms > 0:
                self.progress_bar["maximum"] = duration_ms
            else:
                self.progress_bar["maximum"] = 1  # Empêche une division par zéro si durée 0

        else:
            # Si la playlist est vide ou l'index est invalide
            self.current_track_name.set("Aucune musique chargée")
            self.current_artist_name.set("Artiste inconnu")
            self.current_album_name.set("Album inconnu")
            self.total_time_str.set("00:00")
            self.progress_bar["maximum"] = 0  # Pas de progression
            self.progress_bar["value"] = 0

        if self.player.is_playing and not self.player.is_paused:
            self.play_pause_button.config(text="⏯️ Pause")
        else:
            self.play_pause_button.config(text="▶️ Play")

        self._highlight_current_track()

    def toggle_play_pause(self):
        """Bascule entre lecture et pause."""
        self.player.toggle_pause()
        self._update_ui_for_new_track() # Appelle la fonction de mise à jour centralisée

    def play_next(self):
        """Passe à la musique suivante."""
        self.player.play_next_music()
        self._update_ui_for_new_track()

    def play_previous(self):
        """Passe à la musique précédente."""
        self.player.play_previous_music()
        self._update_ui_for_new_track()

    def set_volume(self, val):
        """Définit le volume du mixeur Pygame."""
        volume = float(val) / 100.0
        pygame.mixer.music.set_volume(volume)

    def update_player_status(self):
        """
        Appelée périodiquement pour mettre à jour l'état du lecteur Pygame
        et l'interface graphique (temps, progression).
        """
        previous_track_index = self.player.current_track_index

        self.player.update() # Demande au lecteur Pygame de vérifier s'il doit passer au morceau suivant

        if self.player.current_track_index != previous_track_index:
            self._update_ui_for_new_track() # Mise à jour complète de l'UI si le morceau a changé

        current_pos_ms = self.player.get_current_time_ms()
        self.current_time_str.set(format_time(current_pos_ms))
        self.progress_bar["value"] = current_pos_ms

        # Ré-planifie cet appel pour la prochaine mise à jour
        if self.player.is_playing or self.player.is_paused or pygame.mixer.music.get_busy():
            self.master.after(self.update_interval, self.update_player_status)
        else:
            # Si aucune musique n'est active, on peut ralentir le taux de rafraîchissement
            # ou arrêter complètement l'update si l'appli ne doit pas attendre de nouvelle action.
            # Pour l'instant, on maintient un intervalle pour relancer si besoin.
            self.master.after(1000, self.update_player_status)


    def on_closing(self):
        """Gère la fermeture de l'application."""
        print("Fermeture de l'application...")
        self.player.quit()
        self.master.destroy()