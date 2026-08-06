# src/gui/music_app_gui.py

import os
import tkinter as tk # Garder l'import pour la Listbox

import customtkinter as ctk
import pygame

# Importe les classes et fonctions refactorisées
from src.player.music_player import MusicPlayer
from src.gui.gui_elements import (
    create_main_window, create_track_label, create_artist_label, create_album_label,
    create_time_frame, create_time_labels, create_progress_bar,
    create_control_buttons_frame, create_control_buttons, create_volume_slider,
    create_playlist_frame, create_playlist_listbox, create_copyright_label,
)
# Utilise la fonction format_time de gui_logic.py pour l'affichage GUI
from src.gui.gui_logic import format_time, calculate_seek_position


class MusicAppGUI:
    def __init__(self, master, found_musics):
        self.master = master
        create_main_window(master)

        self.player = MusicPlayer(found_musics)

        if not self.player.playlist:
            print("Erreur: La playlist est vide. L'application GUI ne démarrera pas correctement.")
            master.destroy()
            return

        self.current_track_name = ctk.StringVar(value="Aucune musique chargée")
        self.current_time_str = ctk.StringVar(value="00:00")
        self.total_time_str = ctk.StringVar(value="00:00")
        self.current_artist_name = ctk.StringVar(value="Artiste inconnu")
        self.current_album_name = ctk.StringVar(value="Album inconnu")
        self.update_interval = 100

        # --- Widgets de l'interface ---
        self.track_label = create_track_label(master, self.current_track_name)
        self.artist_label = create_artist_label(master, self.current_artist_name)
        self.album_label = create_album_label(master, self.current_album_name)

        time_frame = create_time_frame(master)
        self.time_label, self.total_time_label = create_time_labels(
            time_frame, self.current_time_str, self.total_time_str
        )
        
        
        self._pending_seek_ms = None
        self._is_seeking = False

        self.progress_bar = create_progress_bar(time_frame)
        self.progress_bar.bind("<Button-1>", self.on_progress_bar_press)
        self.progress_bar.bind("<B1-Motion>", self.on_progress_bar_drag)
        self.progress_bar.bind("<ButtonRelease-1>", self.on_progress_bar_release)

        control_frame = create_control_buttons_frame(master)
        self.prev_button, self.play_pause_button, self.next_button = create_control_buttons(
            control_frame, self.play_previous, self.toggle_play_pause, self.play_next
        )
        
        self.volume_slider = create_volume_slider(master, self.set_volume,
                                                  initial_volume=int(pygame.mixer.music.get_volume() * 100))

        playlist_frame = create_playlist_frame(master)
        self.playlist_listbox = create_playlist_listbox(playlist_frame, self.on_playlist_select)
        self._populate_playlist_listbox()

        self.copyright_label = create_copyright_label(master)

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
        self.playlist_listbox.delete(0, tk.END)
        for index, track_info in enumerate(self.player.playlist):
            track_name = os.path.basename(track_info['path'])
            self.playlist_listbox.insert(tk.END, f"{index + 1}. {track_name}")

    def on_playlist_select(self, event):
        """Gère la sélection d'un morceau dans la Listbox (double-clic)."""
        selected_indices = self.playlist_listbox.curselection()
        if selected_indices:
            selected_index = selected_indices[0]
            print(f"Morceau sélectionné dans la liste : {selected_index}")
            self.player.load_and_play_music(selected_index)
            self._update_ui_for_new_track()
            self._highlight_current_track()

    def _highlight_current_track(self):
        """Met en surbrillance le morceau actuellement joué dans la Listbox."""
        self.playlist_listbox.selection_clear(0, tk.END)
        if 0 <= self.player.current_track_index < len(self.player.playlist):
            self.playlist_listbox.selection_set(self.player.current_track_index)
            self.playlist_listbox.activate(self.player.current_track_index)
            self.playlist_listbox.see(self.player.current_track_index)

    def on_progress_bar_press(self, event):
        """Démarre l'aperçu de position au clic sur la barre de progression."""
        self._is_seeking = True
        self._preview_seek_position(event.x)

    def on_progress_bar_drag(self, event):
        """Met à jour l'aperçu pendant le glissement, sans recharger la musique."""
        self._preview_seek_position(event.x)

    def on_progress_bar_release(self, event):
        """Applique le déplacement une fois le clic/glissement terminé."""
        if self._pending_seek_ms is not None:
            self.player.seek_music(self._pending_seek_ms)
            self._pending_seek_ms = None

            if self.player.is_playing:
                self.play_pause_button.configure(text="⏯️ Pause")
            else:
                self.play_pause_button.configure(text="▶️ Play")

        self._is_seeking = False

    def _preview_seek_position(self, click_x):
        """
        Met à jour l'affichage (temps écoulé + barre) selon la position du clic/glissement.
        Le morceau n'est rechargé qu'au relâchement du clic (voir on_progress_bar_release),
        pour éviter de recharger/relancer le fichier audio à chaque pixel parcouru.
        """
        total_duration_ms = self.player.get_current_track_duration_ms()
        if total_duration_ms == 0:
            return

        new_position_ms = calculate_seek_position(click_x, self.progress_bar, total_duration_ms)
        self._pending_seek_ms = new_position_ms
        self.current_time_str.set(format_time(new_position_ms))
        self.progress_bar.set(new_position_ms / total_duration_ms)

    def _update_ui_for_new_track(self):
        """Met à jour tous les éléments de l'UI liés au morceau actuel."""
        if self.player.playlist and 0 <= self.player.current_track_index < len(self.player.playlist):
            track_info = self.player.playlist[self.player.current_track_index]
            metadata = track_info.get('metadata', {})
            duration_ms = track_info.get('duration_ms', 0)

            display_title = metadata.get('title', "Titre inconnu")
            if display_title == "Titre inconnu" and 'path' in track_info:
                display_title = os.path.splitext(os.path.basename(track_info['path']))[0]

            self.current_track_name.set(display_title)
            self.current_artist_name.set(metadata.get('artist', "Artiste inconnu"))
            self.current_album_name.set(metadata.get('album', "Album inconnu"))
            self.total_time_str.set(format_time(duration_ms))

        else:
            self.current_track_name.set("Aucune musique chargée")
            self.current_artist_name.set("Artiste inconnu")
            self.current_album_name.set("Album inconnu")
            self.total_time_str.set("00:00")
            self.progress_bar.set(0) # Mettre la barre de progression à zéro

        if self.player.is_playing and not self.player.is_paused:
            self.play_pause_button.configure(text="⏯️ Pause")
        else:
            self.play_pause_button.configure(text="▶️ Play")

        self._highlight_current_track()

    def toggle_play_pause(self):
        """Bascule entre lecture et pause."""
        self.player.toggle_pause()
        self._update_ui_for_new_track()

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

        self.player.update()

        if self.player.current_track_index != previous_track_index:
            self._update_ui_for_new_track()

        if not self._is_seeking:
            current_pos_ms = self.player.get_current_time_ms()
            self.current_time_str.set(format_time(current_pos_ms))

            total_duration = self.player.get_current_track_duration_ms()
            if total_duration > 0:
                self.progress_bar.set(current_pos_ms / total_duration)

        if self.player.is_playing or self.player.is_paused or pygame.mixer.music.get_busy():
            self.master.after(self.update_interval, self.update_player_status)
        else:
            self.master.after(1000, self.update_player_status)

    def on_closing(self):
        """Gère la fermeture de l'application."""
        print("Fermeture de l'application...")
        self.player.quit()
        self.master.destroy()