import sys
from PySide6.QtWidgets import QApplication, QWidget
from ui_user import Ui_Widget

class UserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = UserWidget()
    widget.show()
    sys.exit(app.exec())

