from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialogButtonBox, QComboBox,
    QWidget,QInputDialog
)
from PyQt5.QtCore import Qt

class EditTableDialog(QDialog):
    def __init__(self, db, table_name, parent=None):
        super().__init__(parent)
        self.db = db
        self.table_name = table_name
        self.setWindowTitle(f"Редактировать таблицу: {table_name}")
        self.setMinimumSize(700, 500)
        self.init_ui()
        self.load_columns()
        # Устанавливаем фильтр событий
        self.columns_table.installEventFilter(self)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Rename table
        rename_layout = QHBoxLayout()
        rename_layout.addWidget(QLabel("Новое имя таблицы:"))
        self.rename_input = QLineEdit(self.table_name)
        rename_layout.addWidget(self.rename_input)
        btn_rename = QPushButton("Переименовать")
        btn_rename.clicked.connect(self.rename_table)
        rename_layout.addWidget(btn_rename)
        layout.addLayout(rename_layout)

        # Columns table
        self.columns_table = QTableWidget(0, 3)
        self.columns_table.setHorizontalHeaderLabels(["Имя столбца", "Тип данных", "Действие"])
        self.columns_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.columns_table)

        # Add column
        add_layout = QHBoxLayout()
        self.new_col_name = QLineEdit()
        self.new_col_name.setPlaceholderText("Имя столбца")
        self.new_col_type = QComboBox()
        self.new_col_type.addItems(["INT", "VARCHAR(255)", "TEXT", "DATE", "DATETIME", "DECIMAL(10,2)", "BOOLEAN"])
        btn_add_col = QPushButton("Добавить столбец")
        btn_add_col.clicked.connect(self.add_column)
        add_layout.addWidget(self.new_col_name)
        add_layout.addWidget(self.new_col_type)
        add_layout.addWidget(btn_add_col)
        layout.addLayout(add_layout)

        # Remove table
        btn_remove_table = QPushButton("Удалить таблицу")
        btn_remove_table.clicked.connect(self.remove_table)
        layout.addWidget(btn_remove_table)

        # Close
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_columns(self):
        self.columns_table.setRowCount(0)
        columns = self.db.fetch_all(f"DESCRIBE {self.table_name}")
        for idx, col in enumerate(columns):
            self.columns_table.insertRow(idx)
            self.columns_table.setItem(idx, 0, QTableWidgetItem(col['Field']))
            self.columns_table.setItem(idx, 1, QTableWidgetItem(col['Type']))
            btn_rename = QPushButton("Переименовать")
            btn_rename.clicked.connect(lambda _, row=idx: self.rename_column(row))
            btn_remove = QPushButton("Удалить")
            btn_remove.clicked.connect(lambda _, row=idx: self.remove_column(row))
            action_layout = QHBoxLayout()
            action_widget = QWidget()
            action_layout.addWidget(btn_rename)
            action_layout.addWidget(btn_remove)
            action_layout.setContentsMargins(0,0,0,0)
            action_widget.setLayout(action_layout)
            self.columns_table.setCellWidget(idx, 2, action_widget)

    def rename_table(self):
        new_name = self.rename_input.text().strip()
        if not new_name or new_name == self.table_name:
            return
        try:
            self.db.execute_query(f"RENAME TABLE {self.table_name} TO {new_name}")
            QMessageBox.information(self, "Успех", "Таблица переименована")
            self.table_name = new_name
            self.setWindowTitle(f"Редактировать таблицу: {new_name}")
            self.accept()  # <-- Add this line
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_column(self):
        col_name = self.new_col_name.text().strip()
        col_type = self.new_col_type.currentText()
        if not col_name:
            return
        try:
            self.db.execute_query(f"ALTER TABLE {self.table_name} ADD COLUMN {col_name} {col_type}")
            QMessageBox.information(self, "Успех", "Столбец добавлен")
            self.load_columns()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def rename_column(self, row):
        old_name = self.columns_table.item(row, 0).text()
        new_name, ok = QInputDialog.getText(self, "Переименовать столбец", f"Новое имя для {old_name}:")
        if ok and new_name and new_name != old_name:
            col_type = self.columns_table.item(row, 1).text()
            try:
                self.db.execute_query(f"ALTER TABLE {self.table_name} CHANGE {old_name} {new_name} {col_type}")
                QMessageBox.information(self, "Успех", "Столбец переименован")
                self.load_columns()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def remove_column(self, row):
        col_name = self.columns_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удалить столбец", f"Удалить столбец {col_name}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query(f"ALTER TABLE {self.table_name} DROP COLUMN {col_name}")
                QMessageBox.information(self, "Успех", "Столбец удалён")
                self.load_columns()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def remove_table(self):
        reply = QMessageBox.question(self, "Удалить таблицу", f"Удалить таблицу {self.table_name}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query(f"DROP TABLE {self.table_name}")
                QMessageBox.information(self, "Успех", "Таблица удалена")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def eventFilter(self, obj, event):
        #нужно расставить логи
        print("Event Filter Triggered")
        # Проверяем, что событие произошло на таблице столбцов
        if obj == self.columns_table and event.type() == event.KeyPress:
            print("Key Pressed in Columns Table")
            # Проверяем, что нажата клавиша Delete
            if event.key() == Qt.Key_Delete:
                print("Delete Key Pressed")
                # Удаляем текущую строку
                row = self.columns_table.currentRow()
                print(f"Current Row: {row}")
                if row >= 0:
                    print(f"Removing Column at Row: {row}")
                    #self.columns_table.removeRow(row)
                    self.remove_column(row)
                return True  # событие обработано
        return super().eventFilter(obj, event)