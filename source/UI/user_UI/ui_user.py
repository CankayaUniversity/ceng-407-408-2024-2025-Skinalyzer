import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QFrame, QFileDialog,
                              QScrollArea, QSizePolicy)
from PySide6.QtGui import QPixmap, QFont, QIcon, QColor, QImage
from PySide6.QtCore import Qt, QSize

# Validator modülünü içe aktarın
from skin_lesion_validator import SkinLesionValidator

class SkinalyzerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SKINALYZER")
        self.setMinimumSize(800, 600)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #f5e1ea, stop:1 #e8c1d8);
            }
            QWidget {
                background-color: #F8EBF4;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: white;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #8a4a64;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.uploaded_image = None
        
        # Validator'ü başlat ve referans veri setini yükle
        self.validator = SkinLesionValidator()
        folder1 = r"C:\Users\Dell\Desktop\ham10000_dataset\HAM10000_images_part_1"
        folder2 = r"C:\Users\Dell\Desktop\ham10000_dataset\HAM10000_images_part_2"
        self.validator.load_reference_dataset([folder1, folder2])
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)  
        
        header = self.create_header()
        main_layout.addWidget(header)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(50, 30, 50, 30)
        content_layout.setSpacing(20)
        
        self.info_card = self.create_info_card()
        self.history_card = self.create_history_card()
        
        content_layout.addWidget(self.info_card)
        content_layout.addWidget(self.history_card)
        content_layout.addSpacing(20)
        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        self.setCentralWidget(central_widget)
    
    def create_header(self):
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("background-color: #8a4a64;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
      
        logo_layout = QHBoxLayout()
        logo = QLabel()
        logo.setFixedSize(40, 40)
        logo.setStyleSheet("background-color: #ffffff; border-radius: 20px;")
        logo_layout.addWidget(logo)
        
        title = QLabel("SKINALYZER")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        logo_layout.addWidget(title)
        
        menu_layout = QHBoxLayout()
        about_btn = QPushButton("about us")
        contact_btn = QPushButton("contact")
        profile_btn = QPushButton("profile")
        
        about_btn.clicked.connect(self.show_about)
        contact_btn.clicked.connect(self.show_contact)
        profile_btn.clicked.connect(self.show_profile)
        
        for btn in [about_btn, contact_btn, profile_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
        
        profile_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        
        menu_layout.addWidget(about_btn)
        menu_layout.addWidget(contact_btn)
        menu_layout.addWidget(profile_btn)
        menu_layout.setSpacing(20)
        
        header_layout.addLayout(logo_layout)
        header_layout.addStretch()
        header_layout.addLayout(menu_layout)
        return header
    
    def create_info_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        left_content = QVBoxLayout()
        
        title_label = QLabel("SKINALYZER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black;")
        
        subtitle_label = QLabel("Skinalyzer: AI-Based Skin Cancer Detection System")
        subtitle_label.setStyleSheet("font-size: 17px; font-weight: bold; color: black;")
        subtitle_label.setWordWrap(True)
        
        description_label = QLabel(
            "'Skinalyzer' evaluates symptoms on your skin and assists "
            "in early disease diagnosis through the power of "
            "innovative artificial intelligence (AI) skin technology."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 14px; margin-top: 15px; color: black;")
        
        warning_label = QLabel("Make sure to consult your doctor without delay.")
        warning_label.setStyleSheet("font-size: 14px; margin-top: 15px; color: black;")
        
        upload_button = QPushButton("UPLOAD PHOTO")
        upload_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
                width: 150px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        upload_button.clicked.connect(self.browse_image)
        
        self.image_label = QLabel()
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 250)
        self.image_label.setMaximumSize(200, 200)
        
        self.analyze_button = QPushButton("ANALYZE")
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #8a4a64;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #703a50;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_image)
        
        left_content.addWidget(title_label)
        left_content.addWidget(subtitle_label)
        left_content.addWidget(description_label)
        left_content.addWidget(warning_label)
        left_content.addSpacing(20)
        left_content.addWidget(upload_button)
        left_content.addWidget(self.image_label)
        left_content.addSpacing(10)
        left_content.addWidget(self.analyze_button)
        
        # Layout for displaying analysis results
        self.results_layout = QVBoxLayout()
        left_content.addLayout(self.results_layout)
        left_content.addStretch()
        
        # Right side content (e.g. a static image)
        right_content = QVBoxLayout()
        self.image_label2 = QLabel()
        pixmap = QPixmap("C:\\Users\\user\\OneDrive\\Masaüstü\\Ekran görüntüsü 2025-03-10 212056.png")
        self.image_label2.setPixmap(pixmap)
        self.image_label2.setScaledContents(True)
        right_content.addWidget(self.image_label2)
        right_content.addSpacing(10)
        right_content.addStretch()
        
        card_layout.addLayout(left_content, 1)
        card_layout.addLayout(right_content, 1)
        return card

    def create_history_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
            }
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        icon_label = QLabel()
        icon_label.setFixedSize(150, 150)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            background-color: #8a4a64;
            color: white;
            font-size: 14px;
            border-radius: 10px;
        """)
        icon_label.setText("History\nIcon")
        
        right_content = QVBoxLayout()
        right_content.setSpacing(0)
        
        text_label = QLabel("You can access your saved analyse history by clicking the button below.")
        text_label.setStyleSheet("font-size: 17px; color: black;")
        text_label.setAlignment(Qt.AlignCenter)
        
        show_button = QPushButton("SHOW PAST RESULTS")
        show_button.setStyleSheet("""
            QPushButton {
                background-color: #8a4a64;
                color: white;
                border-radius: 15px;
                padding: 10px;
                min-width: 150px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #703a50;
            }
        """)
        show_button.clicked.connect(self.show_history)
        
        self.history_items_container = QFrame()
        self.history_items_container.setStyleSheet("background-color: transparent;")
        self.history_items_layout = QVBoxLayout(self.history_items_container)
        self.history_items_layout.setContentsMargins(0, 10, 0, 0)
        self.history_items_container.hide() 
        
        right_content.addWidget(text_label)
        right_content.addSpacing(20)
        right_content.addWidget(show_button, 0, Qt.AlignCenter)
        right_content.addWidget(self.history_items_container)
        
        card_layout.addWidget(icon_label)
        card_layout.addSpacing(20)
        card_layout.addLayout(right_content, 1)
        return card
    
    def browse_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Skin Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.uploaded_image = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(pixmap)
                self.image_label.setStyleSheet("background-color: transparent; border-radius: 10px;")
                self.analyze_button.setEnabled(True)
    
    def analyze_image(self):
        if self.uploaded_image:
            # Show the uploaded image
            self.image_label.setPixmap(QPixmap(self.uploaded_image).scaled(
                300, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.image_label.setStyleSheet("""
                background-color: transparent; 
                border: 2px solid #4CAF50;
                border-radius: 10px;
            """)
            # Display "Analyzing..." message
            self.analyzing_label = QLabel("Analyzing...")
            self.analyzing_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
            self.results_layout.addWidget(self.analyzing_label)
            QApplication.processEvents()
            
            # İlk olarak validator ile cilt lezyonu olup olmadığını kontrol et
            is_valid, similarity, validation_message = self.validator.is_skin_lesion(self.uploaded_image)
            if not is_valid:
                self.results_layout.removeWidget(self.analyzing_label)
                self.analyzing_label.deleteLater()
                self.analyzing_label = None
                error_label = QLabel(validation_message)
                error_label.setStyleSheet("color: red; font-weight: bold;")
                self.results_layout.addWidget(error_label)
                return
            
            # Eğer validator uygunluk onayı verdiyse, predict_model çalıştır
            from predict_model import predict_model as run_prediction
            try:
                result = run_prediction(self.uploaded_image)
            except Exception as e:
                error_label = QLabel("Model error: " + str(e))
                self.results_layout.addWidget(error_label)
                self.results_layout.removeWidget(self.analyzing_label)
                self.analyzing_label.deleteLater()
                self.analyzing_label = None
                return

            # Extract prediction results
            predicted_class = result["predicted_class"]
            confidence = result["confidence"]
            risk_level = result["risk_level"]
            lesion_description = result["lesion_description"]

            # Remove "Analyzing..." message and clear previous results
            self.results_layout.removeWidget(self.analyzing_label)
            self.analyzing_label.deleteLater()
            self.analyzing_label = None

            while self.results_layout.count() > 0:
                item = self.results_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

            # Display the results
            results_header = QLabel("Analysis Results")
            results_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")

            class_label = QLabel("Predicted Class: " + predicted_class)
            class_label.setStyleSheet("""
                background-color: #e8f5e9;
                color: #2e7d32;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 5px;
            """)

            confidence_label = QLabel("Confidence Score: {:.2f}%".format(confidence))
            confidence_label.setStyleSheet("margin-top: 5px;")

            risk_label = QLabel("Risk Level: " + risk_level)
            risk_label.setStyleSheet("margin-top: 5px; font-weight: bold;")

            description_label = QLabel("Lesion Description: " + lesion_description)
            description_label.setWordWrap(True)
            description_label.setStyleSheet("margin-top: 5px;")

            self.results_layout.addWidget(results_header)
            self.results_layout.addWidget(class_label)
            self.results_layout.addWidget(confidence_label)
            self.results_layout.addWidget(risk_label)
            self.results_layout.addWidget(description_label)

            self.analyze_button.setText("ANALYZED")
            self.analyze_button.setEnabled(False)
            self.add_to_history()
    
    def add_to_history(self):
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        history_item = QFrame()
        history_item.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border-radius: 8px;
                margin-top: 5px;
            }
        """)
        
        item_layout = QHBoxLayout(history_item)
        
        thumbnail = QLabel()
        if self.uploaded_image:
            pixmap = QPixmap(self.uploaded_image).scaled(
                50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            thumbnail.setPixmap(pixmap)
        thumbnail.setFixedSize(50, 50)
        thumbnail.setStyleSheet("background-color: #8a4a64; border-radius: 5px;")
        
        details = QLabel(f"Analysis - {current_time}\nRisk Level: Low")
        details.setStyleSheet("font-size: 12px;")
        
        item_layout.addWidget(thumbnail)
        item_layout.addWidget(details)
        item_layout.addStretch()
        
        self.history_items_layout.addWidget(history_item)
    
    def show_history(self):
        if self.history_items_container.isHidden():
            if self.history_items_layout.count() == 0:
                no_history = QLabel("No previous analyses found.")
                no_history.setStyleSheet("""
                    background-color: #e0e0e0;
                    padding: 10px;
                    border-radius: 5px;
                """)
                self.history_items_layout.addWidget(no_history)
            self.history_items_container.show()
        else:
            self.history_items_container.hide()
    
    def show_about(self):
        about_frame = QFrame(self)
        about_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #8a4a64;
            }
        """)
        about_frame.setGeometry(100, 100, 600, 400)
        about_layout = QVBoxLayout(about_frame)
        title = QLabel("About Skinalyzer")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        content = QLabel(
            "Skinalyzer is an AI-powered tool designed to help with the early detection "
            "of skin conditions and potential cancer indicators.\n\n"
            "Our mission is to make skin health accessible to everyone through innovative "
            "technology and artificial intelligence.\n\n"
            "Note: This is a demonstration application and not intended for medical use."
        )
        content.setWordWrap(True)
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #8a4a64;
                color: white;
                border-radius: 10px;
                padding: 10px;
                min-width: 100px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #703a50;
            }
        """)
        close_btn.clicked.connect(about_frame.close)
        about_layout.addWidget(title)
        about_layout.addWidget(content)
        about_layout.addStretch()
        about_layout.addWidget(close_btn, 0, Qt.AlignCenter)
        about_frame.show()
    
    def show_contact(self):
        print("Contact clicked")
    
    def show_profile(self):
        print("Profile clicked")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SkinalyzerUI()
    window.show()
    sys.exit(app.exec())
