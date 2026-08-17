# src/gui/gui_widgets.py
# Widgets custom PySide6, un cran par morceau d'UI (pochette+infos, progression,
# contrôles, volume, playlist repliable). Chaque widget expose ses propres
# signaux Qt ; le câblage vers MusicPlayer se fait dans music_app_gui.py.
#
# Le rendu « néon » repose sur deux mécanismes complémentaires :
# - theme.apply_glow() (QGraphicsDropShadowEffect non décalé) pour les halos
#   d'un widget entier — un seul effet possible par widget ;
# - des paintEvent multi-passes en CompositionMode_Plus (lumière additive)
#   quand il faut plusieurs couches de halo ou un cœur d'une autre couleur
#   que le halo (sliders, barre d'accent de la playlist, équaliseur).

import math
import os
import re

from PySide6.QtCore import (
    Qt, Signal, Property, QRectF, QSize,
    QPropertyAnimation, QVariantAnimation, QEasingCurve,
)
from PySide6.QtGui import (
    QColor, QFont, QPainter, QPainterPath, QPen, QPixmap, QLinearGradient,
)
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QStyle, QStyledItemDelegate,
    QSizePolicy,
)

from src.gui import theme
from src.time_format import format_time


def clean_display_title(track_info):
    """Titre présentable : métadonnées si possible, sinon nom de fichier nettoyé
    (préfixe numérique de piste retiré, underscores remplacés par des espaces)."""
    title = (track_info.get('metadata', {}).get('title') or "").strip()
    if not title:
        title = os.path.splitext(os.path.basename(track_info['path']))[0]
    title = re.sub(r"^\s*\d+\s*[-._ ]+", "", title)
    title = title.replace("_", " ").strip()
    return title or os.path.splitext(os.path.basename(track_info['path']))[0]


class NeonSlider(QSlider):
    """
    Slider horizontal peint main : rail sombre, remplissage en dégradé
    deep→saturé avec halo additif, cœur clair, poignée à cœur blanc dont le
    halo (et la taille, animée) marquent le glissement. Un clic sur le rail
    saute directement à la position cliquée.

    Le QSS est volontairement abandonné pour ce widget : il ne sait ni peindre
    un halo, ni donner au cœur une couleur différente du remplissage.
    """

    _H_PAD = 10  # marge horizontale : la poignée et son halo doivent tenir

    def __init__(self, core, glow, deep, min_height=26, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self._core = QColor(core)
        self._glow = QColor(glow)
        self._deep = QColor(deep)
        self._handle_scale = 1.0
        # Agrandir la poignée ne change pas le minimumSizeHint d'un QSlider
        # (vérifié : il reste à 16 px) — sans ceci, poignée et halo sont rognés.
        self.setMinimumHeight(min_height)

        self._scale_anim = QPropertyAnimation(self, b"handle_scale", self)
        self._scale_anim.setDuration(130)
        self._scale_anim.setEasingCurve(QEasingCurve.OutCubic)

    def _get_handle_scale(self):
        return self._handle_scale

    def _set_handle_scale(self, value):
        self._handle_scale = value
        self.update()

    handle_scale = Property(float, _get_handle_scale, _set_handle_scale)

    def _animate_handle(self, target):
        self._scale_anim.stop()
        self._scale_anim.setStartValue(self._handle_scale)
        self._scale_anim.setEndValue(target)
        self._scale_anim.start()

    def _value_at(self, x):
        span = max(1, self.width() - 2 * self._H_PAD)
        fraction = min(1.0, max(0.0, (x - self._H_PAD) / span))
        return round(self.minimum() + fraction * (self.maximum() - self.minimum()))

    # Gestion souris entièrement réimplémentée (pas de super()) : le style natif
    # calcule ses positions sur ses propres métriques, pas sur notre rendu.
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setSliderDown(True)  # émet sliderPressed
            self.setSliderPosition(self._value_at(event.position().x()))
            self._animate_handle(1.4)
            event.accept()

    def mouseMoveEvent(self, event):
        if self.isSliderDown():
            self.setSliderPosition(self._value_at(event.position().x()))
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.isSliderDown():
            self.setSliderPosition(self._value_at(event.position().x()))
            self.setSliderDown(False)  # émet sliderReleased
            self._animate_handle(1.0)
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        mid_y = self.height() / 2
        left = float(self._H_PAD)
        span = max(1.0, self.width() - 2.0 * self._H_PAD)

        rail = QRectF(left, mid_y - 2.5, span, 5.0)
        painter.setPen(QPen(QColor(30, 44, 32), 1.0))
        painter.setBrush(QColor(14, 20, 14))
        painter.drawRoundedRect(rail, 2.5, 2.5)
        painter.setPen(Qt.NoPen)

        span_range = self.maximum() - self.minimum()
        fraction = (self.value() - self.minimum()) / span_range if span_range > 0 else 0.0
        fill_w = span * fraction

        if fill_w > 2:
            fill = QRectF(left, mid_y - 2.5, fill_w, 5.0)

            gradient = QLinearGradient(fill.topLeft(), fill.topRight())
            gradient.setColorAt(0.0, self._deep)
            gradient.setColorAt(1.0, self._glow)
            painter.setBrush(gradient)
            painter.drawRoundedRect(fill, 2.5, 2.5)

            # Halo du remplissage : passes additives, du large au serré.
            painter.setCompositionMode(QPainter.CompositionMode_Plus)
            for spread, alpha in ((5.0, 22), (2.5, 40)):
                halo_color = QColor(self._glow)
                halo_color.setAlpha(alpha)
                painter.setBrush(halo_color)
                painter.drawRoundedRect(fill.adjusted(-spread, -spread, spread, spread),
                                        2.5 + spread, 2.5 + spread)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            # Cœur quasi blanc du tube, au milieu du remplissage.
            if fill_w > 14:
                core_color = QColor(self._core)
                core_color.setAlpha(215)
                painter.setPen(QPen(core_color, 1.4, Qt.SolidLine, Qt.RoundCap))
                painter.drawLine(QRectF(left + 3, mid_y, fill_w - 8, 0).topLeft(),
                                 QRectF(left + 3, mid_y, fill_w - 8, 0).bottomRight())

        # Poignée : halo radial additif + cœur blanc.
        handle_x = left + fill_w
        radius = 4.6 * self._handle_scale
        painter.setPen(Qt.NoPen)
        painter.setCompositionMode(QPainter.CompositionMode_Plus)
        for extra, alpha in ((7.0, 46), (3.5, 90)):
            halo_color = QColor(self._glow)
            halo_color.setAlpha(alpha)
            painter.setBrush(halo_color)
            painter.drawEllipse(QRectF(handle_x - radius - extra, mid_y - radius - extra,
                                       2 * (radius + extra), 2 * (radius + extra)))
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(QRectF(handle_x - radius, mid_y - radius, 2 * radius, 2 * radius))


class AlbumArtWidget(QWidget):
    """
    Pochette 88 px : carré arrondi à bordure verte, note ♪ par défaut,
    fondu enchaîné (paint main, propriété `blend` animée) au changement.
    Le halo extérieur est posé par NowPlayingWidget via theme.apply_glow().
    """

    SIZE = 88
    RADIUS = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)
        self._cover = None        # QPixmap recadrée, ou None → placeholder ♪
        self._previous_frame = None  # instantané du rendu précédent, pour le fondu
        self._blend = 1.0

        self._blend_anim = QPropertyAnimation(self, b"blend", self)
        self._blend_anim.setDuration(260)
        self._blend_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._blend_anim.setStartValue(0.0)
        self._blend_anim.setEndValue(1.0)

    def _get_blend(self):
        return self._blend

    def _set_blend(self, value):
        self._blend = value
        self.update()

    blend = Property(float, _get_blend, _set_blend)

    def set_cover(self, cover_bytes):
        new_cover = None
        if cover_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(cover_bytes):
                ratio = self.devicePixelRatioF()
                size = round(self.SIZE * ratio)
                scaled = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding,
                                       Qt.SmoothTransformation)
                x = max(0, (scaled.width() - size) // 2)
                y = max(0, (scaled.height() - size) // 2)
                new_cover = scaled.copy(x, y, size, size)
                new_cover.setDevicePixelRatio(ratio)

        self._previous_frame = self.grab()  # rendu actuel, bordure comprise
        self._cover = new_cover
        self._blend_anim.stop()
        self._blend_anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        outer = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(outer, self.RADIUS, self.RADIUS)

        painter.save()
        painter.setClipPath(path)
        if self._cover is not None:
            painter.drawPixmap(self.rect(), self._cover)
        else:
            painter.fillRect(self.rect(), QColor("#0a120c"))
            note_font = QFont(theme.FONT_FAMILY)
            note_font.setPixelSize(34)
            painter.setFont(note_font)
            painter.setPen(QColor(theme.GREEN))
            painter.drawText(self.rect(), Qt.AlignCenter, "♪")
        painter.restore()

        # Bordure verte + léger bloom intérieur additif.
        painter.setPen(QPen(QColor(theme.GREEN), 2.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(outer, self.RADIUS, self.RADIUS)
        painter.setCompositionMode(QPainter.CompositionMode_Plus)
        inner_glow = QColor(theme.GREEN)
        inner_glow.setAlpha(55)
        painter.setPen(QPen(inner_glow, 4.0))
        painter.drawRoundedRect(outer.adjusted(2, 2, -2, -2),
                                self.RADIUS - 2, self.RADIUS - 2)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Fondu enchaîné : l'ancien rendu s'estompe par-dessus le nouveau.
        if self._blend < 1.0 and self._previous_frame is not None:
            painter.setOpacity(1.0 - self._blend)
            painter.drawPixmap(self.rect(), self._previous_frame)


class NowPlayingWidget(QWidget):
    """Cadre « en cours de lecture » : pochette à gauche, infos morceau à droite."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("nowPlayingPanel")
        # Un QWidget brut ne peint pas background/border du QSS sans cet attribut.
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(13)

        self.album_art = AlbumArtWidget()
        layout.addWidget(self.album_art)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        self.track_label = QLabel()
        self.track_label.setObjectName("trackLabel")
        self.track_label.setWordWrap(False)

        self.artist_label = QLabel()
        self.artist_label.setObjectName("artistLabel")

        self.album_label = QLabel()
        self.album_label.setObjectName("albumLabel")

        # Largeur en politique Ignored : sous SetFixedSize, un label non tronqué
        # imposerait sinon sa largeur naturelle à toute la fenêtre (le sizeHint
        # est lu avant que l'élision n'ait eu lieu). Ici ils prennent la place
        # que le layout leur donne, et _refresh_title() élide dedans.
        for label in (self.track_label, self.artist_label, self.album_label):
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        # Un stretch de chaque côté : le bloc reste centré sur la hauteur de la
        # pochette quelle que soit la longueur du titre.
        info_layout.addStretch()
        info_layout.addWidget(self.track_label)
        info_layout.addWidget(self.artist_label)
        info_layout.addWidget(self.album_label)
        info_layout.addStretch()

        layout.addLayout(info_layout, stretch=1)

        self._full_title = ""

        theme.apply_glow(self.track_label, theme.GREEN, theme.GLOW_TITLE, alpha=200)
        theme.apply_glow(self.artist_label, theme.ORANGE, theme.GLOW_ARTIST, alpha=190)
        theme.apply_glow(self.album_art, theme.GREEN, theme.GLOW_ART, alpha=160)

        self.set_track_info("Aucune musique chargée", "Artiste inconnu", "Album inconnu")

    def set_track_info(self, title, artist, album):
        self._full_title = title.upper()
        self._refresh_title()
        self.artist_label.setText(artist.upper())
        self.album_label.setText(album.upper())

    def _refresh_title(self):
        """Élide le titre sur une ligne : un retour à la ligne ferait varier la
        hauteur de la fenêtre (SetFixedSize) à chaque changement de morceau."""
        available = self.track_label.width()
        if available < 40:  # avant le premier layout, largeur non significative
            self.track_label.setText(self._full_title)
            return
        metrics = self.track_label.fontMetrics()
        self.track_label.setText(
            metrics.elidedText(self._full_title, Qt.ElideRight, available)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_title()

    def set_cover(self, cover_bytes):
        self.album_art.set_cover(cover_bytes)


class ProgressWidget(QWidget):
    """Temps écoulé + barre de progression néon + temps total."""

    seek_previewed = Signal(int)   # position (ms) pendant le glissement
    seek_committed = Signal(int)   # position (ms) au relâchement

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.current_time_label = QLabel("00:00")
        self.current_time_label.setObjectName("timeLabel")

        self.slider = NeonSlider(theme.GREEN_CORE, theme.GREEN, theme.GREEN_DEEP,
                                 min_height=28)
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


class GlowButton(QPushButton):
    """QPushButton dont le halo (blurRadius) s'anime au survol et à l'appui —
    le QSS n'ayant pas de transition, l'animation passe par QPropertyAnimation."""

    def __init__(self, text, glow_color, idle_radius, hover_radius,
                 alpha=200, animate_hover=True, parent=None):
        super().__init__(text, parent)
        self.glow = theme.apply_glow(self, glow_color, idle_radius, alpha)
        self._idle_radius = idle_radius
        self._hover_radius = hover_radius
        self._animate_hover = animate_hover

        self._glow_anim = QPropertyAnimation(self.glow, b"blurRadius", self)
        self._glow_anim.setDuration(140)
        self._glow_anim.setEasingCurve(QEasingCurve.OutCubic)

    def _animate_glow(self, target):
        self._glow_anim.stop()
        self._glow_anim.setStartValue(self.glow.blurRadius())
        self._glow_anim.setEndValue(target)
        self._glow_anim.start()

    def enterEvent(self, event):
        if self._animate_hover:
            self._animate_glow(self._hover_radius)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._animate_hover:
            self._animate_glow(self._idle_radius)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._animate_hover:
            self.glow.setBlurRadius(self._hover_radius + 10)  # flash d'appui
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._animate_hover:
            target = self._hover_radius if self.underMouse() else self._idle_radius
            self._animate_glow(target)
        super().mouseReleaseEvent(event)


class ControlsWidget(QWidget):
    """Boutons de transport : Précédent / Play-Pause / Suivant."""

    prev_clicked = Signal()
    play_pause_clicked = Signal()
    next_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        # Marges verticales : la place du halo (rogné sinon par ce widget parent).
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignCenter)

        # ◀◀/▶▶/▮▮ plutôt que ⏮/⏭/⏸ : ces derniers appartiennent à une plage
        # Unicode que Windows restyle en icônes couleur "Fluent", ce qui écrase
        # entièrement le QSS (fond bleu opaque au lieu du style néon).
        self.prev_button = GlowButton("◀◀", theme.ORANGE, 8, theme.GLOW_SIDE_HOVER,
                                      alpha=170)
        self.prev_button.setObjectName("sideControlButton")
        self.prev_button.setFixedSize(42, 42)

        self.play_pause_button = GlowButton("▶", theme.GREEN, theme.GLOW_PLAY_IDLE,
                                            theme.GLOW_PLAY_IDLE, alpha=200,
                                            animate_hover=False)
        self.play_pause_button.setObjectName("playPauseButton")
        self.play_pause_button.setFixedSize(62, 62)

        self.next_button = GlowButton("▶▶", theme.ORANGE, 8, theme.GLOW_SIDE_HOVER,
                                      alpha=170)
        self.next_button.setObjectName("sideControlButton")
        self.next_button.setFixedSize(42, 42)

        for button in (self.prev_button, self.play_pause_button, self.next_button):
            button.setCursor(Qt.PointingHandCursor)
            layout.addWidget(button)

        # Respiration du bouton lecture pendant la lecture (1600 ms, sinusoïdale).
        self._pulse = QPropertyAnimation(self.play_pause_button.glow, b"blurRadius", self)
        self._pulse.setDuration(1600)
        self._pulse.setStartValue(theme.GLOW_PLAY_IDLE)
        self._pulse.setKeyValueAt(0.5, theme.GLOW_PLAY_PULSE)
        self._pulse.setEndValue(theme.GLOW_PLAY_IDLE)
        self._pulse.setEasingCurve(QEasingCurve.InOutSine)
        self._pulse.setLoopCount(-1)

        self.prev_button.clicked.connect(self.prev_clicked)
        self.play_pause_button.clicked.connect(self.play_pause_clicked)
        self.next_button.clicked.connect(self.next_clicked)

    def set_playing(self, is_playing):
        self.play_pause_button.setText("▮▮" if is_playing else "▶")
        if is_playing:
            if self._pulse.state() != QPropertyAnimation.Running:
                self._pulse.start()
        else:
            self._pulse.stop()
            self.play_pause_button.glow.setBlurRadius(theme.GLOW_PLAY_IDLE)


class _SpeakerIcon(QWidget):
    """Icône haut-parleur peinte : les ondes s'allument selon le niveau."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 16)
        self._level = 50
        theme.apply_glow(self, theme.ORANGE, 10, alpha=140)

    def set_level(self, level):
        self._level = level
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        body = QPainterPath()
        body.moveTo(1, 5.5)
        body.lineTo(5, 5.5)
        body.lineTo(9, 2)
        body.lineTo(9, 14)
        body.lineTo(5, 10.5)
        body.lineTo(1, 10.5)
        body.closeSubpath()
        body_color = QColor(theme.ORANGE_CORE)
        body_color.setAlpha(90 if self._level == 0 else 235)
        painter.fillPath(body, body_color)

        for radius, threshold in ((3.6, 1), (6.6, 55)):
            arc_color = QColor(theme.ORANGE)
            arc_color.setAlpha(235 if self._level >= threshold else 70)
            painter.setPen(QPen(arc_color, 1.6, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(QRectF(9.5 - radius, 8 - radius, 2 * radius, 2 * radius),
                            -50 * 16, 100 * 16)


class VolumeWidget(QWidget):
    """Icône haut-parleur + slider néon orange, centrés."""

    volume_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.icon = _SpeakerIcon()
        self.slider = NeonSlider(theme.ORANGE_CORE, theme.ORANGE, theme.ORANGE_DEEP,
                                 min_height=24)
        self.slider.setRange(0, 100)
        self.slider.setFixedWidth(180)

        # Stretch de part et d'autre : centre réellement la ligne (poser
        # Qt.AlignCenter sur le layout ne centre rien face à un enfant extensible).
        layout.addStretch()
        layout.addWidget(self.icon)
        layout.addWidget(self.slider)
        layout.addStretch()

        self.slider.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, value):
        self.icon.set_level(value)
        self.volume_changed.emit(value)

    def set_volume(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self.icon.set_level(value)


class _PlaylistDelegate(QStyledItemDelegate):
    """
    Rendu d'une ligne de playlist : titre nettoyé + durée à droite ; la ligne
    en cours de lecture porte une barre d'accent lumineuse et un mini-équaliseur
    animé. Un QGraphicsEffect ne s'appliquant pas à un item de vue, les halos
    sont peints ici en passes additives.
    """

    ROW_HEIGHT = 26

    TITLE_ROLE = Qt.UserRole
    DURATION_ROLE = Qt.UserRole + 1

    def __init__(self, owner):
        super().__init__(owner)
        self._owner = owner
        self._title_font = QFont(theme.FONT_FAMILY)
        self._title_font.setPixelSize(11)
        self._time_font = QFont()
        self._time_font.setFamilies(["Cascadia Mono", "Consolas"])
        self._time_font.setPixelSize(9)

    def sizeHint(self, option, index):
        return QSize(100, self.ROW_HEIGHT)

    def paint(self, painter, option, index):
        rect = option.rect
        row = index.row()
        is_current = row == self._owner.playing_row
        hovered = bool(option.state & QStyle.State_MouseOver)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        duration_color = QColor(theme.TEXT_MUTED)
        if is_current:
            wash = QLinearGradient(rect.left(), 0, rect.right(), 0)
            wash.setColorAt(0.0, QColor(13, 63, 30, 115))
            wash.setColorAt(1.0, QColor(13, 63, 30, 12))
            painter.fillRect(rect, wash)

            # Barre d'accent : halo additif puis cœur clair.
            bar = QRectF(rect.left(), rect.top() + 2, 3, rect.height() - 4)
            painter.setCompositionMode(QPainter.CompositionMode_Plus)
            for spread, alpha in ((6.0, 30), (2.5, 70)):
                halo_color = QColor(theme.GREEN)
                halo_color.setAlpha(alpha)
                painter.fillRect(bar.adjusted(0, -spread / 2, spread, spread / 2), halo_color)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.fillRect(bar, QColor(theme.GREEN_CORE))

            title_color = QColor(theme.GREEN_CORE)
            duration_color = QColor(theme.TIME_TEXT)
        elif hovered:
            painter.fillRect(rect, QColor(57, 255, 106, 13))
            title_color = QColor("#cfe3cf")
        else:
            title_color = QColor("#b8c8b8")

        painter.setFont(self._time_font)
        duration = index.data(self.DURATION_ROLE) or ""
        duration_width = painter.fontMetrics().horizontalAdvance(duration)
        duration_rect = QRectF(rect.right() - duration_width - 12, rect.top(),
                               duration_width, rect.height())
        painter.setPen(duration_color)
        painter.drawText(duration_rect, Qt.AlignVCenter | Qt.AlignRight, duration)

        text_right = duration_rect.left() - 8

        if is_current:
            text_right -= 24
            self._paint_equalizer(painter, QRectF(text_right + 4, rect.top(), 20, rect.height()))

        painter.setFont(self._title_font)
        title = index.data(self.TITLE_ROLE) or ""
        text_rect = QRectF(rect.left() + 14, rect.top(),
                           max(10, text_right - rect.left() - 14), rect.height())
        elided = painter.fontMetrics().elidedText(title, Qt.ElideRight,
                                                  int(text_rect.width()))
        painter.setPen(title_color)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, elided)

        painter.restore()

    def _paint_equalizer(self, painter, zone):
        """3 barres verticales ; animées si lecture en cours, figées en pause."""
        phase = self._owner.eq_phase if self._owner.is_playing else None
        mid_y = zone.center().y()
        for i, offset in enumerate((0.0, 0.33, 0.66)):
            if phase is None:
                height = (5.0, 8.0, 6.0)[i]
            else:
                height = 3.0 + 9.0 * abs(math.sin(2 * math.pi * (phase + offset)))
            bar = QRectF(zone.left() + i * 6, mid_y - height / 2, 3, height)
            painter.setCompositionMode(QPainter.CompositionMode_Plus)
            halo_color = QColor(theme.GREEN)
            halo_color.setAlpha(60)
            painter.fillRect(bar.adjusted(-1.5, -1.5, 1.5, 1.5), halo_color)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.fillRect(bar, QColor(theme.GREEN))


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
        # Nécessaire pour l'état survolé (State_MouseOver) dans le delegate.
        self.list_widget.viewport().setMouseTracking(True)
        panel_layout.addWidget(self.list_widget)

        outer.addWidget(self.list_panel)

        self._expanded = True
        self._track_count = 0

        # État lu par le delegate : ligne en lecture ≠ sélection au clic.
        self.playing_row = -1
        self.is_playing = False
        self.eq_phase = 0.0

        self.list_widget.setItemDelegate(_PlaylistDelegate(self))

        self._eq_anim = QVariantAnimation(self)
        self._eq_anim.setStartValue(0.0)
        self._eq_anim.setEndValue(1.0)
        self._eq_anim.setDuration(900)
        self._eq_anim.setLoopCount(-1)
        self._eq_anim.valueChanged.connect(self._on_eq_tick)

        self._animation = QPropertyAnimation(self.list_panel, b"maximumHeight", self)
        self._animation.setDuration(220)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

        self.toggle_button.clicked.connect(lambda: self.set_expanded(not self._expanded))
        self.list_widget.itemActivated.connect(self._on_item_activated)

        self._update_toggle_text()

    def _on_eq_tick(self, value):
        self.eq_phase = value
        self.list_widget.viewport().update()

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
        for track_info in tracks:
            item = QListWidgetItem()
            item.setData(_PlaylistDelegate.TITLE_ROLE, clean_display_title(track_info))
            item.setData(_PlaylistDelegate.DURATION_ROLE,
                         format_time(track_info.get('duration_ms') or 0))
            self.list_widget.addItem(item)
        self._track_count = len(tracks)
        self._update_toggle_text()

    def highlight_current(self, index):
        self.playing_row = index
        self.list_widget.setCurrentRow(index)
        self.list_widget.viewport().update()

    def set_playing(self, is_playing):
        """Anime l'équaliseur de la ligne courante pendant la lecture."""
        self.is_playing = is_playing
        if is_playing:
            if self._eq_anim.state() != QVariantAnimation.Running:
                self._eq_anim.start()
        else:
            self._eq_anim.stop()
            self.list_widget.viewport().update()

    def _update_toggle_text(self):
        chevron = "▾" if self._expanded else "▸"
        self.toggle_button.setText(f"{chevron}  FILE D'ATTENTE · {self._track_count}")
