# scripts/gui/gui_elements.py

import customtkinter as ctk
import tkinter as tk # Garder l'import pour la Listbox

def create_main_window(master, title="Mon Lecteur Musical", geometry="500x350", icon_path="assets/icon/music_player_icon.ico"):
    """Configure la fenêtre principale de l'application."""
    master.title(title)
    master.geometry(geometry)
    if icon_path:
        try:
            master.iconbitmap(icon_path)
        except tk.TclError:
            icon_path = None
            master.iconbitmap(icon_path)
            
    # master.resizable(False, False)

def create_track_label(master, textvariable):
    """Crée et retourne le label d'affichage du nom du morceau."""
    label = ctk.CTkLabel(master, textvariable=textvariable, font=ctk.CTkFont(size=16, weight="bold"),
                         wraplength=450, anchor="center")
    label.pack(pady=(20, 5))
    return label

def create_artist_label(master, textvariable):
    """Crée et retourne le label d'affichage de l'artiste."""
    label = ctk.CTkLabel(master, textvariable=textvariable, font=ctk.CTkFont(size=12),
                         wraplength=450, anchor="center")
    label.pack(pady=2)
    return label

def create_album_label(master, textvariable):
    """Crée et retourne le label d'affichage de l'album."""
    label = ctk.CTkLabel(master, textvariable=textvariable, font=ctk.CTkFont(size=10, slant="italic"),
                         wraplength=450, anchor="center")
    label.pack(pady=2)
    return label

def create_time_frame(master):
    """Crée et retourne le cadre contenant les labels de temps et la barre de progression."""
    time_frame = ctk.CTkFrame(master)
    time_frame.pack(pady=5, fill="x", padx=20)
    return time_frame

def create_time_labels(parent_frame, current_time_var, total_time_var):
    """Crée et retourne les labels d'affichage du temps écoulé et total."""
    current_label = ctk.CTkLabel(parent_frame, textvariable=current_time_var, font=ctk.CTkFont(size=10))
    current_label.pack(side="left")

    total_label = ctk.CTkLabel(parent_frame, textvariable=total_time_var, font=ctk.CTkFont(size=10))
    total_label.pack(side="right")
    return current_label, total_label

def create_progress_bar(parent_frame):
    """Crée et retourne la barre de progression."""
    progress_bar = ctk.CTkProgressBar(parent_frame, orientation="horizontal")
    progress_bar.pack(side="left", padx=10, expand=True, fill="x")
    return progress_bar

def create_control_buttons_frame(master):
    """Crée et retourne le cadre pour les boutons de contrôle."""
    control_frame = ctk.CTkFrame(master)
    control_frame.pack(pady=10)
    return control_frame

def create_control_buttons(parent_frame, play_previous_cmd, toggle_play_pause_cmd, play_next_cmd):
    """Crée et retourne les boutons Précédent, Play/Pause, Suivant."""
    prev_button = ctk.CTkButton(parent_frame, text="⏮️ Précédent", command=play_previous_cmd)
    prev_button.pack(side="left", padx=5)

    play_pause_button = ctk.CTkButton(parent_frame, text="▶️ Play", command=toggle_play_pause_cmd)
    play_pause_button.pack(side="left", padx=5)

    next_button = ctk.CTkButton(parent_frame, text="Suivant ⏭️", command=play_next_cmd)
    next_button.pack(side="left", padx=5)
    return prev_button, play_pause_button, next_button

def create_volume_slider(master, set_volume_cmd, initial_volume=50):
    """Crée et retourne le slider de volume."""
    volume_frame = ctk.CTkFrame(master)
    volume_frame.pack(pady=(10, 5))

    ctk.CTkLabel(volume_frame, text="Volume:").pack(side="left", padx=(0, 5))
    volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, orientation="horizontal",
                                  command=set_volume_cmd, width=150)
    volume_slider.set(initial_volume)
    volume_slider.pack(side="left")
    return volume_slider

def create_copyright_label(master, author_name, year):
    """Crée et retourne le label de copyright."""
    label = ctk.CTkLabel(master, text=f"Copyright: {author_name}, {year} ;)",
                         font=ctk.CTkFont(family="Arial", size=9, weight="normal"),
                         text_color="gray")
    label.pack(side="bottom", pady=10)
    return label

def create_playlist_frame(master):
    """Crée et retourne un cadre pour la playlist."""
    playlist_frame = ctk.CTkFrame(master)
    playlist_frame.pack(pady=10, padx=20, fill="both", expand=True)
    return playlist_frame

def create_playlist_listbox(parent_frame, select_callback):
    """Crée et retourne la Listbox de la playlist avec sa scrollbar, stylisée pour CTk."""
    current_appearance = ctk.get_appearance_mode()
    
    if current_appearance == "Dark":
        bg_color = "#2b2b2b"
        text_color = "#ffffff"
        select_bg_color = "#3a7ebf"
    else:
        bg_color = "#dbdbdb"
        text_color = "#000000"
        select_bg_color = "#3a7ebf"

    listbox_frame = ctk.CTkFrame(parent_frame)
    listbox_frame.pack(fill="both", expand=True)
    
    playlist_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, height=10,
                                   font=("Arial", 10), bd=0, highlightthickness=0,
                                   bg=bg_color, fg=text_color,
                                   selectbackground=select_bg_color,
                                   selectforeground=text_color)
    playlist_listbox.pack(side="left", fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(listbox_frame, command=playlist_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    playlist_listbox.config(yscrollcommand=scrollbar.set)

    playlist_listbox.bind("<Double-Button-1>", select_callback)
    
    return playlist_listbox