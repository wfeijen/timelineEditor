import sys
from PyQt5.QtWidgets import QtCore, QtWidgets

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.dateedit = QtWidgets.QDateEdit(calendarPopup=True)
        # self.menuBar().setCornerWidget(self.dateedit, QtCore.Qt.TopLeftCorner)
        self.menuBar().setCornerWidget(self.dateedit, QtCore.Qt.Corner.TopLeftCorner)
        self.dateedit.setDateTime(QtCore.QDateTime.currentDateTime())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    # sys.exit(app.exec_())
    sys.exit(app.exec())