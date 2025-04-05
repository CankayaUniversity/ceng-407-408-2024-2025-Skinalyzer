from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class DetailsWindow(QDialog):  
    def __init__(self, result):
        super().__init__()
        self.setWindowTitle("Analiz Detayları")
        self.setMinimumSize(600, 400)
        self.setWindowModality(Qt.ApplicationModal) 
        
       
        layout = QVBoxLayout(self)
        
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)  
        image_pixmap = QPixmap(result['image_path'])
        if not image_pixmap.isNull():
            image_pixmap = image_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(image_pixmap)
        else:
            image_label.setText("Görsel yüklenemedi")
        layout.addWidget(image_label)

        detail_text = (
            f"<b>Predicted Class:</b> {result['predicted_class']}<br>"
            f"<b>Risk Level</b> {result['risk_level']}<br>"
            f"<b>Confidence:</b> %{result['confidence']}<br>"
            f"<b>Description</b> {result['description']}<br>"
            f"<b>Date:</b> {result['date']}"
        )
        detail_label = QLabel(detail_text)
        detail_label.setWordWrap(True)
        detail_label.setStyleSheet("margin: 10px; font-size: 14px;")
        layout.addWidget(detail_label)

        # Back button
        back_button = QPushButton("Go Back")
        back_button.setStyleSheet("""
            background-color: #9D5171; 
            color: white; 
            border-radius: 5px; 
            padding: 8px 15px; 
            font-weight: bold;
        """)
        back_button.clicked.connect(self.accept)  
        layout.addWidget(back_button)