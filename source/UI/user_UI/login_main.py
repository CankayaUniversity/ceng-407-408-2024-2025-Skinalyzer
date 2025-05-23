import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
from ui_login_mainwindow import Ui_MainWindow
from registermain import RegisterWindow 

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.label_4.mousePressEvent = self.open_register_window
        
        self.ui.email.returnPressed.connect(self.ui.loginfunction)
        self.ui.password.returnPressed.connect(self.ui.loginfunction)
    
    def open_register_window(self, event):
        self.register_window = RegisterWindow()  
        self.register_window.show()  
        self.close()   
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            focused_widget = QApplication.focusWidget()
            if focused_widget in (self.ui.email, self.ui.password):
                self.ui.loginfunction()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())