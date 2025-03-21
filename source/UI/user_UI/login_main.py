import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_login_mainwindow import Ui_MainWindow
from registermain import RegisterWindow 

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        
        self.ui.label_4.mousePressEvent = self.open_register_window 
    def open_register_window(self, event):
        self.register_window = RegisterWindow()  
        self.register_window.show()  
        self.close()   

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
