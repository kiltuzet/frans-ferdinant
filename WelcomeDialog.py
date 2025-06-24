from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добро пожаловать!")
        self.setMinimumSize(350, 180)

        layout = QVBoxLayout(self)
        label = QLabel(
            "<h2>Добро пожаловать в систему управления автобусным парком!</h2>"
            "<p>Используйте вкладки для работы с автобусами, маршрутами, бронированием и поиска.</p>"
            "<p>Для входа в режим администратора нажмите <b>Ctrl+Shift+A</b>.</p>"
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        btn_ok = QPushButton("ОК")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)