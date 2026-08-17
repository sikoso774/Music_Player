# src/gui/music_app_gui.py

import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox, QLayout

from src.player.music_player import MusicPlayer
from src.player.vlc_setup import VlcNotAvailableError
from src.player.audio_info import get_cover_bytes
from src.gui import theme
from src.gui.gui_widgets import (
    NowPlayingWidget, ProgressWidget, ControlsWidget, VolumeWidget, PlaylistWidget,
)
from src.resource_path import resource_path


class MusicAppGUI(QMainWindow):
    WINDOW_W = 480
    MARGIN = 16  # marge horizontale du layout central
    UPDATE_INTERVAL_MS = 100

    def __init__(self, found_musics):
        super().__init__()
        self.startup_failed = False

        self.setWindowTitle("Mon Lecteur Musical")
        self.setWindowIcon(QIcon(resource_path("assets/icon/zkz_icon.ico")))
        self.setStyleSheet(theme.build_stylesheet())
        # La taille est entièrement pilotée par le contenu (cf. _build_ui) : agrandir
        # la fenêtre laisserait le contenu collé à gauche avec une zone morte à droite.
        # On retire donc le bouton maximiser — équivalent du resizable(False, False)
        # de la version CustomTkinter.
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowTitleHint
            | Qt.WindowSystemMenuHint
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowCloseButtonHint
        )

        try:
            self.player = MusicPlayer(found_musics)
        except VlcNotAvailableError:
            print("Erreur : VLC n'est pas installé ou n'a pas pu être initialisé. "
                  "L'application GUI ne démarrera pas.")
            QMessageBox.critical(
                self,
                "VLC introuvable",
                "VLC media player n'a pas été détecté sur cet ordinateur.\n\n"
                "Ce lecteur a besoin de VLC pour fonctionner. Merci d'installer VLC "
                "(gratuit) depuis :\nhttps://www.videolan.org/vlc/\n\n"
                "puis de relancer l'application."
            )
            self.startup_failed = True
            return

        if not self.player.playlist:
            print("Erreur: La playlist est vide. L'application GUI ne démarrera pas correctement.")
            self.startup_failed = True
            return

        self._build_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_player_status)

        self.player.load_and_play_music(0)
        self._update_ui_for_new_track()
        self.timer.start(self.UPDATE_INTERVAL_MS)

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        central.setAttribute(Qt.WA_StyledBackground, True)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(self.MARGIN, 16, self.MARGIN, 8)
        layout.setSpacing(10)
        # Force la fenêtre à toujours épouser la taille du contenu : c'est ce qui
        # rend le repli/dépli de la playlist fluide (la fenêtre suit l'animation
        # de hauteur de PlaylistWidget) et empêche le redimensionnement manuel.
        layout.setSizeConstraint(QLayout.SetFixedSize)
        # SetFixedSize contraint le widget à son sizeHint et écrase tout
        # setFixedWidth() posé à côté : la largeur voulue doit donc être imposée
        # *depuis l'intérieur* du layout. addStrut() fixe la largeur minimale du
        # contenu (dimension perpendiculaire à un layout vertical), ce qui porte
        # le sizeHint à WINDOW_W au lieu de la largeur naturelle des widgets.
        layout.addStrut(self.WINDOW_W - 2 * self.MARGIN)

        # QMainWindow ne reprend pas la contrainte de taille de son widget central :
        # sans ça la fenêtre reste redimensionnable et le contenu se retrouve collé
        # à gauche. On applique la même contrainte au layout de la fenêtre pour
        # qu'elle épouse son contenu (et suive donc l'animation de la playlist).
        self.layout().setSizeConstraint(QLayout.SetFixedSize)

        self.now_playing = NowPlayingWidget()
        layout.addWidget(self.now_playing)

        self.progress = ProgressWidget()
        self.progress.seek_committed.connect(self._on_seek_committed)
        layout.addWidget(self.progress)

        self.controls = ControlsWidget()
        self.controls.prev_clicked.connect(self.play_previous)
        self.controls.play_pause_clicked.connect(self.toggle_play_pause)
        self.controls.next_clicked.connect(self.play_next)
        layout.addWidget(self.controls)

        self.volume = VolumeWidget()
        self.volume.set_volume(self.player.get_volume())
        self.volume.volume_changed.connect(self.set_volume)
        layout.addWidget(self.volume)

        self.playlist = PlaylistWidget()
        self.playlist.populate(self.player.playlist)
        self.playlist.track_activated.connect(self._on_playlist_track_activated)
        layout.addWidget(self.playlist)

        copyright_label = QLabel("Copyright: Zoléni KOKOLO ZASSI, 2025 ;)")
        copyright_label.setObjectName("copyrightLabel")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)

    def _on_playlist_track_activated(self, index):
        self.player.load_and_play_music(index)
        self._update_ui_for_new_track()

    def _on_seek_committed(self, position_ms):
        self.player.seek_music(position_ms)
        self.controls.set_playing(self.player.is_playing and not self.player.is_paused)

    def _update_ui_for_new_track(self):
        """Met à jour tous les éléments de l'UI liés au morceau actuel."""
        track_info = self.player.get_current_track_info()
        if track_info:
            metadata = track_info.get('metadata', {})
            duration_ms = track_info.get('duration_ms', 0)

            display_title = metadata.get('title', "Titre inconnu")
            if display_title == "Titre inconnu" and 'path' in track_info:
                display_title = os.path.splitext(os.path.basename(track_info['path']))[0]

            self.now_playing.set_track_info(
                display_title,
                metadata.get('artist', "Artiste inconnu"),
                metadata.get('album', "Album inconnu"),
            )
            self.progress.set_duration(duration_ms)
            self.now_playing.set_cover(get_cover_bytes(track_info['path']))
        else:
            self.now_playing.set_track_info("Aucune musique chargée", "Artiste inconnu", "Album inconnu")
            self.progress.reset()
            self.now_playing.set_cover(None)

        self.controls.set_playing(self.player.is_playing and not self.player.is_paused)
        self.playlist.highlight_current(self.player.current_track_index)

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

    def set_volume(self, value):
        """Définit le volume de lecture."""
        self.player.set_volume(value)

    def update_player_status(self):
        """
        Appelée périodiquement (QTimer) pour mettre à jour l'état du lecteur
        et l'interface graphique (temps, progression).
        """
        previous_track_index = self.player.current_track_index

        self.player.update()

        if self.player.current_track_index != previous_track_index:
            self._update_ui_for_new_track()

        if not self.progress.is_seeking:
            self.progress.update_position(self.player.get_current_time_ms())

        interval = self.UPDATE_INTERVAL_MS if (self.player.is_playing or self.player.is_paused) else 1000
        self.timer.setInterval(interval)

    def closeEvent(self, event):
        """Gère la fermeture de l'application."""
        print("Fermeture de l'application...")
        if hasattr(self, "timer"):
            self.timer.stop()
        if hasattr(self, "player"):
            self.player.quit()
        super().closeEvent(event)
