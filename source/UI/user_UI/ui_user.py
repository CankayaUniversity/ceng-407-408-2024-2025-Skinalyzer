from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QTableView, QFrame, QTextBrowser,QHBoxLayout
)

class Ui_Widget(object):
    def setupUi(self, Widget):
        Widget.setObjectName("Widget")
        Widget.resize(832, 616)
        Widget.setStyleSheet("QWidget#Widget { background-color: white; }")

        # Scroll Area 
        self.scrollArea = QScrollArea(Widget)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setGeometry(QRect(0, 0, 832, 616))  # Sayfa boyutunu korur
        self.scrollArea.setWidgetResizable(True)  # İçerik genişleyebilir
        self.scrollArea.setStyleSheet("QScrollArea { background-color: white; }")

        # All widget
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setStyleSheet("QWidget#scrollAreaWidgetContents { background-color: white; }")

        # Main Layout 
        self.main_layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.main_layout.setContentsMargins(10, 0, 10, 10)
        self.main_layout.setSpacing(10)

        # Header frame
        self.frame_3 = QFrame()
        self.frame_3.setStyleSheet("""
            QFrame {
                
                background-color: #9D5171;
                
                 }
        """)
        self.frame_3.setFixedHeight(100) 
        self.main_layout.addWidget(self.frame_3)

        #content of frame
        self.inner_layout = QHBoxLayout(self.frame_3)
        self.inner_layout.setContentsMargins(100, 0, 10, 10)
        self.label_38 = QLabel("Skinanalyzer")
        self.label_38.setStyleSheet("font: 600 12pt 'Segoe UI' background-color: #ffffff;")
        self.inner_layout.addWidget(self.label_38)

        
        self.label_39 = QLabel("About us")
        self.label_39.setStyleSheet("font: 600 12pt 'Segoe UI' background-color: #ffffff;")
        self.inner_layout.addWidget(self.label_39)

        self.label_40 = QLabel("Contact us")
        self.label_40.setStyleSheet("font: 600 12pt 'Segoe UI' background-color: #ffffff;")
        self.inner_layout.addWidget(self.label_40)
        
        self.label_42 = QLabel("Help")
        self.label_42.setStyleSheet("font: 600 12pt 'Segoe UI' background-color: #ffffff;")
        self.inner_layout.addWidget(self.label_42)

        # Grey frame's layout
        self.grey_frame_layout = QVBoxLayout()
        self.grey_frame_layout.setContentsMargins(75, 0, 75, 10)

        
        # inner grey Frame'i
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                border-radius: 15px;
                background-color: #dcdcdc;
                border: 1px solid #b0b0b0;
                padding: 10px;
            }
        """)
        self.frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.grey_frame_layout.addWidget(self.frame)
       

        self.inner_layout = QHBoxLayout(self.frame)  
        self.inner_layout.setSpacing(10)

        self.left_frame = QFrame(self.frame)
        self.left_frame.setStyleSheet("background-color: transparent; border: none;")
        self.left_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed) 
        self.inner_layout.addWidget(self.left_frame)

        left_layout = QVBoxLayout(self.left_frame)

        # Grey frames header
        self.label_37 = QLabel("Skinanalyzer")
        self.label_37.setStyleSheet("font: 9pt 'Segoe UI'; color: black; border: none")
        left_layout.addWidget(self.label_37)

        # Açıklama metni
        self.textBrowser_5 = QTextBrowser()
        self.textBrowser_5.setStyleSheet("border: none; color: rgb(0, 0, 0);")
        self.textBrowser_5.setText("Skinanalyzer evaluates symptoms on your skin and assists in early disease diagnosis through the power of innovative artificial intelligence (AI) skin technology.")
        self.textBrowser_5.setFixedHeight(75) 

        left_layout.addWidget(self.textBrowser_5)
        

        self.uploadLabel = QLabel("Upload foto")
        self.uploadLabel.setStyleSheet("""
        QLabel {
                border-radius: 15px;
                background-color: #ffffff;
                color:#dcdcdc;                       
                border: none;
                padding: 10px;
                font: 9pt 'Segoe UI';
                
        }
        """)
        self.uploadLabel.setFixedSize(200,100)
        left_layout.addWidget(self.uploadLabel)

        
        self.uploadButton_5 = QPushButton("Upload")
        self.uploadButton_5.setStyleSheet("""
        QPushButton {
                text-align: center;
                background-color: rgb(157, 81, 113);
                border-radius: 5px;
        }
        QPushButton:hover {
                background-color: #E2E1E1  /* Hover rengini burada belirleyebilirsiniz */
        }
        """)
        self.uploadButton_5.setFixedSize(100, 50) 
        self.uploadButton_5.setEnabled(True)
        left_layout.addWidget(self.uploadButton_5)

        self.right_frame = QFrame(self.frame)
        self.right_frame.setStyleSheet("background-color: transparent;")
        self.right_frame.setFixedWidth(250)

        right_layout = QVBoxLayout()  # Creating layout for right_frame
        self.right_frame.setLayout(right_layout)  # Setting the layout to right_frame

        # Right frame content
        self.photo_label = QLabel("photo will be uploaded")
        right_layout.addWidget(self.photo_label)  # Adding the widget to the right layout

        # Add right_frame to the main layout
        self.inner_layout.addWidget(self.right_frame)

        # bottom grey frame 
        self.frame_2 = QFrame()
        self.frame_2.setStyleSheet("""
            QFrame {
                border-radius: 15px;
                background-color: #dcdcdc;
                border: 1px solid #b0b0b0;
                padding: 10px;
            }
        """)
        self.frame_2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.grey_frame_layout.addWidget(self.frame_2)
        

        # Frame 2 
        self.inner_layout_2 = QVBoxLayout(self.frame_2)
        self.label_41 = QLabel("You can access your saved analyse history by clicking the button below")
        self.label_41.setStyleSheet("font: 9pt 'Segoe UI'; color: black; border: none;")
        self.inner_layout_2.addWidget(self.label_41)

        self.showButton = QPushButton("Show")
        self.showButton.setStyleSheet("text-align: center; background-color: rgb(157, 81, 113);")
        self.showButton.setFixedSize(100, 50) 
        self.inner_layout_2.addWidget(self.showButton)

        self.inner_layout_2.setAlignment(self.showButton, Qt.AlignmentFlag.AlignCenter)
        self.inner_layout_2.setAlignment(self.label_41, Qt.AlignmentFlag.AlignCenter)

        self.grey_frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.grey_frame_layout)

       
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        Widget.setLayout(QVBoxLayout())
        Widget.layout().addWidget(self.scrollArea)

        self.uploadButton_5.clicked.connect(self.upload_button_clicked)
        

    def upload_button_clicked(self):
                print("Upload Button Clicked!")

