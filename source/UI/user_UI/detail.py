from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QGridLayout, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class DetailsWindow(QDialog):  
    def __init__(self, result):
        super().__init__()
        self.setWindowTitle("Analysis Details")
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

        confidence_value = result['confidence']
        if isinstance(confidence_value, (int, float)):
            confidence_str = f"{confidence_value:.2f}"
        else:
            confidence_str = str(confidence_value)

        info_frame = QFrame()
        info_layout = QGridLayout(info_frame)
        
        info_layout.addWidget(QLabel("Predicted Class:"), 0, 0)
        info_layout.addWidget(QLabel(result['predicted_class']), 0, 1)
        
        info_layout.addWidget(QLabel("Risk Level:"), 1, 0)
        info_layout.addWidget(QLabel(result['risk_level']), 1, 1)
        
        info_layout.addWidget(QLabel("Confidence:"), 2, 0)
        info_layout.addWidget(QLabel(f"%{confidence_str}"), 2, 1)
        
        info_layout.addWidget(QLabel("Date:"), 3, 0)
        info_layout.addWidget(QLabel(result['date']), 3, 1)
        
        layout.addWidget(info_frame)
        
        if result['description']:
            desc_frame = QFrame()
            desc_layout = QVBoxLayout(desc_frame)
            
            desc_title = QLabel("Description:")
            desc_title.setStyleSheet("font-weight: bold;")
            desc_layout.addWidget(desc_title)
            
            # Clean the HTML from description
            clean_description = self.clean_html_content(result['description'])
            desc_items = self.split_description_into_items(clean_description)
            
            for item in desc_items:
                item_label = QLabel(f"• {item}")
                item_label.setWordWrap(True)
                desc_items_layout = QVBoxLayout()
                desc_items_layout.addWidget(item_label)
                desc_layout.addLayout(desc_items_layout)
            
            layout.addWidget(desc_frame)
        
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
    
    def clean_html_content(self, html_content):
        """Remove HTML tags and format properly"""
        if not html_content:
            return ""
        
        replacements = [
            ("<br>", "\n"),
            ("<b>", ""),
            ("</b>", ""),
            ("<span style='color:red;'>", ""),
            ("</span>", ""),
            ("&nbsp;", " ")
        ]
        
        for old, new in replacements:
            html_content = html_content.replace(old, new)
        
        return html_content
    
    def split_description_into_items(self, description):
        """Split the description into individual items for the list display"""
        if not description:
            return []
        
        if '\n' in description:
            lines = description.split('\n')
            items = [line.strip() for line in lines if line.strip()]
            if items:
                return items

        if '. ' in description:
            sentences = description.split('. ')
            items = [sentence.strip() + ('.' if not sentence.endswith('.') and i < len(sentences)-1 else '') 
                    for i, sentence in enumerate(sentences) if sentence.strip()]
            if items:
                return items

        for delim in ['• ', '- ', '* ', ';']:
            if delim in description:
                items = [item.strip() for item in description.split(delim) if item.strip()]
                if items:
                    return items
        
        return [description] if description.strip() else []