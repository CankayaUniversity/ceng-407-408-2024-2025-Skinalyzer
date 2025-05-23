from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
                              QHBoxLayout, QPushButton, QSplitter, QGridLayout, 
                              QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QFont, QColor, QPalette
import mysql.connector
from detail import DetailsWindow

class AnalysisResultsWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("Analysis Results History")
        self.setMinimumSize(800, 600)
        self.user_id = user_id
    
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        title_label = QLabel("Analysis Results History")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color:#9D5171; margin-bottom: 15px;")
        main_layout.addWidget(title_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        results = self.get_user_results()
        
        if not results:
            no_results = QLabel("No analysis results found for this user.")
            no_results.setAlignment(Qt.AlignCenter)
            no_results.setStyleSheet("font-size: 14px; color: #7F8C8D; padding: 40px;")
            content_layout.addWidget(no_results)
        else:
            for index, res in enumerate(results):
               
                card = self.create_result_card(res, index)
                content_layout.addWidget(card)
        
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        content_layout.addItem(spacer)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        bottom_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #8a4a64;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        close_btn.clicked.connect(self.close)  # Close the current window when clicked
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn)
        main_layout.addLayout(bottom_layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #F8EBF4;
                color: #2C3E50;
                font-family: Arial, sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #F0F0F0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #9D5171;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #AAAAAA;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def create_result_card(self, res, index):
        """Analiz sonucu için kart oluştur"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
        """)
        
        card_layout = QGridLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        image_frame = QFrame()
        image_layout = QVBoxLayout(image_frame)
        image_layout.setAlignment(Qt.AlignCenter)
        
        thumbnail_label = QLabel()
        thumbnail_pixmap = QPixmap(res['image_path'])
        if not thumbnail_pixmap.isNull():
            thumbnail_pixmap = thumbnail_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumbnail_label.setPixmap(thumbnail_pixmap)
            thumbnail_label.setStyleSheet("""
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 5px;
                background-color: #FAFAFA;
            """)
        else:
            thumbnail_label.setText("Image could not be loaded")
            thumbnail_label.setStyleSheet("""
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                padding: 30px;
                background-color: #FAFAFA;
                color: #7F8C8D;
            """)
        
        image_layout.addWidget(thumbnail_label)
        
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        
        date_label = QLabel(f"<span style='color:#7F8C8D;'>Date:</span> {res['date']}")
        date_label.setStyleSheet("font-size: 12px;")

        predicted_class = QLabel(f"<span style='font-weight:bold; font-size:16px;'>{res['predicted_class']}</span>")

        risk_color = self.get_risk_color(res['risk_level'])
        risk_label = QLabel(f"<span style='color:{risk_color}; font-weight:bold;'>Risk Level: {res['risk_level']}</span>")
 
        # Format confidence with proper decimal point
        confidence_value = res['confidence']
        if isinstance(confidence_value, (int, float)):
            confidence_str = f"{confidence_value:.2f}"
        else:
            confidence_str = str(confidence_value)
        confidence_label = QLabel(f"<span style='color:#7F8C8D;'>Confidence:</span> %{confidence_str}")

        # Remove the description label completely - hide from the main results view

        info_layout.addWidget(date_label)
        info_layout.addWidget(predicted_class)
        info_layout.addWidget(risk_label)
        info_layout.addWidget(confidence_label)
        info_layout.addStretch()

        detail_button = QPushButton("Show Details")
        detail_button.setCursor(Qt.PointingHandCursor)
        detail_button.setStyleSheet("""
            QPushButton {
                background-color: #ECF0F1;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 5px 10px;
                color: #2C3E50;
            }
            QPushButton:hover {
                background-color: #D6DBDF;
            }
        """)
        detail_button.clicked.connect(lambda: self.show_details(res))  
        info_layout.addWidget(detail_button)
 
        card_layout.addWidget(image_frame, 0, 0)
        card_layout.addWidget(info_frame, 0, 1)
        card_layout.setColumnStretch(1, 2)  
        
        return card
    
    def show_details(self, result):
        details_window = DetailsWindow(result)
        details_window.exec_() 

 
    def get_risk_color(self, risk_level):
        """Returns the color based on the risk level"""
        
        risk_level = risk_level.strip().lower()

        risk_colors = {
            "low": "#2ECC71",  
            "medium": "#F39C12",   
            "high": "#E74C3C"  
        }
        print(f"Risk level: '{risk_level}'")

        
        return risk_colors.get(risk_level, "#000000")
    
    def get_user_results(self):
        try:
            conn = mysql.connector.connect(
                host="mydatabase.c9y4kwss4q2e.eu-north-1.rds.amazonaws.com",
                user="bilgesufindik",
                password="Topraksu.01",
                database="mydatabase",
                port=3306
            ) 
            cursor = conn.cursor()

            query = """
            SELECT ImagePath, PredictedClass, Confidence, RiskLevel, LesionDescription, DateAnalyzed
            FROM result WHERE UserID = %s ORDER BY DateAnalyzed DESC
            """
            cursor.execute(query, (self.user_id,))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                result = {
                    "image_path": row[0],
                    "predicted_class": row[1],
                    "confidence": row[2],  
                    "risk_level": row[3],
                    "description": row[4],
                    "date": row[5].strftime("%Y-%m-%d %H:%M")
                }
                results.append(result)

            cursor.close()
            conn.close()
            return results

        except mysql.connector.Error as err:
            print("MySQL Error:", err)
            return []