from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QTabWidget, QDateTimeEdit, QDialog,
    QDialogButtonBox, QFormLayout, QShortcut,QHeaderView,QCheckBox,QGroupBox,QTreeWidget,
    QTreeWidgetItem,QAction,QMenu
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QKeySequence
from db import Database

class CreateTableDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Создание новой таблицы")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Название таблицы
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название таблицы:"))
        self.table_name_input = QLineEdit()
        name_layout.addWidget(self.table_name_input)
        layout.addLayout(name_layout)
        
        # Таблица столбцов
        self.columns_table = QTableWidget(0, 6)
        self.columns_table.setHorizontalHeaderLabels([
            "Имя столбца", "Тип данных", "Первичный ключ", 
            "Не NULL", "Автоинкремент", "Внешний ключ"
        ])
        self.columns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.columns_table)
        
        # Кнопки управления столбцами
        btn_layout = QHBoxLayout()
        add_column_btn = QPushButton("Добавить столбец")
        add_column_btn.clicked.connect(self.add_column_row)
        remove_column_btn = QPushButton("Удалить выбранный")
        remove_column_btn.clicked.connect(self.remove_column_row)
        btn_layout.addWidget(add_column_btn)
        btn_layout.addWidget(remove_column_btn)
        layout.addLayout(btn_layout)
        
        # Предпросмотр SQL
        layout.addWidget(QLabel("SQL запрос:"))
        self.sql_preview = QLineEdit()
        self.sql_preview.setReadOnly(True)
        layout.addWidget(self.sql_preview)
        
        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.create_table)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.add_column_row()  # Добавляем первую строку по умолчанию
    
    def add_column_row(self):
        row = self.columns_table.rowCount()
        self.columns_table.insertRow(row)
    
    # Имя столбца
        name_item = QTableWidgetItem()
        self.columns_table.setItem(row, 0, name_item)
    
    # Тип данных
        type_combo = QComboBox()
        type_combo.addItems([
        "INT", "VARCHAR(255)", "TEXT", "DATE", "DATETIME", 
        "DECIMAL(10,2)", "BOOLEAN", "ENUM"
        ])
        self.columns_table.setCellWidget(row, 1, type_combo)
    
    # Первичный ключ
        pk_check = QCheckBox()
        self.columns_table.setCellWidget(row, 2, pk_check)
    
    # Не NULL
        nn_check = QCheckBox()
        self.columns_table.setCellWidget(row, 3, nn_check)
    
    # Автоинкремент
        ai_check = QCheckBox()
        self.columns_table.setCellWidget(row, 4, ai_check)
    
    # Внешний ключ (пока просто флажок)
        fk_check = QCheckBox()
        self.columns_table.setCellWidget(row, 5, fk_check)
    
    # Подключаем сигналы для обновления предпросмотра
        type_combo.currentTextChanged.connect(self.update_sql_preview)
        pk_check.stateChanged.connect(self.update_sql_preview)
        nn_check.stateChanged.connect(self.update_sql_preview)
        ai_check.stateChanged.connect(self.update_sql_preview)
        fk_check.stateChanged.connect(self.update_sql_preview)
    
    # Обновляем предпросмотр
        self.update_sql_preview()
    
    def remove_column_row(self):
        current_row = self.columns_table.currentRow()
        if current_row >= 0:
            self.columns_table.removeRow(current_row)
            self.update_sql_preview()
    
    def update_sql_preview(self):
        table_name = self.table_name_input.text().strip()
        if not table_name:
            self.sql_preview.setText("Введите название таблицы")
            return
            
        columns = []
        primary_keys = []
        
        for row in range(self.columns_table.rowCount()):
            col_name = self.columns_table.item(row, 0).text().strip() if self.columns_table.item(row, 0) else ""
            if not col_name:
                continue
                
            col_type = self.columns_table.cellWidget(row, 1).currentText()
            
            col_def = f"{col_name} {col_type}"
            
            if self.columns_table.cellWidget(row, 3).isChecked():  # NOT NULL
                col_def += " NOT NULL"
                
            if self.columns_table.cellWidget(row, 4).isChecked():  # AUTO_INCREMENT
                col_def += " AUTO_INCREMENT"
                
            if self.columns_table.cellWidget(row, 2).isChecked():  # PRIMARY KEY
                primary_keys.append(col_name)
                
            columns.append(col_def)
        
        if primary_keys:
            columns.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
        
        sql = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(columns) + "\n);"
        self.sql_preview.setText(sql)
    
    def create_table(self):
        table_name = self.table_name_input.text().strip()
        if not table_name:
            QMessageBox.warning(self, "Ошибка", "Введите название таблицы")
            return
            
        sql = self.sql_preview.text()
        try:
            self.db.execute_query(sql)
            QMessageBox.information(self, "Успех", "Таблица успешно создана")
            self.accept()
        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать таблицу:\n{str(err)}")

class ManagePermissionsDialog(QDialog):
    def __init__(self, db, table_name, parent=None):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        self.setWindowTitle(f"Управление правами: {table_name}")
        self.setMinimumSize(600, 400)
        
        self.init_ui()
        self.load_users()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Вкладки для разных типов прав
        self.tabs = QTabWidget()
        
        # Вкладка для существующих прав
        self.existing_perms_tab = QWidget()
        self.existing_perms_layout = QVBoxLayout(self.existing_perms_tab)
        self.existing_perms_layout.addWidget(QLabel("Текущие разрешения:"))
        
        self.perms_table = QTableWidget(0, 5)
        self.perms_table.setHorizontalHeaderLabels([
            "Пользователь", "Просмотр (SELECT)", "Добавление (INSERT)", 
            "Редактирование (UPDATE)", "Удаление (DELETE)"
        ])
        self.perms_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.existing_perms_layout.addWidget(self.perms_table)
        
        self.tabs.addTab(self.existing_perms_tab, "Текущие права")
        
        # Вкладка для добавления новых прав
        self.add_perms_tab = QWidget()
        self.add_perms_layout = QVBoxLayout(self.add_perms_tab)
        
        # Выбор пользователя
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Пользователь:"))
        self.user_combo = QComboBox()
        user_layout.addWidget(self.user_combo)
        self.add_perms_layout.addLayout(user_layout)
        
        # Права
        perms_group = QGroupBox("Права доступа")
        perms_layout = QVBoxLayout()
        
        self.select_cb = QCheckBox("Просмотр (SELECT)")
        self.insert_cb = QCheckBox("Добавление (INSERT)")
        self.update_cb = QCheckBox("Редактирование (UPDATE)")
        self.delete_cb = QCheckBox("Удаление (DELETE)")
        
        perms_layout.addWidget(self.select_cb)
        perms_layout.addWidget(self.insert_cb)
        perms_layout.addWidget(self.update_cb)
        perms_layout.addWidget(self.delete_cb)
        perms_group.setLayout(perms_layout)
        self.add_perms_layout.addWidget(perms_group)
        
        # Кнопка добавления
        add_btn = QPushButton("Добавить права")
        add_btn.clicked.connect(self.add_permission)
        self.add_perms_layout.addWidget(add_btn)
        
        self.tabs.addTab(self.add_perms_tab, "Добавить права")
        
        layout.addWidget(self.tabs)
        
        # Кнопки диалога
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_users(self):
        self.user_combo.clear()
        
        # Загрузка пользователей
        users = self.db.fetch_all("SELECT id, login FROM users")
        for user in users:
            self.user_combo.addItem(user['login'], user['id'])
        
        # Загрузка текущих прав
        self.perms_table.setRowCount(0)
        permissions = self.db.fetch_all("""
            SELECT u.login, p.can_select, p.can_insert, p.can_update, p.can_delete
            FROM user_permissions p
            JOIN users u ON p.user_id = u.id
            WHERE p.table_name = %s
        """, (self.table_name,))
        
        for row_idx, perm in enumerate(permissions):
            self.perms_table.insertRow(row_idx)
            self.perms_table.setItem(row_idx, 0, QTableWidgetItem(perm['login']))
            self.perms_table.setItem(row_idx, 1, QTableWidgetItem("✓" if perm['can_select'] else "✗"))
            self.perms_table.setItem(row_idx, 2, QTableWidgetItem("✓" if perm['can_insert'] else "✗"))
            self.perms_table.setItem(row_idx, 3, QTableWidgetItem("✓" if perm['can_update'] else "✗"))
            self.perms_table.setItem(row_idx, 4, QTableWidgetItem("✓" if perm['can_delete'] else "✗"))
    
    def add_permission(self):
        user_id = self.user_combo.currentData()
        if not user_id:
            return
            
        permissions = {
            'select': self.select_cb.isChecked(),
            'insert': self.insert_cb.isChecked(),
            'update': self.update_cb.isChecked(),
            'delete': self.delete_cb.isChecked()
        }
        
        if not any(permissions.values()):
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы одно разрешение")
            return
            
        try:
            # Проверяем существующие права
            existing = self.db.fetch_one(
                "SELECT 1 FROM user_permissions WHERE user_id = %s AND table_name = %s",
                (user_id, self.table_name)
            )
            
            if existing:
                # Обновляем существующие права
                self.db.execute_query("""
                    UPDATE user_permissions
                    SET can_select = %s, can_insert = %s, can_update = %s, can_delete = %s
                    WHERE user_id = %s AND table_name = %s
                """, (
                    permissions['select'], permissions['insert'],
                    permissions['update'], permissions['delete'],
                    user_id, self.table_name
                ))
            else:
                # Добавляем новые права
                self.db.execute_query("""
                    INSERT INTO user_permissions 
                    (user_id, table_name, can_select, can_insert, can_update, can_delete)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    user_id, self.table_name,
                    permissions['select'], permissions['insert'],
                    permissions['update'], permissions['delete']
                ))
            
            QMessageBox.information(self, "Успех", "Права успешно обновлены")
            self.load_users()
        except Exception as err:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить права:\n{str(err)}")


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
        self.setMinimumSize(1000, 700)
        
        self.init_ui()
        self.load_users()
        self.load_database_structure()
    
    def init_ui(self):
        self.tabs = QTabWidget()
        
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
        db_layout.addWidget(self.db_tree)
        
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
            
        if context_menu.actions():
            context_menu.exec_(self.db_tree.viewport().mapToGlobal(position))
    
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
