# src/gui/theme.py
# Palette et constantes de style pour le thème "néon" (vert/orange) de l'appli.

BG_WINDOW = "#0a0a0a"       # Fond de la fenêtre principale
BG_PANEL = "#111411"        # Fond des cadres/panneaux
BG_PANEL_LIGHT = "#181d18"  # Fond légèrement plus clair (listbox, hover de fond)

GREEN = "#39ff6a"           # Accent principal (lecture, progression, sélection)
GREEN_DIM = "#1f8f42"       # Vert atténué (hover, bordures secondaires)
ORANGE = "#ff8c1a"          # Accent secondaire (artiste, volume, précédent/suivant)
ORANGE_DIM = "#a85c10"      # Orange atténué (hover)

TEXT_PRIMARY = "#eafbea"    # Titre du morceau
TEXT_SECONDARY = "#8fa38f"  # Temps, labels secondaires
TEXT_MUTED = "#5c6b5c"      # Album, copyright

BORDER = "#1f4d2e"          # Bordures de cadres/panneaux

FONT_FAMILY = "Segoe UI"


def build_stylesheet():
    """
    Génère le QSS global de l'appli à partir des constantes ci-dessus.
    Les widgets ciblés sont sélectionnés par objectName (voir gui_widgets.py).
    """
    return f"""
    QMainWindow, QWidget#centralWidget {{
        background-color: {BG_WINDOW};
    }}

    QWidget#nowPlayingPanel, QWidget#playlistListPanel {{
        background-color: {BG_PANEL};
        border: 1px solid {BORDER};
        border-radius: 12px;
    }}

    QLabel#albumArt {{
        background-color: {BG_PANEL_LIGHT};
        border: 2px solid {GREEN};
        border-radius: 8px;
        color: {GREEN};
        font-size: 30px;
    }}

    QLabel#trackLabel {{
        color: {TEXT_PRIMARY};
        font-size: 15px;
        font-weight: bold;
    }}

    QLabel#artistLabel {{
        color: {ORANGE};
        font-size: 12px;
        font-weight: bold;
    }}

    QLabel#albumLabel {{
        color: {TEXT_MUTED};
        font-size: 10px;
        font-style: italic;
    }}

    QLabel#timeLabel {{
        color: {TEXT_SECONDARY};
        font-size: 10px;
    }}

    QLabel#volumeCaption {{
        color: {TEXT_SECONDARY};
        font-size: 11px;
    }}

    QLabel#copyrightLabel {{
        color: {TEXT_MUTED};
        font-size: 9px;
    }}

    QSlider#progressSlider::groove:horizontal {{
        height: 8px;
        background: {BG_PANEL_LIGHT};
        border: 1px solid {GREEN_DIM};
        border-radius: 4px;
    }}
    QSlider#progressSlider::sub-page:horizontal {{
        background: {GREEN};
        border-radius: 4px;
    }}
    QSlider#progressSlider::handle:horizontal {{
        background: {GREEN};
        width: 12px;
        margin: -4px 0;
        border-radius: 6px;
    }}

    QSlider#volumeSlider::groove:horizontal {{
        height: 6px;
        background: {BG_PANEL_LIGHT};
        border-radius: 3px;
    }}
    QSlider#volumeSlider::sub-page:horizontal {{
        background: {ORANGE};
        border-radius: 3px;
    }}
    QSlider#volumeSlider::handle:horizontal {{
        background: {ORANGE};
        width: 12px;
        margin: -4px 0;
        border-radius: 6px;
    }}
    QSlider#volumeSlider::handle:horizontal:hover {{
        background: {GREEN};
    }}

    QPushButton#sideControlButton {{
        background-color: transparent;
        color: {ORANGE};
        border: 1px solid {ORANGE_DIM};
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }}
    QPushButton#sideControlButton:hover {{
        background-color: {BG_PANEL_LIGHT};
    }}

    QPushButton#playPauseButton {{
        background-color: {GREEN_DIM};
        color: {BG_WINDOW};
        border: none;
        border-radius: 28px;
        font-size: 22px;
        font-weight: bold;
    }}
    QPushButton#playPauseButton:hover {{
        background-color: {GREEN};
    }}

    QPushButton#playlistToggle {{
        background-color: {BG_PANEL};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER};
        border-radius: 6px;
        text-align: left;
        padding-left: 10px;
        font-size: 12px;
        font-weight: bold;
        height: 34px;
    }}
    QPushButton#playlistToggle:hover {{
        background-color: {BG_PANEL_LIGHT};
    }}

    QListWidget#playlistListWidget {{
        background-color: {BG_PANEL};
        color: {TEXT_PRIMARY};
        border: none;
        font-size: 10px;
    }}
    QListWidget#playlistListWidget::item {{
        padding: 4px 6px;
    }}
    QListWidget#playlistListWidget::item:selected {{
        background-color: {GREEN_DIM};
        color: {TEXT_PRIMARY};
    }}

    QScrollBar:vertical {{
        background: {BG_PANEL};
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {GREEN_DIM};
        border-radius: 4px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {GREEN};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """
