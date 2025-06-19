# scripts/gui/gui_elements.py

import tkinter as tk
from tkinter import ttk

def create_main_window(master, title="Mon Lecteur Musical", geometry="500x350"):
    """Configure la fenêtre principale de l'application."""
    master.title(title)
    master.geometry(geometry)
    # master.resizable(False, False) # Si tu veux garder cette option, décommente

def create_track_label(master, textvariable):
    """Crée et retourne le label d'affichage du nom du morceau."""
    label = ttk.Label(master, textvariable=textvariable, font=("Arial", 16, "bold"),
                      wraplength=450, anchor="center")
    label.pack(pady=(20, 5))
    return label

def create_artist_label(master, textvariable):
    """Crée et retourne le label d'affichage de l'artiste."""
    label = ttk.Label(master, textvariable=textvariable, font=("Arial", 12),
                      wraplength=450, anchor="center")
    label.pack(pady=2)
    return label

def create_album_label(master, textvariable):
    """Crée et retourne le label d'affichage de l'album."""
    label = ttk.Label(master, textvariable=textvariable, font=("Arial", 10, "italic"),
                      wraplength=450, anchor="center")
    label.pack(pady=2)
    return label

def create_time_frame(master):
    """Crée et retourne le cadre contenant les labels de temps et la barre de progression."""
    time_frame = ttk.Frame(master)
    time_frame.pack(pady=5, fill="x", padx=20)
    return time_frame

def create_time_labels(parent_frame, current_time_var, total_time_var):
    """Crée et retourne les labels d'affichage du temps écoulé et total."""
    current_label = ttk.Label(parent_frame, textvariable=current_time_var, font=("Arial", 10))
    current_label.pack(side="left")

    total_label = ttk.Label(parent_frame, textvariable=total_time_var, font=("Arial", 10))
    total_label.pack(side="right")
    return current_label, total_label

def create_progress_bar(parent_frame):
    """Crée et retourne la barre de progression."""
    progress_bar = ttk.Progressbar(parent_frame, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(side="left", padx=10, expand=True, fill="x")
    return progress_bar

def create_control_buttons_frame(master):
    """Crée et retourne le cadre pour les boutons de contrôle."""
    control_frame = ttk.Frame(master)
    control_frame.pack(pady=10)
    return control_frame

def create_control_buttons(parent_frame, play_previous_cmd, toggle_play_pause_cmd, play_next_cmd):
    """Crée et retourne les boutons Précédent, Play/Pause, Suivant."""
    prev_button = ttk.Button(parent_frame, text="⏮️ Précédent", command=play_previous_cmd)
    prev_button.grid(row=0, column=0, padx=5)

    play_pause_button = ttk.Button(parent_frame, text="▶️ Play", command=toggle_play_pause_cmd)
    play_pause_button.grid(row=0, column=1, padx=5)

    next_button = ttk.Button(parent_frame, text="Suivant ⏭️", command=play_next_cmd)
    next_button.grid(row=0, column=2, padx=5)
    return prev_button, play_pause_button, next_button

def create_volume_slider(master, set_volume_cmd, initial_volume=50):
    """Crée et retourne le slider de volume."""
    volume_frame = ttk.Frame(master)
    volume_frame.pack(pady=(10, 5))

    ttk.Label(volume_frame, text="Volume:").pack(side="left", padx=(0, 5))
    volume_slider = ttk.Scale(volume_frame, from_=0, to_=100, orient="horizontal", command=set_volume_cmd,
                               length=150)
    volume_slider.set(initial_volume) # Définit la position initiale du slider
    volume_slider.pack(side="left")
    return volume_slider

def create_copyright_label(master, text, author_name, year):
    """Crée et retourne le label de copyright."""
    label = ttk.Label(master, text=f"Copyright: {author_name}, {year} ;)", font=("Arial", 9),
                      foreground="gray")
    label.pack(side="bottom", pady=10)
    return label

def create_playlist_frame(master):
    """Crée et retourne un cadre pour la playlist avec un titre."""
    playlist_frame = ttk.LabelFrame(master, text="Playlist")
    playlist_frame.pack(pady=10, padx=20, fill="both", expand=True)
    return playlist_frame

def create_playlist_listbox(parent_frame, select_callback):
    """Crée et retourne la Listbox de la playlist avec sa scrollbar."""
    # Création du cadre pour la listbox et la scrollbar
    listbox_frame = ttk.Frame(parent_frame)
    listbox_frame.pack(fill="both", expand=True)

    playlist_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, height=10,
                                   font=("Arial", 10), bd=0, highlightthickness=0)
    playlist_listbox.pack(side="left", fill="both", expand=True)

    # Création de la scrollbar
    scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=playlist_listbox.yview)
    scrollbar.pack(side="right", fill="y")

    # Lier la scrollbar à la listbox
    playlist_listbox.config(yscrollcommand=scrollbar.set)

    # Lier l'événement de double-clic à la fonction de rappel
    playlist_listbox.bind("<Double-Button-1>", select_callback)

    return playlist_listbox