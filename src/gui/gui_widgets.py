# src/gui/gui_widgets.py
# Widgets custom PySide6, un cran par morceau d'UI (pochette+infos, progression,
# contrôles, volume, playlist repliable). Chaque widget expose ses propres
# signaux Qt ; le câblage vers MusicPlayer se fait dans music_app_gui.py.

import os

from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton,
    QListWidget, QFrame, QStyle,
)

from src.time_format import format_time


class _ClickSlider(QSlider):
    """QSlider dont un clic sur la piste saute directement à la position cliquée
    (comportement par défaut de QSlider : un simple page-step)."""

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            value = QStyle.sliderValueFromPosition(
                self.minimum(), self.maximum(), int(event.position().x()), self.width()
            )
            self.setValue(value)
            self.sliderMoved.emit(value)
        super().mousePressEvent(event)


class NowPlayingWidget(QWidget):
    """Cadre « en cours de lecture » : pochette à gauche, infos morceau à droite."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("nowPlayingPanel")
        # Un QWidget brut ne peint pas background-color/border du QSS sans cet
        # attribut (contrairement à QFrame/QLabel/QPushButton qui le font nativement).
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.album_art_label = QLabel("♪")
        self.album_art_label.setObjectName("albumArt")
        self.album_art_label.setFixedSize(76, 76)
        self.album_art_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.album_art_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.track_label = QLabel("Aucune musique chargée")
        self.track_label.setObjectName("trackLabel")
        self.track_label.setWordWrap(True)

        self.artist_label = QLabel("Artiste inconnu")
        self.artist_label.setObjectName("artistLabel")

        self.album_label = QLabel("Album inconnu")
        self.album_label.setObjectName("albumLabel")

        info_layout.addWidget(self.track_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addWidget(self.album_label)
        info_layout.addStretch()

        layout.addLayout(info_layout, stretch=1)

    def set_track_info(self, title, artist, album):
        self.track_label.setText(title)
        self.artist_label.setText(artist)
        self.album_label.setText(album)

    def set_cover(self, cover_bytes):
        """Affiche la pochette donnée (bytes bruts, recadrée en carré), ou la note ♪ par défaut."""
        if cover_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(cover_bytes):
                size = self.album_art_label.width()
                scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                x = max(0, (scaled.width() - size) // 2)
                y = max(0, (scaled.height() - size) // 2)
                self.album_art_label.setPixmap(scaled.copy(x, y, size, size))
                return
        self.album_art_label.clear()
        self.album_art_label.setText("♪")


class ProgressWidget(QWidget):
    """Temps écoulé + barre de progression + temps total."""

    seek_previewed = Signal(int)   # position (ms) pendant le glissement
    seek_committed = Signal(int)   # position (ms) au relâchement

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.current_time_label = QLabel("00:00")
        self.current_time_label.setObjectName("timeLabel")

        self.slider = _ClickSlider(Qt.Horizontal)
        self.slider.setObjectName("progressSlider")
        self.slider.setRange(0, 0)

        self.total_time_label = QLabel("00:00")
        self.total_time_label.setObjectName("timeLabel")

        layout.addWidget(self.current_time_label)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.total_time_label)

        self._is_seeking = False
        self.slider.sliderPressed.connect(self._on_pressed)
        self.slider.sliderMoved.connect(self._on_moved)
        self.slider.sliderReleased.connect(self._on_released)

    def _on_pressed(self):
        self._is_seeking = True

    def _on_moved(self, value):
        self.current_time_label.setText(format_time(value))
        self.seek_previewed.emit(value)

    def _on_released(self):
        self._is_seeking = False
        self.seek_committed.emit(self.slider.value())

    @property
    def is_seeking(self):
        return self._is_seeking

    def set_duration(self, duration_ms):
        self.slider.setRange(0, max(duration_ms, 0))
        self.total_time_label.setText(format_time(duration_ms))

    def update_position(self, position_ms):
        """Met à jour l'affichage pendant la lecture normale (pas en cours de seek)."""
        if self._is_seeking:
            return
        self.slider.blockSignals(True)
        self.slider.setValue(position_ms)
        self.slider.blockSignals(False)
        self.current_time_label.setText(format_time(position_ms))

    def reset(self):
        self.slider.blockSignals(True)
        self.slider.setRange(0, 0)
        self.slider.blockSignals(False)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")


class ControlsWidget(QWidget):
    """Boutons de transport : Précédent / Play-Pause / Suivant."""

    prev_clicked = Signal()
    play_pause_clicked = Signal()
    next_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        # ◀◀/▶▶ plutôt que ⏮/⏭ : ces derniers appartiennent à une plage Unicode
        # que Windows restyle avec ses propres icônes couleur "Fluent", ce qui
        # écrase entièrement le QSS (fond bleu opaque au lieu du cercle orange).
        self.prev_button = QPushButton("◀◀")
        self.prev_button.setObjectName("sideControlButton")
        self.prev_button.setFixedSize(40, 40)

        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.setObjectName("playPauseButton")
        self.play_pause_button.setFixedSize(56, 56)

        self.next_button = QPushButton("▶▶")
        self.next_button.setObjectName("sideControlButton")
        self.next_button.setFixedSize(40, 40)

        for button in (self.prev_button, self.play_pause_button, self.next_button):
            button.setCursor(Qt.PointingHandCursor)
            layout.addWidget(button)

        self.prev_button.clicked.connect(self.prev_clicked)
        self.play_pause_button.clicked.connect(self.play_pause_clicked)
        self.next_button.clicked.connect(self.next_clicked)

    def set_playing(self, is_playing):
        # "▮▮" plutôt que "⏸" : même piège Unicode que ⏮/⏭ (icône Windows colorée).
        self.play_pause_button.setText("▮▮" if is_playing else "▶")


class VolumeWidget(QWidget):
    """Label « Volume » + slider 0-100."""

    volume_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        caption = QLabel("Volume")
        caption.setObjectName("volumeCaption")
        layout.addWidget(caption)

        self.slider = _ClickSlider(Qt.Horizontal)
        self.slider.setObjectName("volumeSlider")
        self.slider.setRange(0, 100)
        self.slider.setFixedWidth(180)
        layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self.volume_changed)

    def set_volume(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)


class PlaylistWidget(QWidget):
    """Bouton de repli + liste des morceaux (QListWidget), hauteur animée."""

    track_activated = Signal(int)
    expanded_changed = Signal(bool)

    EXPANDED_HEIGHT = 200

    def __init__(self, parent=None):
        super().__init__(parent)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)

        self.toggle_button = QPushButton()
        self.toggle_button.setObjectName("playlistToggle")
        self.toggle_button.setFixedHeight(34)
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        outer.addWidget(self.toggle_button)

        self.list_panel = QWidget()
        self.list_panel.setObjectName("playlistListPanel")
        self.list_panel.setAttribute(Qt.WA_StyledBackground, True)
        self.list_panel.setMaximumHeight(self.EXPANDED_HEIGHT)
        panel_layout = QVBoxLayout(self.list_panel)
        panel_layout.setContentsMargins(6, 6, 6, 6)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("playlistListWidget")
        self.list_widget.setFrameShape(QFrame.NoFrame)
        panel_layout.addWidget(self.list_widget)

        outer.addWidget(self.list_panel)

        self._expanded = True
        self._track_count = 0

        self._animation = QPropertyAnimation(self.list_panel, b"maximumHeight", self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)

        self.toggle_button.clicked.connect(lambda: self.set_expanded(not self._expanded))
        self.list_widget.itemActivated.connect(self._on_item_activated)

        self._update_toggle_text()

    def _on_item_activated(self, item):
        self.track_activated.emit(self.list_widget.row(item))

    def set_expanded(self, expanded):
        self._expanded = expanded
        self._animation.stop()
        self._animation.setStartValue(self.list_panel.maximumHeight())
        self._animation.setEndValue(self.EXPANDED_HEIGHT if expanded else 0)
        self._animation.start()
        self._update_toggle_text()
        self.expanded_changed.emit(expanded)

    def populate(self, tracks):
        self.list_widget.clear()
        for index, track_info in enumerate(tracks):
            name = os.path.basename(track_info['path'])
            self.list_widget.addItem(f"{index + 1}. {name}")
        self._track_count = len(tracks)
        self._update_toggle_text()

    def highlight_current(self, index):
        self.list_widget.setCurrentRow(index)

    def _update_toggle_text(self):
        chevron = "▾" if self._expanded else "▸"
        self.toggle_button.setText(f"{chevron}  File d'attente · {self._track_count}")
