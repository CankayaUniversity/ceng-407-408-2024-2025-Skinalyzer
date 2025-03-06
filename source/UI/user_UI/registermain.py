from PySide6.QtWidgets import QMainWindow
from ui_register_mainwindow import Ui_RegisterWindow  # Register UI dosyanı içe aktar

class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_RegisterWindow()
        self.ui.setupUi(self)
