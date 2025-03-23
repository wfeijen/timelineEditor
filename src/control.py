import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget
from PyQt5.QtGui import QKeyEvent

class KeyboardEventApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Keyboard Event Example")
        self.setGeometry(100, 100, 800, 200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.key_label = QLabel("Last Key Pressed: None", self.central_widget)
        self.key_label.setGeometry(10, 10, 600, 30)

    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent):
            key_text = event.text()
            key_nr = str(event.key())
            ret = f"Last Key Pressed: nr: {key_nr} _  {key_text} "
            print(ret)

    def keyReleaseEvent(self, event):
        if isinstance(event, QKeyEvent):
            key_text = event.text()
            key_nr = str(event.key())
            ret = f"Key Released: nr: {key_nr} _ {key_text} "
            print(ret)

def main():
    app = QApplication(sys.argv)
    window = KeyboardEventApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()