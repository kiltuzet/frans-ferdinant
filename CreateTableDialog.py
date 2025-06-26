from PyQt5.QtWidgets import (
 QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox,QDialog,
    QDialogButtonBox, QHeaderView,QCheckBox)



class CreateTableDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Создание новой таблицы")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        # Подключаем обработчик изменений в таблице
        self.columns_table.itemChanged.connect(self.update_sql_preview)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Название таблицы
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название таблицы:"))
        self.table_name_input = QLineEdit()
        self.table_name_input.textChanged.connect(self.update_sql_preview)
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
            # Получаем имя столбца
            col_item = self.columns_table.item(row, 0)
            col_name = col_item.text().strip() if col_item and col_item.text() else ""
            if not col_name:
                continue
                
            # Получаем тип данных
            type_widget = self.columns_table.cellWidget(row, 1)
            col_type = type_widget.currentText() if type_widget else "VARCHAR(255)"
            
            col_def = f"{col_name} {col_type}"
            
            # NOT NULL
            nn_widget = self.columns_table.cellWidget(row, 3)
            if nn_widget and nn_widget.isChecked():
                col_def += " NOT NULL"
                
            # AUTO_INCREMENT
            ai_widget = self.columns_table.cellWidget(row, 4)
            if ai_widget and ai_widget.isChecked():
                col_def += " AUTO_INCREMENT"
                
            # PRIMARY KEY
            pk_widget = self.columns_table.cellWidget(row, 2)
            if pk_widget and pk_widget.isChecked():
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
