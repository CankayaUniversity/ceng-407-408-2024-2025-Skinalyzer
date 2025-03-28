from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt

class AnalysisResultsWindow(QWidget):
    def __init__(self, results):
        super().__init__()
        self.setWindowTitle("Analysis Results History")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        if not results:
            label = QLabel("No analysis results yet.")
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
                card_layout.addWidget(QLabel(f"<b>Risk Level:</b> {res['risk_level']}"))
                card_layout.addWidget(QLabel("<b>Details:</b>"))
                for detail in res['details']:
                    card_layout.addWidget(QLabel(f"• {detail}"))
                card_layout.addWidget(QLabel(f"<b>Recommendation:</b> {res['recommendation']}"))

                content_layout.addWidget(card)

        scroll.setWidget(content)
        layout.addWidget(scroll)
