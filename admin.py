from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QTabWidget, QDialog,
    QDialogButtonBox, QFormLayout,QTreeWidget,
    QTreeWidgetItem,QAction,QMenu,
    QLabel
)
from PyQt5.QtCore import Qt
from db import Database
from ManagePermissionsDialog import ManagePermissionsDialog
from CreateTableDialog import CreateTableDialog
from EditTableDialog import EditTableDialog


class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация администратора")
        self.setModal(True)
        self.db = Database()  # Добавьте это, если нет доступа к db из родителя

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
        login = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        # Получаем пользователя с ролью "Администратор"
        user = self.db.fetch_one("""
            SELECT u.id, u.login, u.password, t.type_name
            FROM users u
            JOIN user_types t ON u.id_type_user = t.id
            WHERE u.login = %s
        """, (login,))

        if user and user['password'] == password and user['type_name'].lower() == "администратор":
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные учетные данные или недостаточно прав")

class AdminPanel(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Панель администратора")
        self.setMinimumSize(1000, 700)
        self.page_size = 100
        self.current_page = 0
        self.current_table = None  # Для хранения выбранной таблицы
        self.init_ui()
        self.load_users()
        self.load_database_structure()
        self.db_tree.installEventFilter(self)

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)  # табы будут занимать всё доступное пространство
        
        # Вкладка управления пользователями
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)
        
        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Логин", "Роль", "Дата регистрации"
        ])
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        users_layout.addWidget(self.users_table)
        
        # Кнопки управления пользователями
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
        
        users_layout.addLayout(button_layout)
        
        # Вкладка управления БД
        db_tab = QWidget()
        db_layout = QVBoxLayout(db_tab)
        
        # Дерево структуры БД
        self.db_tree = QTreeWidget()
        self.db_tree.setHeaderLabel("Структура базы данных")
        self.db_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.db_tree.customContextMenuRequested.connect(self.show_db_context_menu)
        self.db_tree.itemClicked.connect(self.show_table_data)  # <-- добавьте эту строку
        db_layout.addWidget(self.db_tree)
        
        # Таблица данных
        self.data_table = QTableWidget()
        db_layout.addWidget(self.data_table)

        # --- КОНТРОЛЫ ПАГИНАЦИИ ---
        self.pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Назад")
        self.next_btn = QPushButton("Вперёд")
        self.page_label = QLabel("Страница 1")
        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)
        self.pagination_layout.addWidget(self.prev_btn)
        self.pagination_layout.addWidget(self.page_label)
        self.pagination_layout.addWidget(self.next_btn)
        db_layout.addLayout(self.pagination_layout)
        
        # Добавляем вкладки
        self.tabs.addTab(users_tab, "Управление пользователями")
        self.tabs.addTab(db_tab, "Управление базой данных")
        
        # Основной лейаут
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)
        
        # Проверяем существование таблицы прав
        self.check_permissions_table()
    
    def check_permissions_table(self):
        # Проверяем существование таблицы user_permissions
        tables = self.db.fetch_all("SHOW TABLES")
        table_names = [list(table.values())[0] for table in tables]
        
        if 'user_permissions' not in table_names:
            try:
                self.db.execute_query("""
                    CREATE TABLE user_permissions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        table_name VARCHAR(64) NOT NULL,
                        can_select BOOLEAN NOT NULL DEFAULT 0,
                        can_insert BOOLEAN NOT NULL DEFAULT 0,
                        can_update BOOLEAN NOT NULL DEFAULT 0,
                        can_delete BOOLEAN NOT NULL DEFAULT 0,
                        UNIQUE KEY (user_id, table_name),
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
                QMessageBox.information(self, "Информация", 
                                       "Таблица прав пользователей создана автоматически")
            except Exception as e:
                QMessageBox.warning(self, "Предупреждение", 
                                   f"Не удалось создать таблицу прав: {str(e)}")
    
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
    
    def load_database_structure(self):
        self.db_tree.clear()
        db_item = QTreeWidgetItem(self.db_tree, ["База данных: bus_depot"])
        
        # Загрузка таблиц
        tables = self.db.fetch_all("SHOW TABLES")
        table_names = [list(table.values())[0] for table in tables]
        
        for table in table_names:
            table_item = QTreeWidgetItem(db_item, [table])
            table_item.setData(0, Qt.UserRole, table)
            
            # Загрузка столбцов для таблицы
            columns = self.db.fetch_all(f"DESCRIBE {table}")
            for column in columns:
                col_info = f"{column['Field']} ({column['Type']})"
                if column['Key'] == "PRI":
                    col_info += " 🔑"
                elif column['Key'] == "MUL":
                    col_info += " 🔗"
                QTreeWidgetItem(table_item, [col_info])
        
        db_item.setExpanded(True)
    
    def show_db_context_menu(self, position):
        item = self.db_tree.currentItem()
        if not item:
            return
            
        context_menu = QMenu()
        
        # Контекстное меню для корневого элемента (БД)
        if item.text(0).startswith("База данных"):
            create_table_action = QAction("Создать новую таблицу", self)
            create_table_action.triggered.connect(self.create_new_table)
            context_menu.addAction(create_table_action)
            
        # Контекстное меню для таблицы
        elif item.parent() and item.parent().text(0).startswith("База данных"):
            table_name = item.data(0, Qt.UserRole)
            
            manage_permissions_action = QAction("Управление правами", self)
            manage_permissions_action.triggered.connect(
                lambda: self.manage_permissions(table_name)
            )
            context_menu.addAction(manage_permissions_action)

            edit_table_action = QAction("Редактировать таблицу", self)
            edit_table_action.triggered.connect(
                lambda: self.edit_table(table_name)
            )
            context_menu.addAction(edit_table_action)
            
        if context_menu.actions():
            context_menu.exec_(self.db_tree.viewport().mapToGlobal(position))

    def edit_table(self, table_name):
        dialog = EditTableDialog(self.db, table_name, self)
        dialog.exec_()
        self.load_database_structure()  # Always reload after dialog closes
    
    def create_new_table(self):
        dialog = CreateTableDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_database_structure()
    
    def manage_permissions(self, table_name):
        dialog = ManagePermissionsDialog(self.db, table_name, self)
        dialog.exec_()
    
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

    def eventFilter(self, obj, event):
        if obj == self.db_tree and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Delete:
                item = self.db_tree.currentItem()
                if not item:
                    return True
                parent = item.parent()
                # Если выбран столбец (есть родитель и родитель — таблица)
                if parent and parent.parent() and parent.parent().text(0).startswith("База данных"):
                    table_name = parent.data(0, Qt.UserRole)
                    col_info = item.text(0)
                    col_name = col_info.split(" ")[0]
                    reply = QMessageBox.question(self, "Удалить столбец", f"Удалить столбец '{col_name}' из таблицы '{table_name}'?", QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        try:
                            self.db.execute_query(f"ALTER TABLE {table_name} DROP COLUMN {col_name}")
                            QMessageBox.information(self, "Успех", "Столбец удалён")
                            self.load_database_structure()
                        except Exception as e:
                            QMessageBox.critical(self, "Ошибка", str(e))
                    return True
                # Если выбран элемент таблицы (есть родитель и он — корень)
                elif parent and parent.text(0).startswith("База данных"):
                    table_name = item.data(0, Qt.UserRole)
                    reply = QMessageBox.question(self, "Удалить таблицу", f"Удалить таблицу '{table_name}'?", QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        try:
                            self.db.execute_query(f"DROP TABLE {table_name}")
                            QMessageBox.information(self, "Успех", "Таблица удалена")
                            self.load_database_structure()
                        except Exception as e:
                            QMessageBox.critical(self, "Ошибка", str(e))
                    return True
        return super().eventFilter(obj, event)

    def show_table_data(self, item, column, page=None):
        table_name = item.data(0, Qt.UserRole)
        if not table_name or not isinstance(table_name, str):
            return
        self.current_table = table_name
        if page is None:
            self.current_page = 0
        offset = self.current_page * self.page_size
        print(f"Показываем данные таблицы: {table_name}, страница: {self.current_page }, смещение: {offset}")
        rows = self.db.fetch_all(
            f"SELECT * FROM {table_name} LIMIT %s OFFSET %s", (self.page_size, offset)
        )
        print(f"Получено строк: {len(rows)}")
        if len(rows)==0:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.page_label.setText(f"Страница {self.current_page + 1}")
            print("Нет данных для отображения")
            return
        self.data_table.setColumnCount(len(rows[0]))
        self.data_table.setHorizontalHeaderLabels(rows[0].keys())
        self.data_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, key in enumerate(row):
                self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(row[key])))
        self.data_table.resizeColumnsToContents()
        self.page_label.setText(f"Страница {self.current_page + 1}")
        
    #пагинация вперед
    def next_page(self):
        if not self.current_table:
            print("Нет выбранной таблицы")
            return
        # Проверяем, есть ли данные на следующей странице
        offset = (self.current_page + 1) * self.page_size
        rows = self.db.fetch_all(
            f"SELECT * FROM {self.current_table} LIMIT %s OFFSET %s", (self.page_size, offset)
        )
        if not rows:
            QMessageBox.information(self, "Информация", "Больше нет данных для отображения.")
            return
        self.current_page += 1
        item = QTreeWidgetItem([self.current_table])
        item.setData(0, Qt.UserRole, self.current_table)
        self.show_table_data(item, 0, self.current_page)
        print(self.current_page)

    #пагинация назад
    def prev_page(self):
        if not self.current_table or self.current_page == 0:
            return
        self.current_page -= 1
        item = QTreeWidgetItem([self.current_table])
        item.setData(0, Qt.UserRole, self.current_table)
        self.show_table_data(item, 0, self.current_page)

class BusDepotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Автобусный парк")
        self.setGeometry(100, 100, 900, 600)
        
        # Настройка горячих клавиш для админки

        
        self.init_ui()
        self.load_data()

        # Устанавливаем стиль для табов
        self.set_tab_style()

    def set_tab_style(self):
        style = """
        QTabBar::tab {
            background: #e9ecef;
            color: #333;
            padding: 6px 12px;
            border: 1px solid #57b7c1;
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            margin-right: 2px;
            min-width: 180px;
            max-width: 300px;
            min-height: 28px;
            font-size: 15px;
            font-weight: 500;
            z-index: 1;
            text-align: center;
            white-space: normal;
            height: 40px;
        }
        """
        self.tabs.setStyleSheet(style)
