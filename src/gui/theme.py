# src/gui/theme.py
# Palette et styles du thème « Enseigne » : néon vert/orange sur noir profond.
# Principe néon : le trait lumineux a un cœur quasi blanc (constantes *_CORE),
# la couleur saturée (GREEN/ORANGE) vit dans les halos et les remplissages,
# les *_DEEP servent d'ombres teintées. Le QSS ne sachant faire ni halo ni
# transition, les glows passent par apply_glow() (QGraphicsDropShadowEffect)
# et les dégradés lumineux par les paintEvent de gui_widgets.py.

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect

BG_WINDOW = "#040604"       # Fond de la fenêtre (noir très légèrement vert)
BG_PANEL = "#0a0d0a"        # Fond des panneaux
BG_PANEL_LIGHT = "#131813"  # Fond hover
BG_LIST = "#070a07"         # Fond du panneau de playlist

GREEN_CORE = "#d9ffe6"      # Cœur du tube (texte et traits lumineux)
GREEN = "#39ff6a"           # Halo, remplissages, bordures
GREEN_DIM = "#1f8f42"       # Vert atténué (scrollbar, éléments secondaires)
GREEN_DEEP = "#0d3f1e"      # Ombres teintées, fonds d'accent

ORANGE_CORE = "#ffe2c0"     # Cœur orange (artiste, boutons latéraux)
ORANGE = "#ff8c1a"          # Halo orange, remplissage volume
ORANGE_DIM = "#a85c10"      # Orange atténué
ORANGE_DEEP = "#3d2408"     # Ombre orange teintée

TEXT_PRIMARY = "#eafbea"    # Texte principal
TEXT_SECONDARY = "#9fb59f"  # Labels secondaires
TEXT_MUTED = "#5c6b5c"      # Album, copyright, durées inactives
TIME_TEXT = "#9fd4ae"       # Chiffres de temps (vert doux)

FONT_FAMILY = "Segoe UI"
# Bahnschrift (DIN condensée, livrée avec Windows 10/11) pour les titres ;
# Qt conserve la liste entière comme repli si elle manque (vérifié).
FONT_DISPLAY = '"Bahnschrift", "Segoe UI Semibold", "Segoe UI"'
FONT_MONO = '"Cascadia Mono", "Consolas"'

# Rayons de halo (px). Dosage « Enseigne » : larges, mais jamais plus de deux
# éléments à pleine intensité en même temps (le titre et le bouton lecture).
GLOW_TITLE = 24
GLOW_ARTIST = 14
GLOW_ART = 20
GLOW_PLAY_IDLE = 22
GLOW_PLAY_PULSE = 38    # crête de la respiration pendant la lecture
GLOW_SIDE_HOVER = 16


def apply_glow(widget, color, radius=20, alpha=190):
    """
    Pose un halo néon (ombre portée non décalée) sur un widget.
    Retourne l'effet : à conserver si on veut l'animer (QPropertyAnimation
    sur sa propriété `blurRadius`). Un widget ne peut porter qu'un seul
    QGraphicsEffect — le suivant remplace celui-ci sans avertissement.
    """
    effect = QGraphicsDropShadowEffect(widget)
    effect.setOffset(0, 0)
    effect.setBlurRadius(radius)
    glow_color = QColor(color)
    glow_color.setAlpha(alpha)
    effect.setColor(glow_color)
    widget.setGraphicsEffect(effect)
    return effect


def build_stylesheet():
    """
    Génère le QSS global à partir des constantes ci-dessus.
    Les widgets sont ciblés par objectName. Les sliders et la pochette ne sont
    pas stylés ici : ils se peignent eux-mêmes (paintEvent, cf. gui_widgets.py).
    """
    return f"""
    QMainWindow {{
        background-color: {BG_WINDOW};
    }}

    QWidget#nowPlayingPanel {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                    stop:0 #0c100c, stop:1 #080b08);
        border: 2px solid;
        border-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                      stop:0 {GREEN}, stop:1 {ORANGE});
        border-radius: 16px;
    }}

    QLabel#trackLabel {{
        color: {GREEN_CORE};
        font-family: {FONT_DISPLAY};
        font-size: 17px;
        font-weight: bold;
        letter-spacing: 2px;
        background: transparent;
    }}

    QLabel#artistLabel {{
        color: {ORANGE_CORE};
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 3px;
        background: transparent;
    }}

    QLabel#albumLabel {{
        color: {TEXT_MUTED};
        font-size: 10px;
        letter-spacing: 1px;
        background: transparent;
    }}

    QLabel#timeLabel {{
        color: {TIME_TEXT};
        font-family: {FONT_MONO};
        font-size: 10px;
        background: transparent;
    }}

    QLabel#copyrightLabel {{
        color: {TEXT_MUTED};
        font-size: 9px;
        letter-spacing: 1px;
        background: transparent;
    }}

    QPushButton#sideControlButton {{
        background-color: transparent;
        color: {ORANGE_CORE};
        border: 1px solid #ccffe2c0;
        border-radius: 21px;
        font-size: 12px;
        font-weight: bold;
    }}
    QPushButton#sideControlButton:hover {{
        background-color: #14ff8c1a;
    }}
    QPushButton#sideControlButton:pressed {{
        background-color: #26ff8c1a;
        border-color: {ORANGE_CORE};
        color: #ffffff;
    }}

    QPushButton#playPauseButton {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.7,
                                    stop:0 #102014, stop:0.7 #0a130c, stop:1 #071008);
        color: #ffffff;
        border: 2px solid {GREEN_CORE};
        border-radius: 31px;
        font-size: 16px;
        font-weight: bold;
    }}
    QPushButton#playPauseButton:hover {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.7,
                                    stop:0 #16301e, stop:0.7 #0e1a10, stop:1 #0a130c);
    }}
    QPushButton#playPauseButton:pressed {{
        background: qradialgradient(cx:0.5, cy:0.5, radius:0.7,
                                    stop:0 #1d4028, stop:0.7 #122016, stop:1 #0c160e);
        border-color: #ffffff;
    }}

    QPushButton#playlistToggle {{
        background-color: {BG_PANEL};
        color: {GREEN_CORE};
        border: 1px solid;
        border-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 {GREEN}, stop:1 {ORANGE});
        border-radius: 12px;
        text-align: left;
        padding-left: 12px;
        font-family: {FONT_DISPLAY};
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 3px;
    }}
    QPushButton#playlistToggle:hover {{
        background-color: {BG_PANEL_LIGHT};
    }}

    QWidget#playlistListPanel {{
        background-color: {BG_LIST};
        border: 1px solid #3839ff6a;
        border-radius: 14px;
    }}

    QListWidget#playlistListWidget {{
        background: transparent;
        border: none;
        outline: none;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 4px 2px 4px 0;
    }}
    QScrollBar::handle:vertical {{
        background: {GREEN_DIM};
        border-radius: 3px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {GREEN};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    """
