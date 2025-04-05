import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QPushButton, QLabel, QFrame, QFileDialog,
                              QScrollArea, QSizePolicy,QDialog)
from PySide6.QtGui import QPixmap, QFont, QIcon, QColor, QImage
from PySide6.QtCore import Qt, QSize
import mysql.connector
from result import AnalysisResultsWindow
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from login_main import MainWindow  

from skin_lesion_validator import SkinLesionValidator 

class SkinalyzerUI(QMainWindow):
    def __init__(self,user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("SKINALYZER")
        self.setMinimumSize(1200, 600)
        
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
        
        self.validator = SkinLesionValidator()
        folder1 = r"C:\Users\user\OneDrive\Masaüstü\ham10000_dataset\HAM10000_images_part_1"
        folder2 = r"C:\Users\user\OneDrive\Masaüstü\ham10000_dataset\HAM10000_images_part_2"
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
        profile_btn = QPushButton("log out")
        
        about_btn.clicked.connect(self.show_about)
        contact_btn.clicked.connect(self.show_contact)
        profile_btn.clicked.connect(self.log_out)
        
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
                border:1px solid #A0A0A0;   
                color:black;                    
            }
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        left_content = QVBoxLayout()
        
        title_label = QLabel("SKINALYZER")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: black; border:none;")
        
        subtitle_label = QLabel("Skinalyzer: AI-Based Skin Cancer Detection System")
        subtitle_label.setStyleSheet("font-size: 17px; font-weight: bold; color: black; border:none;")
        subtitle_label.setWordWrap(True)
        
        description_label = QLabel(
            "'Skinalyzer' evaluates symptoms on your skin and assists "
            "in early disease diagnosis through the power of "
            "innovative artificial intelligence (AI) skin technology."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 14px; margin-top: 15px; color: black; border:none;")
        
        warning_label = QLabel("Make sure to consult your doctor without delay.")
        warning_label.setStyleSheet("font-size: 14px; margin-top: 15px; color: black; border:none;")
        
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
        upload_button.setFixedWidth(350)
        upload_button.setFixedHeight(60)
        upload_button.clicked.connect(self.browse_image)
        
        self.image_label = QLabel()
        self.image_label.setStyleSheet("background-color:transparent; border-radius: 10px; border: 1px solid #A0A0A0;")
        self.image_label.setMinimumSize(300, 250)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMaximumSize(200, 200)
        left_content.setSpacing(20)
        
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

        button_layout = QHBoxLayout()
        button_layout.addWidget(upload_button, alignment=Qt.AlignCenter)
        
        left_content.addWidget(title_label)
        left_content.addWidget(subtitle_label)
        left_content.addWidget(description_label)
        left_content.addWidget(warning_label)
        left_content.addSpacing(20)
        left_content.addLayout(button_layout)
        left_content.addWidget(self.image_label, alignment=Qt.AlignCenter)
        left_content.addSpacing(10)
        left_content.addWidget(self.analyze_button, alignment=Qt.AlignCenter)
        left_content.addStretch()
        
        self.results_layout = QVBoxLayout()
        left_content.addLayout(self.results_layout)
        left_content.addStretch()
        
    
        right_content = QVBoxLayout()
        self.image_label2 = QLabel()
        pixmap = QPixmap("C:\\Users\\user\\OneDrive\\Masaüstü\\skinalyzer\\ceng-407-408-2024-2025-Skinalyzer\\images\\mainpage_static_img.png")
        self.image_label2.setPixmap(pixmap)
        self.image_label2.setMinimumWidth(500)
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
                border:1px solid #A0A0A0; 
            }
        """)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        left_content = QHBoxLayout()
        icon_label = QLabel()

        self.pixmap_2 = QPixmap("C:\\Users\\user\\OneDrive\Masaüstü\\skinalyzer\\ceng-407-408-2024-2025-Skinalyzer\\images\\pastresult_logo.jpg")
        icon_label.setPixmap(self.pixmap_2)
        icon_label.setStyleSheet("border:none;")
        icon_label.setFixedSize(200, 200)
        icon_label.setAlignment(Qt.AlignCenter)

        left_content.addWidget(icon_label)
        
        right_content = QVBoxLayout()
        right_content.setSpacing(0)
        
        text_label = QLabel("You can access your saved analyse history by clicking the button below.")
        text_label.setStyleSheet("font-size: 17px; color: black; border:none;")
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
            
            self.image_label.setPixmap(QPixmap(self.uploaded_image).scaled(
                300, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
            self.image_label.setStyleSheet("""
                background-color: transparent; 
                border: 2px solid #4CAF50;
                border-radius: 10px;
                margin-bottom: 20px;
            """)
            
            self.clear_results_layout()
            
            self.analyze_button.setEnabled(False)
            self.analyze_button.setText("Analyzing...")
            
            QApplication.processEvents()
            
            is_valid, similarity, validation_message = self.validator.is_skin_lesion(self.uploaded_image)
            if not is_valid:
                self.clear_results_layout()
                error_frame = self.create_result_frame("Error", validation_message, "error")
                self.results_layout.addWidget(error_frame)
                self.analyze_button.setText("ANALYZE")
                self.analyze_button.setEnabled(True)
                return
            
            from predict_model import predict_model as run_prediction
            try:
                result = run_prediction(self.uploaded_image)
                
                save_result_to_db(self.user_id, self.uploaded_image, result["predicted_class"],
                    result["confidence"], result["risk_level"], result["lesion_description"])
                    
            except Exception as e:
                self.clear_results_layout()
                error_frame = self.create_result_frame("Error", f"Model error: {str(e)}", "error")
                self.results_layout.addWidget(error_frame)
                self.analyze_button.setText("ANALYZE")
                self.analyze_button.setEnabled(True)
                return
            
           
            self.clear_results_layout()
            self.analyze_button.setText("ANALYZE")
            self.analyze_button.setEnabled(True)
            
            
            result_container = QFrame()
            result_container.setStyleSheet("background-color: white; border-radius: 15px; border: 1px solid #e0e0e0;")
            result_container_layout = QVBoxLayout(result_container)
            
            
            header_frame = QFrame()
            header_frame.setStyleSheet("background-color: #8a4a64; border-radius: 10px 10px 0 0; border: none;")
            header_layout = QHBoxLayout(header_frame)
            
            title_label = QLabel("Analysis Results")
            title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; border: none;")
            
            confidence_widget = QFrame()
            confidence_widget.setStyleSheet("background-color: white; border-radius: 15px; border: none;")
            confidence_layout = QHBoxLayout(confidence_widget)
            confidence_label = QLabel(f"{result['confidence']:.1f}%")
            confidence_label.setStyleSheet("color: #8a4a64; font-weight: bold; font-size: 14px; border: none;")
            confidence_layout.addWidget(confidence_label)
            confidence_layout.setContentsMargins(10, 5, 10, 5)
            
            header_layout.addWidget(title_label)
            header_layout.addStretch()
            header_layout.addWidget(confidence_widget)
            
            
            content_frame = QFrame()
            content_frame.setStyleSheet("border: none;")
            content_layout = QVBoxLayout(content_frame)
            
            if "low" in result["risk_level"].lower():
                risk_color = "#D4EDDA"  
            elif "medium" in result["risk_level"].lower():
                risk_color = "#FFECB3"  
            elif "high" in result["risk_level"].lower():
                risk_color = "#FFCDD2"  
            else:
                risk_color = "#757575"  
                
            class_frame = QFrame()
            class_frame.setStyleSheet(f"background-color:{risk_color}; border-radius: 8px; border: none;")
            class_layout = QHBoxLayout(class_frame)
            
            class_label = QLabel(result["predicted_class"])
            if "low" in result["risk_level"].lower():
                class_label.setStyleSheet(f"color: #4CAF50; background-color: transparent; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
            elif "medium" in result["risk_level"].lower():
                class_label.setStyleSheet(f"color: #FF9800; background-color: transparent; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
            elif "high" in result["risk_level"].lower():
                class_label.setStyleSheet(f"color:#F44336; background-color: transparent; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
            else:
                class_label.setStyleSheet(f"color: white; background-color: transparent; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
                        
            risk_label = QLabel(result["risk_level"])
            if "low" in result["risk_level"].lower():
                risk_label.setStyleSheet(f"color: #4CAF50; background-color: transparent; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
            elif "medium" in result["risk_level"].lower():
                risk_label.setStyleSheet(f"color: #FF9800; background-color: transparent; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
            elif "high" in result["risk_level"].lower():
                risk_label.setStyleSheet(f"color: #F44336; background-color:transparent; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
            else:
                risk_label.setStyleSheet(f"color: white; background-color:transparent; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
                        
            class_layout.addWidget(class_label)
            class_layout.addStretch()
            class_layout.addWidget(risk_label)
            
           
            description_frame = QFrame()
            description_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 8px; border: none;")
            description_layout = QVBoxLayout(description_frame)
            
            description_title = QLabel("Lesion Description")
            description_title.setStyleSheet("font-weight: bold; color: #333; border: none;")
            
            description_text = QLabel(result["lesion_description"])
            description_text.setStyleSheet("color: #555; border: none;")
            description_text.setWordWrap(True)
            
            description_layout.addWidget(description_title)
            description_layout.addWidget(description_text)
            
            content_layout.addWidget(class_frame)
            content_layout.addWidget(description_frame)
            
            note_label = QLabel("Please consult with a dermatologist for proper diagnosis.")
            note_label.setStyleSheet("font-style: italic; color: #666; margin-top: 10px; border: none;")
            content_layout.addWidget(note_label)
            
           
            result_container_layout.addWidget(header_frame)
            result_container_layout.addWidget(content_frame)
            
            button_frame = QFrame()
            button_frame.setStyleSheet("border: none;")
            button_layout = QHBoxLayout(button_frame)
            

            new_analysis_button = QPushButton("New Analysis")
            new_analysis_button.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border-radius: 8px;
                    padding: 8px 15px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)

            new_analysis_button.clicked.connect(self.reset_analysis)
            
            button_layout.addWidget(new_analysis_button)
            
            result_container_layout.addWidget(button_frame)
            
            self.results_layout.addWidget(result_container)
            QApplication.processEvents()
            scroll_area = self.findChild(QScrollArea)
            if scroll_area:
                scroll_area.ensureWidgetVisible(result_container)
            
            self.add_to_history()

    def save_analysis_results(self):
        try:
            from predict_model import predict_model as run_prediction
            result = run_prediction(self.uploaded_image)

            
            save_result_to_db(self.user_id, self.uploaded_image, result["predicted_class"],
                                result["confidence"], result["risk_level"], result["lesion_description"])

            print("Analysis result has been saved to the database.")

        except Exception as e:
            print(f"Error saving analysis result: {e}")

        
    def clear_results_layout(self):
        """Clear all widgets from the results layout"""
        while self.results_layout.count() > 0:
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
    def create_result_frame(self, title, message, type="info"):
        """Create a styled frame for displaying messages"""
        frame = QFrame()
        
        if type == "error":
            frame.setStyleSheet("background-color: #FFEBEE; border-radius: 10px; padding: 10px;")
            title_color = "#D32F2F"
        elif type == "warning":
            frame.setStyleSheet("background-color: #FFF8E1; border-radius: 10px; padding: 10px;")
            title_color = "#FF8F00"
        else:  
            frame.setStyleSheet("background-color: #E3F2FD; border-radius: 10px; padding: 10px;")
            title_color = "#1976D2"
            
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {title_color}; border: none;")
        
        message_label = QLabel(message)
        message_label.setStyleSheet("color: #333; border: none;")
        message_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        
        return frame
        
    def reset_analysis(self):
        """Reset the analysis UI to upload new image"""
        self.image_label.clear()
        self.image_label.setStyleSheet("background-color: transparent; border-radius: 10px; border: 1px solid #A0A0A0;")
        self.clear_results_layout()
        self.analyze_button.setText("ANALYZE")
        self.analyze_button.setEnabled(False)
        self.uploaded_image = None
    
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
         self.results_window = AnalysisResultsWindow(self.user_id)
         self.results_window.show()
    
    def show_about(self):
        """Shows the About dialog with information about the application"""
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About Skinalyzer")
        about_dialog.setFixedSize(600, 400)
        about_dialog.setStyleSheet("""
            QDialog {
                background-color: #F8EBF4;
                color: #2C3E50;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(about_dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title_label = QLabel("About Skinalyzer")
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #9D5171;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        content_label = QLabel(
            "Skinalyzer is an AI-powered tool designed to help with the early detection "
            "of skin conditions and potential cancer indicators.\n\n"
            "Our mission is to make skin health accessible to everyone through innovative "
            "technology and artificial intelligence.\n\n"
            "Note: This is a demonstration application and not intended for medical use."
        )
        content_label.setStyleSheet("""
            font-size: 14px; 
            color: #2C3E50;
            line-height: 150%;
        """)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignCenter)
        
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #9D5171;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8a4a64;
            }
            QPushButton:pressed {
                background-color: #703a50;
            }
        """)
        close_btn.clicked.connect(about_dialog.accept)
        
        layout.addWidget(title_label)
        layout.addWidget(content_label)
        layout.addStretch()
        layout.addWidget(close_btn, 0, Qt.AlignCenter)
        
        about_dialog.exec()

    def show_contact(self):
        """Shows the Contact dialog with contact information"""
        contact_dialog = QDialog(self)
        contact_dialog.setWindowTitle("Contact Us")
        contact_dialog.setFixedSize(600, 400)
        contact_dialog.setStyleSheet("""
            QDialog {
                background-color: #F8EBF4;
                color: #2C3E50;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(contact_dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title_label = QLabel("Contact Us")
        title_label.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #9D5171;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        content_label = QLabel(
            "For questions, feedback, or support regarding Skinalyzer:\n\n"
            "Email: test@example.com\n"
            "Phone: +1 (555) 555-5555\n\n"
            "Follow us on social media for updates and skin health tips:\n"
            "@skinalyzer"
        )
        content_label.setStyleSheet("""
            font-size: 14px; 
            color: #2C3E50;
            line-height: 150%;
        """)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignCenter)
        
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #9D5171;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8a4a64;
            }
            QPushButton:pressed {
                background-color: #703a50;
            }
        """)
        close_btn.clicked.connect(contact_dialog.accept)
        
        layout.addWidget(title_label)
        layout.addWidget(content_label)
        layout.addStretch()
        layout.addWidget(close_btn, 0, Qt.AlignCenter)
        
        contact_dialog.exec()

    def log_out(self):
        """Shows a confirmation dialog for logging out"""
        logout_dialog = QDialog(self)
        logout_dialog.setWindowTitle("Log Out")
        logout_dialog.setFixedSize(450, 250)
        logout_dialog.setStyleSheet("""
            QDialog {
                background-color: #F8EBF4;
                color: #2C3E50;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(logout_dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        question_label = QLabel("Are you sure you want to log out?")
        question_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #9D5171;
        """)
        question_label.setAlignment(Qt.AlignCenter)

        desc_label = QLabel("This will take you back to the login page.")
        desc_label.setStyleSheet("""
            font-size: 14px; 
            color: #2C3E50;
        """)
        desc_label.setAlignment(Qt.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
 
        yes_btn = QPushButton("Yes")
        yes_btn.setFixedWidth(100)
        yes_btn.setCursor(Qt.PointingHandCursor)
        yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #9D5171;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8a4a64;
            }
            QPushButton:pressed {
                background-color: #703a50;
            }
        """)
        yes_btn.clicked.connect(self.go_to_login)
        
        no_btn = QPushButton("No")
        no_btn.setFixedWidth(100)
        no_btn.setCursor(Qt.PointingHandCursor)
        no_btn.setStyleSheet("""
            QPushButton {
                background-color: #7F8C8D;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6C7A7A;
            }
            QPushButton:pressed {
                background-color: #596566;
            }
        """)
        no_btn.clicked.connect(logout_dialog.reject)    
        
        button_layout.addStretch()
        button_layout.addWidget(yes_btn)
        button_layout.addWidget(no_btn)
        button_layout.addStretch()
        
        layout.addWidget(question_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        logout_dialog.exec()



    def go_to_login(self):
        from login_main import MainWindow
        self.login_window = MainWindow()
        self.login_window.show()
        self.close()

    
def save_result_to_db(user_id, image_path, predicted_class, confidence, risk_level, lesion_description):
    conn = mysql.connector.connect(
        host="mydatabase.c9y4kwss4q2e.eu-north-1.rds.amazonaws.com",
        user="bilgesufindik",
        password="Topraksu.01",
        database="mydatabase",
        port=3306
    )
    cursor = conn.cursor()

    query = """
    INSERT INTO result (UserID, ImagePath, PredictedClass, Confidence, RiskLevel, LesionDescription)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (user_id, image_path, predicted_class, confidence, risk_level, lesion_description)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()   
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SkinalyzerUI()
    window.show()
    sys.exit(app.exec())