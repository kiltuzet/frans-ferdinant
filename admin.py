from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QTabWidget, QDateTimeEdit, QDialog,
    QDialogButtonBox, QFormLayout, QShortcut
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QKeySequence
from db import Database

class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация администратора")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Логин:", self.username_input)
        form_layout.addRow("Пароль:", self.password_input)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.verify_credentials)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
    
    def verify_credentials(self):
        # Здесь должна быть проверка логина и пароля
        # В реальном приложении используйте хеширование и безопасное хранение паролей
        if self.username_input.text() == "admin" and self.password_input.text() == "admin123":
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные учетные данные")

class AdminPanel(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Панель администратора")
        self.setGeometry(200, 200, 800, 600)
        
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Логин", "Роль", "Дата регистрации"
        ])
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.users_table)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        btn_add = QPushButton("Добавить пользователя")
        btn_add.clicked.connect(self.add_user)
        button_layout.addWidget(btn_add)
        
        btn_delete = QPushButton("Удалить пользователя")
        btn_delete.clicked.connect(self.delete_user)
        button_layout.addWidget(btn_delete)
        
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_users)
        button_layout.addWidget(btn_refresh)
        
        layout.addLayout(button_layout)
    
    def load_users(self):
    # Загрузка пользователей из базы данных с подстановкой названия роли
        users = self.db.fetch_all("""
        SELECT u.id, u.login, t.type_name, u.created_at 
        FROM users u
        JOIN user_types t ON u.id_type_user = t.id
        ORDER BY u.id
    """)
    
        self.users_table.setRowCount(len(users))
        for row_idx, user in enumerate(users):
            self.users_table.setItem(row_idx, 0, QTableWidgetItem(str(user['id'])))
            self.users_table.setItem(row_idx, 1, QTableWidgetItem(user['login']))
            self.users_table.setItem(row_idx, 2, QTableWidgetItem(user['type_name']))
            self.users_table.setItem(row_idx, 3, QTableWidgetItem(str(user['created_at'])))
        self.users_table.resizeColumnsToContents()
    
    def add_user(self):
    # Сначала получаем список доступных ролей
        roles = self.db.fetch_all("SELECT id, type_name FROM user_types ORDER BY id")
    
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить пользователя")
    
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
    
        username_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
    
    # Создаем комбобокс с ролями
        role_combo = QComboBox()
        for role in roles:
            role_combo.addItem(role['type_name'], role['id'])
        form.addRow("Логин:", username_input)
        form.addRow("Пароль:", password_input)
        form.addRow("Роль:", role_combo)
    
        layout.addLayout(form)
    
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.save_user(
        dialog, 
        username_input.text(), 
        password_input.text(), 
        role_combo.currentData()  # Возвращает id выбранной роли
        ))
        buttons.rejected.connect(dialog.reject)
    
        layout.addWidget(buttons)
        dialog.exec_()
    
    def save_user(self, dialog, username, password, role):
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        try:
            # В реальном приложении пароль должен быть захэширован
            self.db.execute_query(
                "INSERT INTO users (login, password, id_type_user) VALUES (%s, %s, %s)",
                (username, password, role)
            )
            self.load_users()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить пользователя: {str(e)}")
    
    def delete_user(self):
        selected = self.users_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления")
            return
        
        user_id = self.users_table.item(selected[0].row(), 0).text()
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Вы уверены, что хотите удалить пользователя с ID {user_id}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM users WHERE id = %s", (user_id,))
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить пользователя: {str(e)}")

class BusDepotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Автобусный парк")
        self.setGeometry(100, 100, 900, 600)
        
        # Настройка горячих клавиш для админки

        
        self.init_ui()
        self.load_data()
   
    
    # ... (остальной код класса BusDepotApp остается без изменений)
