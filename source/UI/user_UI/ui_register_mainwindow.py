from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QColumnView, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget, QMessageBox, QSpacerItem,QComboBox)
import mysql.connector
import bcrypt
import uuid
import re

class Ui_RegisterWindow(object):
    def on_register(self):
        full_name = self.fullName.text().strip()
        user_name = self.userName.text().strip()
        email = self.r_email.text().strip()  
        password = self.password.text().strip()
        confirm_password = self.confirm_pass.text().strip()
        skin_color = self.skinColor.currentText().strip()

        if not full_name or not user_name or not email or not password or not confirm_password:
            self.show_error("Please fill in all fields!")
            return
        if len(full_name) < 3:
            self.show_error("Full name must be at least 3 characters long!")
            return

        if len(password) < 4:
            self.show_error("Password must be at least 4 characters long!")
            return


        if password != confirm_password:
            self.show_error("Passwords do not match!")
            return
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.show_error("Please enter a valid email address!")
            return     
       

        try:
            conn = mysql.connector.connect(
            host="mydatabase.c9y4kwss4q2e.eu-north-1.rds.amazonaws.com",
            user="bilgesufindik",
            password="Topraksu.01",
            database="mydatabase",
            port=3306
        )
            cursor = conn.cursor()

            cursor.execute("SELECT Email FROM user WHERE Email = %s", (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                self.show_error("This email is already registered!")
                cursor.close()
                conn.close()
                return

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

            insert_query = """
            INSERT INTO user (UserID, Name, Email, Password, Role, DateJoined, SkinColor)
            VALUES (%s, %s, %s, %s, %s, CURDATE(), %s)
            """
            user_id = f"USR{int.from_bytes(email.encode(), 'little') % 100000}"  
            cursor.execute(insert_query, (user_id, full_name, email, hashed_password, "user", skin_color))
            print(f"Number of rows affected: {cursor.rowcount}")
            conn.commit()

            if cursor.rowcount > 0:
                self.show_success("Registration successful! You can now log in.")
            else:
                self.show_error("Registration failed! Please try again.")

        except mysql.connector.Error as e:
            self.show_error(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec()

    def show_success(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Successful")
        msg.exec()

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1019, 679)
        MainWindow.setStyleSheet(u"background-color: rgb(248, 235, 244);")
        self.window = MainWindow 
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        
        self.main_layout = QHBoxLayout(self.centralwidget)
        self.main_layout.setAlignment(Qt.AlignCenter) 

        self.horizontalLayoutWidget = QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(60, 0, 291, 651)
        
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)

        self.columnView_2 = QColumnView(self.horizontalLayoutWidget)
        spacer = QSpacerItem(50, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.main_layout.addItem(spacer) 
        self.columnView_2.setObjectName(u"columnView_2")
        self.columnView_2.setStyleSheet(u"background-color: rgb(157, 81, 113);")
        self.horizontalLayout.addWidget(self.columnView_2, 1)
        self.columnView_2.setMinimumHeight(200)
        self.columnView_2.setMaximumHeight(1000)
        
        self.columnView = QColumnView(self.horizontalLayoutWidget)
        self.columnView.setObjectName(u"columnView")
        self.columnView.setStyleSheet(u"background-color: rgb(219, 126, 166);")
        self.horizontalLayout.addWidget(self.columnView, 1)
        self.columnView.setMinimumHeight(200)
        self.columnView.setMaximumHeight(1000)   

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(460, 30, 501, 601)
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(20, 10, 20, 10)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.verticalLayout.addWidget(self.label)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.verticalLayout.addWidget(self.label_2)

        self.fullName = QLineEdit(self.widget)
        self.fullName.setObjectName(u"fullName")
        self.fullName.setStyleSheet(u"QLineEdit {\n    color: rgb(0, 0, 0); \n    background-color: rgb(255, 255, 255);\n    font: 9pt \"Segoe UI\";\n    border: 1px solid #9D5171;\n    border-radius: 5px;\n}")
        self.verticalLayout.addWidget(self.fullName)

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.verticalLayout.addWidget(self.label_3)

        self.userName = QLineEdit(self.widget)
        self.userName.setObjectName(u"userName")
        self.userName.setStyleSheet(u"QLineEdit {\n    color: rgb(0, 0, 0); \n    background-color: rgb(255, 255, 255);\n    font: 9pt \"Segoe UI\";\n    border: 1px solid #9D5171;\n    border-radius: 5px;\n}")
        self.verticalLayout.addWidget(self.userName)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.verticalLayout.addWidget(self.label_4)

        self.r_email = QLineEdit(self.widget)
        self.r_email.setObjectName(u"r_email")
        self.r_email.setStyleSheet(u"QLineEdit {\n    color: rgb(0, 0, 0); \n    background-color: rgb(255, 255, 255);\n    font: 9pt \"Segoe UI\";\n    border: 1px solid #9D5171;\n    border-radius: 5px;\n}")
        self.verticalLayout.addWidget(self.r_email)

        self.label_5 = QLabel(self.widget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.verticalLayout.addWidget(self.label_5)

        self.password = QLineEdit(self.widget)
        self.password.setObjectName(u"password")
        self.password.setStyleSheet(u"QLineEdit {\n    color: rgb(0, 0, 0); \n    background-color: rgb(255, 255, 255);\n    font: 9pt \"Segoe UI\";\n    border: 1px solid #9D5171;\n    border-radius: 5px;\n}")
        self.verticalLayout.addWidget(self.password)

        self.label_6 = QLabel(self.widget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.verticalLayout.addWidget(self.label_6)

        self.confirm_pass = QLineEdit(self.widget)
        self.confirm_pass.setObjectName(u"confirm_pass")
        self.confirm_pass.setStyleSheet(u"QLineEdit {\n    color: rgb(0, 0, 0); \n    background-color: rgb(255, 255, 255);\n    font: 9pt \"Segoe UI\";\n    border: 1px solid #9D5171;\n    border-radius: 5px;\n}")
        self.verticalLayout.addWidget(self.confirm_pass)

        self.label_7 = QLabel(self.widget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"color: rgb(0, 0, 0);")
        self.verticalLayout.addWidget(self.label_7)

        self.skinColor = QComboBox(self.widget)
        self.skinColor.setObjectName("skinColor")
        self.skinColor.setStyleSheet("""
            QComboBox {
                color: black;  /* Seçilen öğenin rengi */
                background-color: white;
                font: 9pt "Segoe UI";
                border: 1px solid #9D5171;
                border-radius: 5px;
            }

            QComboBox QAbstractItemView {
                color: black; 
                background-color: white;
                selection-background-color: #9D5171;  
                selection-color: white;  
            }
        """)

        self.skinColor.addItems(["Select","Light", "Medium", "Dark"])

        self.verticalLayout.addWidget(self.skinColor)

        self.back_login = QPushButton(self.widget)
        self.back_login .setObjectName(u"back_login")
        self.back_login .setStyleSheet("""
                QPushButton {
                    color: #222222;
                    background-color: transparent;
                    border: none;
                    font-size: 12px;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
        self.verticalLayout.addWidget(self.back_login)
        self.back_login.clicked.connect(self.back_to_login)

        self.registerButton = QPushButton(self.widget)
        self.registerButton.setObjectName(u"registerButton")
        self.registerButton.setStyleSheet(u"background-color: rgb(157, 81, 113);")
        self.registerButton.setFixedWidth(350)
        self.verticalLayout.addWidget(self.registerButton, alignment=Qt.AlignCenter)
        
        
       
        self.registerButton.clicked.connect(self.on_register)

        self.main_layout.addWidget(self.horizontalLayoutWidget, 1)
        spacer = QSpacerItem(150, 50, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.main_layout.addItem(spacer)  
        self.main_layout.addWidget(self.widget, 2)
        spacer_right = QSpacerItem(100, 50, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.main_layout.addItem(spacer_right)  

        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Register")
        self.label.setText("Please Fill out form to Register!")
        self.label_2.setText("Name:")
        self.label_3.setText("Surname:")
        self.label_4.setText("Email :")
        self.label_5.setText("Password:")
        self.label_6.setText("Confirm Password:")
        self.label_7.setText("Select Your skin color:")
        self.back_login.setText("Yes I have an account? Login")
        self.registerButton.setText("Register")
      


    def back_to_login(self):
        from login_main import MainWindow
        self.back_window = MainWindow()
        self.back_window.show()
        self.window.close()  