from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, *args, **kwargs):
        if args[1] == Qt.DisplayRole:
            value = self._data.iloc[args[0].row(), args[0].column()]
            return str(value)
        elif args[1] == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def rowCount(self, *args, **kwargs):
        return self._data.shape[0]

    def columnCount(self, *args, **kwargs):
        return self._data.shape[1]

    def headerData(self, *args, **kwargs):
        if args[2] == Qt.DisplayRole:
            if args[1] == Qt.Horizontal:
                return str(self._data.columns[args[0]])

            if args[1] == Qt.Vertical:
                return str(self._data.index[args[0]])
