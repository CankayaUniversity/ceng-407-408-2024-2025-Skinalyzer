from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt
import mysql.connector
from PySide6.QtGui import QPixmap


class AnalysisResultsWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.setWindowTitle("Analysis Results History")
        self.setMinimumSize(600, 400)

        self.user_id = user_id
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        results = self.get_user_results()

        if not results:
            label = QLabel("No analysis results found for this user.")
            content_layout.addWidget(label)
        else:
            for res in results:
                card = QFrame()
                card.setStyleSheet("""
                    QFrame {
                        background-color: #f8f8f8;
                        border: 1px solid #ccc;
                        border-radius: 10px;
                        margin-bottom: 10px;
                    }
                """)
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(10, 10, 10, 10)

                card_layout.addWidget(QLabel(f"<b>Date:</b> {res['date']}"))
                card_layout.addWidget(QLabel(f"<b>Predicted Class:</b> {res['predicted_class']}"))
                card_layout.addWidget(QLabel(f"<b>Confidence:</b> {res['confidence']}%"))
                card_layout.addWidget(QLabel(f"<b>Risk Level:</b> {res['risk_level']}"))
                card_layout.addWidget(QLabel(f"<b>Description:</b> {res['description']}"))
                thumbnail_label = QLabel()
                thumbnail_pixmap = QPixmap(res['image_path'])
                if not thumbnail_pixmap.isNull():
                    thumbnail_pixmap = thumbnail_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    thumbnail_label.setPixmap(thumbnail_pixmap)
                    thumbnail_label.setStyleSheet("margin-top: 10px;")
                    card_layout.addWidget(thumbnail_label)
                else:
                    card_layout.addWidget(QLabel("Image could not be loaded."))

                content_layout.addWidget(card)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_user_results(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Tprksu.001",
                database="user_database"
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
                    "confidence": round(row[2] * 100, 2),
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
