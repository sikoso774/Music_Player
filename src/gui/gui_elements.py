# src/gui/gui_elements.py

import customtkinter as ctk
import tkinter as tk # Garder l'import pour la Listbox

from src.gui import theme

def create_main_window(master, title="Mon Lecteur Musical", geometry="500x540", icon_path="assets/icon/zkz_icon.ico"):
    """Configure la fenêtre principale de l'application."""
    ctk.set_appearance_mode("dark")
    master.title(title)
    master.geometry(geometry)
    master.configure(fg_color=theme.BG_WINDOW)
    if icon_path:
        try:
            master.iconbitmap(icon_path)
        except tk.TclError:
            icon_path = None
            master.iconbitmap(icon_path)

    # master.resizable(False, False)

def create_track_label(master, textvariable):
    """Crée et retourne le label d'affichage du nom du morceau."""
    label = ctk.CTkLabel(master, textvariable=textvariable,
                         font=ctk.CTkFont(family=theme.FONT_FAMILY, size=17, weight="bold"),
                         text_color=theme.TEXT_PRIMARY, wraplength=450, anchor="center")
    label.pack(pady=(20, 5))
    return label

def create_artist_label(master, textvariable):
    """Crée et retourne le label d'affichage de l'artiste."""
    label = ctk.CTkLabel(master, textvariable=textvariable,
                         font=ctk.CTkFont(family=theme.FONT_FAMILY, size=12, weight="bold"),
                         text_color=theme.ORANGE, wraplength=450, anchor="center")
    label.pack(pady=2)
    return label

def create_album_label(master, textvariable):
    """Crée et retourne le label d'affichage de l'album."""
    label = ctk.CTkLabel(master, textvariable=textvariable,
                         font=ctk.CTkFont(family=theme.FONT_FAMILY, size=10, slant="italic"),
                         text_color=theme.TEXT_MUTED, wraplength=450, anchor="center")
    label.pack(pady=2)
    return label

def create_time_frame(master):
    """Crée et retourne le cadre contenant les labels de temps et la barre de progression."""
    time_frame = ctk.CTkFrame(master, fg_color="transparent")
    time_frame.pack(pady=5, fill="x", padx=20)
    return time_frame

def create_time_labels(parent_frame, current_time_var, total_time_var):
    """Crée et retourne les labels d'affichage du temps écoulé et total."""
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
    """Crée et retourne la barre de progression."""
    progress_bar = ctk.CTkProgressBar(parent_frame, orientation="horizontal",
                                      fg_color=theme.BG_PANEL_LIGHT, progress_color=theme.GREEN,
                                      border_color=theme.GREEN_DIM, border_width=1)
    progress_bar.pack(side="left", padx=10, expand=True, fill="x")
    return progress_bar

def create_control_buttons_frame(master):
    """Crée et retourne le cadre pour les boutons de contrôle."""
    control_frame = ctk.CTkFrame(master, fg_color="transparent")
    control_frame.pack(pady=10)
    return control_frame

def create_control_buttons(parent_frame, play_previous_cmd, toggle_play_pause_cmd, play_next_cmd):
    """Crée et retourne les boutons Précédent, Play/Pause, Suivant avec une largeur réduite."""

    # Largeur de 90 pixels, tu peux ajuster cette valeur
    button_width = 90

    side_button_style = dict(
        fg_color="transparent", hover_color=theme.BG_PANEL_LIGHT,
        text_color=theme.ORANGE, border_color=theme.ORANGE_DIM, border_width=1,
    )

    prev_button = ctk.CTkButton(parent_frame, text="⏮ Précédent", command=play_previous_cmd,
                                width=button_width, **side_button_style)
    prev_button.pack(side="left", padx=5)

    play_pause_button = ctk.CTkButton(parent_frame, text="▶ Play", command=toggle_play_pause_cmd,
                                      width=button_width, fg_color=theme.GREEN_DIM,
                                      hover_color=theme.GREEN, text_color=theme.BG_WINDOW,
                                      font=ctk.CTkFont(family=theme.FONT_FAMILY, weight="bold"))
    play_pause_button.pack(side="left", padx=5)

    next_button = ctk.CTkButton(parent_frame, text="Suivant ⏭", command=play_next_cmd,
                                width=button_width, **side_button_style)
    next_button.pack(side="left", padx=5)

    return prev_button, play_pause_button, next_button

def create_volume_slider(master, set_volume_cmd, initial_volume=50):
    """Crée et retourne le slider de volume."""
    volume_frame = ctk.CTkFrame(master, fg_color="transparent")
    volume_frame.pack(pady=(10, 5))

    ctk.CTkLabel(volume_frame, text="Volume:", text_color=theme.TEXT_SECONDARY,
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=11)).pack(side="left", padx=(0, 5))
    volume_slider = ctk.CTkSlider(volume_frame, from_=0, to=100, orientation="horizontal",
                                  command=set_volume_cmd, width=150,
                                  fg_color=theme.BG_PANEL_LIGHT, progress_color=theme.ORANGE,
                                  button_color=theme.ORANGE, button_hover_color=theme.GREEN)
    volume_slider.set(initial_volume)
    volume_slider.pack(side="left")
    return volume_slider

def create_copyright_label(master, author_name="Zoléni KOKOLO ZASSI", year=2025):
    """Crée et retourne le label de copyright."""
    label = ctk.CTkLabel(master, text=f"Copyright: {author_name}, {year} ;)",
                         font=ctk.CTkFont(family=theme.FONT_FAMILY, size=9, weight="normal"),
                         text_color=theme.TEXT_MUTED)
    label.pack(side="bottom", pady=10)
    return label

def create_playlist_frame(master):
    """Crée et retourne un cadre pour la playlist."""
    playlist_frame = ctk.CTkFrame(master, fg_color="transparent")
    playlist_frame.pack(pady=10, padx=20, fill="both", expand=True)
    return playlist_frame

def create_playlist_listbox(parent_frame, select_callback):
    """Crée et retourne la Listbox de la playlist avec sa scrollbar, stylisée pour CTk."""
    listbox_frame = ctk.CTkFrame(parent_frame, fg_color=theme.BG_PANEL,
                                 border_color=theme.BORDER, border_width=1)
    listbox_frame.pack(fill="both", expand=True)

    playlist_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, height=10,
                                   font=(theme.FONT_FAMILY, 10), bd=0, highlightthickness=0,
                                   bg=theme.BG_PANEL, fg=theme.TEXT_PRIMARY,
                                   selectbackground=theme.GREEN_DIM,
                                   selectforeground=theme.TEXT_PRIMARY)
    playlist_listbox.pack(side="left", fill="both", expand=True, padx=1, pady=1)

    scrollbar = ctk.CTkScrollbar(listbox_frame, command=playlist_listbox.yview,
                                 fg_color=theme.BG_PANEL, button_color=theme.GREEN_DIM,
                                 button_hover_color=theme.GREEN)
    scrollbar.pack(side="right", fill="y")
    playlist_listbox.config(yscrollcommand=scrollbar.set)

    playlist_listbox.bind("<Double-Button-1>", select_callback)

    return playlist_listbox
