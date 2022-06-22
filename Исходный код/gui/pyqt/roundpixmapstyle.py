from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt


class RoundPixmapStyle(QtWidgets.QProxyStyle):
    def __init__(self, radius=10, *args, **kwargs):
        super(RoundPixmapStyle, self).__init__(*args, **kwargs)
        self._radius = radius

    def drawItemPixmap(self, painter, rectangle, alignment, pixmap):
        painter.save()
        pix = QtGui.QPixmap(pixmap.size())
        pix.fill(Qt.transparent)
        p = QtGui.QPainter(pix)
        p.setBrush(QtGui.QBrush(pixmap))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(pixmap.rect(), self._radius, self._radius)
        p.end()
        super(RoundPixmapStyle, self).drawItemPixmap(painter, rectangle, alignment, pix)
        painter.restore()
