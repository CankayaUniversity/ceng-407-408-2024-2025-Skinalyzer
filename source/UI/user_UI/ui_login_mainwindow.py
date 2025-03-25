from PySide6.QtCore import QRect, Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout ,QLabel, QLineEdit, QMainWindow, QPushButton, QStatusBar, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy
import mysql.connector
from ui_user import SkinalyzerUI 
import bcrypt
from registermain import RegisterWindow

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600) 
        MainWindow.setStyleSheet(u"background-color: rgb(248, 235, 244);")

        
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

       
        outer_layout = QVBoxLayout(self.centralwidget)
        outer_layout.setAlignment(Qt.AlignCenter) 
        
      
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"background-color: rgb(255, 255, 255); padding: 20px;") 
        self.widget.setFixedWidth(400)  
        self.widget.setFixedHeight(600)
        outer_layout.addWidget(self.widget)

        
        layout = QVBoxLayout(self.widget)
        layout.setAlignment(Qt.AlignCenter)  
       

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

        
        self.email = QLineEdit(self.widget)
        self.email.setObjectName(u"email")
        self.email.setStyleSheet(u"QLineEdit {\n"
                                 "	color: rgb(0, 0, 0);\n"
                                 "	font: 9pt \"Segoe UI\";\n"
                                 "    border: 1px solid #9D5171;\n"
                                 "    border-radius: 5px;\n"
                                 "}")
       
        self.email.setFixedWidth(350)
        self.email.setFixedHeight(55)
        email_layout = QHBoxLayout()
        email_layout.setAlignment(Qt.AlignCenter)  
        email_layout.addWidget(self.email)

        layout.addLayout(email_layout) 
        

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.label_3.setText("Password:")
        layout.addWidget(self.label_3)

       
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
        self.password.setFixedHeight(55)
      
        password_layout = QHBoxLayout()
        password_layout.setAlignment(Qt.AlignCenter) 
        password_layout.addWidget(self.password)

        layout.addLayout(password_layout) 

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)  
        layout.addItem(spacer)

        self.loginButton = QPushButton(self.widget)
        self.loginButton.setObjectName(u"loginButton")
        self.loginButton.setStyleSheet(u"background-color: rgb(157, 81, 113);")
        self.loginButton.setText("Login")
        self.loginButton.setFixedWidth(200)
        self.loginButton.setFixedHeight(60)

        
        loginButton_layout = QHBoxLayout()
        loginButton_layout.setAlignment(Qt.AlignCenter)  
        loginButton_layout.addWidget(self.loginButton)

        layout.addLayout(loginButton_layout) 

        
        self.messageLabel = QLabel(self.widget)
        self.messageLabel.setObjectName(u"messageLabel")
        self.messageLabel.setStyleSheet("color: red;")
        self.messageLabel.setAlignment(Qt.AlignCenter)
        self.messageLabel.setText("")
        layout.addWidget(self.messageLabel)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"color: rgb(34, 34, 34);")
        self.label_4.setText("Don't have an account? Register")
        
        label_4_layout = QHBoxLayout()
        label_4_layout.setAlignment(Qt.AlignCenter)  
        label_4_layout.addWidget(self.label_4)

        layout.addLayout(label_4_layout)

        
        MainWindow.show()

        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

       
        self.loginButton.clicked.connect(self.loginfunction)
 
    def initialize_database(self):

        
        
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Tprksu.001",
            database="user_database"
        )
        cursor = conn.cursor()

        
        cursor.execute("SELECT UserID, Password FROM user")
        users = cursor.fetchall()

        for user in users:
            user_id, plain_password = user

            
            if not plain_password.startswith("$2b$"):
                hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode()

                
                update_query = "UPDATE user SET Password = %s WHERE UserID = %s"
                cursor.execute(update_query, (hashed_password, user_id))
                conn.commit()
                print(f"The user {user_id} password has been updated by hashing.")

        print("All passwords have been successfully hashed and updated.")

        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user (
            UserID VARCHAR(50) PRIMARY KEY,
            Name VARCHAR(100) NOT NULL,
            Email VARCHAR(255) UNIQUE NOT NULL,
            Password VARCHAR(255) NOT NULL,
            Role VARCHAR(50) DEFAULT 'user',
            DateJoined DATE DEFAULT (CURRENT_DATE),
            SkinColor VARCHAR(50)
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("User tablosu başarıyla oluşturuldu.")

        
        self.insert_users(cursor, conn)

        
        cursor.close()
        conn.close()

    def insert_users(self, cursor, conn):
        
        users = [
            ("USR001", "Bilge Admin", "bilge@example.com", self.hash_password("1234"), "admin", "Dark"),
            ("USR002", "Pelin Admin", "ahmet@example.com", self.hash_password("12345"), "admin", "Light"),
            ("USR003", "Melike User", "mehmet@example.com", self.hash_password("123456"), "user", "Medium"),
            ("USR004", "Emrahan User", "ayse@example.com", self.hash_password("1234567"), "user", "Fair")
        ]

        query = """
        INSERT IGNORE INTO user (UserID, Name, Email, Password, Role, DateJoined, SkinColor)
        VALUES (%s, %s, %s, %s, %s, CURDATE(), %s)
        """
        cursor.executemany(query, users)
        conn.commit()
        print(" Users added successfully.")

    def hash_password(self, password):
       
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

    def loginfunction(self):
        
        email = self.email.text()
        password = self.password.text()


        if email == "test@example.com" and password == "12345":
            self.messageLabel.setText("Login successful!")
            self.switch_to_main_page()

       
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Tprksu.001",
            database="user_database"
        )
        cursor = conn.cursor()

        
        query = "SELECT Password FROM user WHERE Email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            stored_password = user[0]

            
            if stored_password.startswith("$2b$"):
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                   #9self.switch_to_main_page()
                    self.messageLabel.setText("correct password!")
                    self.messageLabel.setStyleSheet("color: green;")
                else:
                    self.messageLabel.setText(" Incorrect password!")
                    self.messageLabel.setStyleSheet("color: red;")
            else:
                self.messageLabel.setText(" Invalid password format!")
                self.messageLabel.setStyleSheet("color: red;")
        else:
            self.messageLabel.setText(" User not found!")
            self.messageLabel.setStyleSheet("color: red;")
    
    def switch_to_main_page(self):

        self.skinalyzer_window = SkinalyzerUI()
        self.skinalyzer_window.show()
        self.parent().close()
        main_window = self.centralwidget.window()
        main_window.close()
