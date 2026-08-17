# src/gui/gui_elements.py

import tkinter as tk # Garder l'import pour la Listbox

import customtkinter as ctk

from src.gui import theme
from src.resource_path import resource_path

def create_main_window(master, title="Mon Lecteur Musical", geometry="480x560", icon_path=None):
    """Configure la fenêtre principale de l'application."""
    icon_path = icon_path or resource_path("assets/icon/zkz_icon.ico")
    ctk.set_appearance_mode("dark")
    master.title(title)
    master.geometry(geometry)
    master.resizable(False, False)  # taille pilotée par le code (repli playlist)
    master.configure(fg_color=theme.BG_WINDOW)
    if icon_path:
        try:
            master.iconbitmap(icon_path)
        except tk.TclError:
            master.iconbitmap(None)

def create_now_playing_frame(master):
    """Cadre « en cours de lecture » : pochette à gauche, infos morceau à droite."""
    frame = ctk.CTkFrame(master, fg_color=theme.BG_PANEL, corner_radius=12,
                         border_color=theme.BORDER, border_width=1)
    frame.pack(pady=(16, 8), padx=16, fill="x")
    return frame

def create_album_art(parent, size=76):
    """
    Crée le carré de pochette (bordure néon verte). Retourne le label qui portera
    l'image (via configure(image=...)) ; par défaut il affiche une note ♪.
    """
    container = ctk.CTkFrame(parent, fg_color=theme.BG_PANEL_LIGHT, corner_radius=8,
                             border_color=theme.GREEN, border_width=2,
                             width=size, height=size)
    container.pack(side="left", padx=12, pady=12)
    container.pack_propagate(False)  # garde la taille fixe malgré le contenu

    art_label = ctk.CTkLabel(container, text="♪",
                             font=ctk.CTkFont(family=theme.FONT_FAMILY, size=30),
                             text_color=theme.GREEN)
    art_label.pack(expand=True)
    return art_label

def create_track_info(parent, name_var, artist_var, album_var):
    """Colonne d'infos (titre / artiste / album) alignée à gauche."""
    info = ctk.CTkFrame(parent, fg_color="transparent")
    info.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=12)

    track_label = ctk.CTkLabel(info, textvariable=name_var, anchor="w", justify="left",
                               font=ctk.CTkFont(family=theme.FONT_FAMILY, size=15, weight="bold"),
                               text_color=theme.TEXT_PRIMARY, wraplength=280)
    track_label.pack(fill="x")
    artist_label = ctk.CTkLabel(info, textvariable=artist_var, anchor="w",
                                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                                text_color=theme.ORANGE)
    artist_label.pack(fill="x")
    album_label = ctk.CTkLabel(info, textvariable=album_var, anchor="w",
                               font=ctk.CTkFont(family=theme.FONT_FAMILY, size=10, slant="italic"),
                               text_color=theme.TEXT_MUTED)
    album_label.pack(fill="x")
    return track_label, artist_label, album_label

def create_time_frame(master):
    """Cadre contenant les labels de temps et la barre de progression."""
    time_frame = ctk.CTkFrame(master, fg_color="transparent")
    time_frame.pack(pady=4, fill="x", padx=20)
    return time_frame

def create_time_labels(parent_frame, current_time_var, total_time_var):
    """Labels du temps écoulé et total."""
    current_label = ctk.CTkLabel(parent_frame, textvariable=current_time_var,
                                 font=ctk.CTkFont(family=theme.FONT_FAMILY, size=10),
                                 text_color=theme.TEXT_SECONDARY)
    current_label.pack(side="left")

    total_label = ctk.CTkLabel(parent_frame, textvariable=total_time_var,
                               font=ctk.CTkFont(family=theme.FONT_FAMILY, size=10),
                               text_color=theme.TEXT_SECONDARY)
    total_label.pack(side="right")
    return current_label, total_label

def create_progress_bar(parent_frame):
    """Barre de progression néon."""
    progress_bar = ctk.CTkProgressBar(parent_frame, orientation="horizontal", height=8,
                                      fg_color=theme.BG_PANEL_LIGHT, progress_color=theme.GREEN,
                                      border_color=theme.GREEN_DIM, border_width=1)
    progress_bar.pack(side="left", padx=10, expand=True, fill="x")
    return progress_bar

def create_control_buttons_frame(master):
    """Cadre pour les boutons de contrôle."""
    control_frame = ctk.CTkFrame(master, fg_color="transparent")
    control_frame.pack(pady=12)
    return control_frame

def create_control_buttons(parent_frame, play_previous_cmd, toggle_play_pause_cmd, play_next_cmd):
    """Boutons circulaires : Précédent / Suivant ronds orange, Play/Pause gros rond vert."""
    side_style = dict(
        width=40, height=40, corner_radius=20, fg_color="transparent",
        hover_color=theme.BG_PANEL_LIGHT, text_color=theme.ORANGE,
        border_color=theme.ORANGE_DIM, border_width=1, font=ctk.CTkFont(size=16),
    )

    prev_button = ctk.CTkButton(parent_frame, text="⏮", command=play_previous_cmd, **side_style)
    prev_button.pack(side="left", padx=10)

    play_pause_button = ctk.CTkButton(parent_frame, text="▶", command=toggle_play_pause_cmd,
                                      width=56, height=56, corner_radius=28,
                                      fg_color=theme.GREEN_DIM, hover_color=theme.GREEN,
                                      text_color=theme.BG_WINDOW,
                                      font=ctk.CTkFont(size=22, weight="bold"))
    play_pause_button.pack(side="left", padx=10)

    next_button = ctk.CTkButton(parent_frame, text="⏭", command=play_next_cmd, **side_style)
    next_button.pack(side="left", padx=10)

    return prev_button, play_pause_button, next_button

def create_volume_slider(master, set_volume_cmd, initial_volume=50):
    """Slider de volume néon (orange)."""
    volume_frame = ctk.CTkFrame(master, fg_color="transparent")
    volume_frame.pack(pady=(2, 8))

    ctk.CTkLabel(volume_frame, text="Volume", text_color=theme.TEXT_SECONDARY,
                 font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11)).pack(side="left", padx=(0, 8))
    volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, orientation="horizontal",
                                  command=set_volume_cmd, width=180,
                                  fg_color=theme.BG_PANEL_LIGHT, progress_color=theme.ORANGE,
                                  button_color=theme.ORANGE, button_hover_color=theme.GREEN)
    volume_slider.set(initial_volume)
    volume_slider.pack(side="left")
    return volume_slider

def create_playlist_toggle(master, command):
    """Barre-bouton qui replie/déplie la playlist. Le texte est piloté par le contrôleur."""
    toggle = ctk.CTkButton(master, command=command, anchor="w",
                           fg_color=theme.BG_PANEL, hover_color=theme.BG_PANEL_LIGHT,
                           text_color=theme.TEXT_PRIMARY, border_color=theme.BORDER, border_width=1,
                           corner_radius=6, height=34,
                           font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"))
    toggle.pack(pady=(4, 0), padx=16, fill="x")
    return toggle

def create_playlist_frame(master):
    """Cadre pour la playlist (packé/dépacké lors du repli)."""
    playlist_frame = ctk.CTkFrame(master, fg_color="transparent")
    playlist_frame.pack(pady=(6, 8), padx=16, fill="both", expand=True)
    return playlist_frame

def create_playlist_listbox(parent_frame, select_callback):
    """Listbox de la playlist, stylisée néon, avec sa scrollbar."""
    listbox_frame = ctk.CTkFrame(parent_frame, fg_color=theme.BG_PANEL,
                                 border_color=theme.BORDER, border_width=1, corner_radius=6)
    listbox_frame.pack(fill="both", expand=True)

    playlist_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, height=8,
                                   font=(theme.FONT_FAMILY, 10), bd=0, highlightthickness=0,
                                   bg=theme.BG_PANEL, fg=theme.TEXT_PRIMARY,
                                   selectbackground=theme.GREEN_DIM,
                                   selectforeground=theme.TEXT_PRIMARY,
                                   activestyle="none")
    playlist_listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)

    scrollbar = ctk.CTkScrollbar(listbox_frame, command=playlist_listbox.yview,
                                 fg_color=theme.BG_PANEL, button_color=theme.GREEN_DIM,
                                 button_hover_color=theme.GREEN)
    scrollbar.pack(side="right", fill="y")
    playlist_listbox.config(yscrollcommand=scrollbar.set)

    playlist_listbox.bind("<Double-Button-1>", select_callback)

    return playlist_listbox

def create_copyright_label(master, author_name="Zoléni KOKOLO ZASSI", year=2025):
    """Label de copyright."""
    label = ctk.CTkLabel(master, text=f"Copyright: {author_name}, {year} ;)",
                         font=ctk.CTkFont(family=theme.FONT_FAMILY, size=9, weight="normal"),
                         text_color=theme.TEXT_MUTED)
    label.pack(side="bottom", pady=8)
    return label
