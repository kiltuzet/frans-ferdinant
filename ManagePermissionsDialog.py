from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel,  QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QTabWidget, QDialog,
    QDialogButtonBox, QHeaderView,QCheckBox,QGroupBox
)


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
