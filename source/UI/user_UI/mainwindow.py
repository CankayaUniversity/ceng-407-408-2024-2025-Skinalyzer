import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_mainwindow import Ui_MainWindow
from registermain import RegisterWindow  # Register penceresini içe aktar

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Register penceresini açmak için
        self.ui.label_4.mousePressEvent = self.open_register_window  # Tıklama olayını yakala

    def open_register_window(self, event):
        self.register_window = RegisterWindow()  # Yeni bir RegisterWindow nesnesi oluştur
        self.register_window.show()  # Pencereyi göster
        self.close()  # Login penceresini kapat (isteğe bağlı)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
