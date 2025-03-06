from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout ,QLabel, QLineEdit, QMainWindow, QPushButton, QStatusBar, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)  # Başlangıç boyutu
        MainWindow.setStyleSheet(u"background-color: rgb(248, 235, 244);")

        # Central widget
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        # Dış Layout
        outer_layout = QVBoxLayout(self.centralwidget)
        outer_layout.setAlignment(Qt.AlignCenter)  # Bütün widget'ları ortalamak için
        

        # Orta widget (bu widget içeriği taşıyacak ve ortalayacak)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"background-color: rgb(255, 255, 255); padding: 20px;")  # Padding ekleyerek içeriği biraz daha kenardan uzaklaştırıyoruz
        self.widget.setFixedWidth(400)  # Genişliği sabitle
        outer_layout.addWidget(self.widget)

        # İç Layout (ortadaki widget'ın içindeki widget'ları yerleştirecek)
        layout = QVBoxLayout(self.widget)
        layout.setAlignment(Qt.AlignCenter)  # Widget'ları ortalamak için
       

        # Labels
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"color: rgb(0, 0, 0);\n"
                                 "font: 600 12pt \"Segoe UI\";")
        self.label.setText("Welcome")
        layout.addWidget(self.label)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.label_2.setText("E-mail/Phone Number:")
        layout.addWidget(self.label_2)

        # Email QLineEdit
        self.email = QLineEdit(self.widget)
        self.email.setObjectName(u"email")
        self.email.setStyleSheet(u"QLineEdit {\n"
                                 "	color: rgb(0, 0, 0);\n"
                                 "	font: 9pt \"Segoe UI\";\n"
                                 "    border: 1px solid #9D5171;\n"
                                 "    border-radius: 5px;\n"
                                 "}")
         # Kutunun minimum genişliğini ayarla
        self.email.setFixedWidth(350)
        self.email.setFixedHeight(50)
        # Kutu ortalamak için QHBoxLayout ekle
        email_layout = QHBoxLayout()
        email_layout.setAlignment(Qt.AlignCenter)  # Ortala
        email_layout.addWidget(self.email)

        layout.addLayout(email_layout) 
        

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.label_3.setText("Password:")
        layout.addWidget(self.label_3)

        # Password QLineEdit
        self.password = QLineEdit(self.widget)
        self.password.setObjectName(u"password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(u"QLineEdit {\n"
                                    "	color: rgb(0, 0, 0);\n"
                                    "	font: 9pt \"Segoe UI\";\n"
                                    "    border: 1px solid #9D5171;\n"
                                    "    border-radius: 5px;\n"
                                    "}")
        
        self.password.setFixedWidth(350)
        self.password.setFixedHeight(50)
        # Kutu ortalamak için QHBoxLayout ekle
        password_layout = QHBoxLayout()
        password_layout.setAlignment(Qt.AlignCenter)  # Ortala
        password_layout.addWidget(self.password)

        layout.addLayout(password_layout) 

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)  # Yükseklik ve genişlik ayarı
        layout.addItem(spacer)

        # Login Button
        self.loginButton = QPushButton(self.widget)
        self.loginButton.setObjectName(u"loginButton")
        self.loginButton.setStyleSheet(u"background-color: rgb(157, 81, 113);")
        self.loginButton.setText("Login")
        self.loginButton.setFixedWidth(200)
        self.loginButton.setFixedHeight(60)

        # Kutu ortalamak için QHBoxLayout ekle
        loginButton_layout = QHBoxLayout()
        loginButton_layout.setAlignment(Qt.AlignCenter)  # Ortala
        loginButton_layout.addWidget(self.loginButton)

        layout.addLayout(loginButton_layout) 

        # Message Label
        self.messageLabel = QLabel(self.widget)
        self.messageLabel.setObjectName(u"messageLabel")
        self.messageLabel.setStyleSheet("color: red;")
        self.messageLabel.setAlignment(Qt.AlignCenter)
        self.messageLabel.setText("")  # Başlangıçta boş bırak
        layout.addWidget(self.messageLabel)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"color: rgb(34, 34, 34);")
        self.label_4.setText("Don't have an account? Register")
        
        label_4_layout = QHBoxLayout()
        label_4_layout.setAlignment(Qt.AlignCenter)  # Ortala
        label_4_layout.addWidget(self.label_4)

        layout.addLayout(label_4_layout)

        # Pencereyi normal boyutta başlatıyoruz
        MainWindow.show()

        # Pencereyi ayarlama
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Login button'a tıklanıldığında login fonksiyonunu çağır
        self.loginButton.clicked.connect(self.loginfunction)
 
    def loginfunction(self):
        email = self.email.text()
        password = self.password.text()

        if email == "test@example.com" and password == "12345":
            self.messageLabel.setText("Login successful!")
            self.messageLabel.setStyleSheet("color: green;")
        else:
            self.messageLabel.setText("Invalid email or password!")
            self.messageLabel.setStyleSheet("color: red;")
