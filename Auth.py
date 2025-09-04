from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
from db import Database

class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setModal(True)
        self.db = Database()

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.username_input.setToolTip("Введите ваш логин")
        self.password_input.setToolTip("Введите ваш пароль")

        form_layout.addRow("Логин:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)
        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verify_credentials)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.user_role = None
        self.user_id = None

    def verify_credentials(self):
        login = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        user = self.db.fetch_one("""
            SELECT u.id, u.login, u.password, t.type_name
            FROM users u
            JOIN user_types t ON u.id_type_user = t.id
            WHERE u.login = %s
        """, (login,))

        if user and user['password'] == password:
            self.user_role = user['type_name'].lower()
            self.user_id = user['id']
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные учетные данные")