import sys
import os
import hashlib
import shutil
import datetime
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem,
    QDateEdit
)
from PyQt5.QtCore import QDate
import openpyxl

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle("Вход")
        self.resize(300, 150)

        self.conn = sqlite3.connect("buspark_filled.db")
        self.cursor = self.conn.cursor()
        self.initDB()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.check_login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def initDB(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        self.conn.commit()
        hashed_admin = hash_password("admin")
        self.cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                            ("admin", hashed_admin, "admin"))
        self.conn.commit()

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        hashed_pass = hash_password(password)
        self.cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, hashed_pass))
        result = self.cursor.fetchone()
        if result:
            user_id, role = result
            self.on_success(user_id, role)
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

class BusParkApp(QWidget):
    def __init__(self, user_id, user_role):
        super().__init__()
        self.user_id = user_id
        self.user_role = user_role
        self.conn = sqlite3.connect("buspark_filled.db")
        self.cursor = self.conn.cursor()
        self.setWindowTitle("Система Автобусный парк")
        self.resize(900, 600)

        self.initDB()
        self.initUI()

    def initDB(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                license_number TEXT UNIQUE,
                phone TEXT
            )
        ''')
        self.conn.commit()

    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.createDriverTab(), "Водители")
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def createDriverTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        form = QHBoxLayout()
        form.addWidget(QLabel("Имя:"))
        self.driver_name = QLineEdit()
        form.addWidget(self.driver_name)

        form.addWidget(QLabel("Лицензия:"))
        self.driver_license = QLineEdit()
        form.addWidget(self.driver_license)

        form.addWidget(QLabel("Телефон:"))
        self.driver_phone = QLineEdit()
        form.addWidget(self.driver_phone)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.driver_save_btn = QPushButton("Добавить водителя")
        self.driver_save_btn.clicked.connect(self.saveDriver)
        btns.addWidget(self.driver_save_btn)

        self.driver_delete_btn = QPushButton("Удалить водителя")
        self.driver_delete_btn.clicked.connect(self.deleteDriver)
        btns.addWidget(self.driver_delete_btn)

        layout.addLayout(btns)

        self.driver_table = QTableWidget()
        layout.addWidget(self.driver_table)
        tab.setLayout(layout)
        self.loadDrivers()
        return tab

    def loadDrivers(self):
        self.cursor.execute("SELECT * FROM drivers")
        rows = self.cursor.fetchall()
        self.driver_table.setColumnCount(4)
        self.driver_table.setRowCount(len(rows))
        self.driver_table.setHorizontalHeaderLabels(["ID", "Имя", "Лицензия", "Телефон"])
        for row_idx, row in enumerate(rows):
            for col_idx, val in enumerate(row):
                self.driver_table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))

    def saveDriver(self):
        name = self.driver_name.text()
        lic = self.driver_license.text()
        phone = self.driver_phone.text()
        if not all([name, lic, phone]):
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны")
            return
        try:
            self.cursor.execute("INSERT INTO drivers (name, license_number, phone) VALUES (?, ?, ?)",
                                (name, lic, phone))
            self.conn.commit()
            self.loadDrivers()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Водитель с такой лицензией уже есть")

    def deleteDriver(self):
        row = self.driver_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите водителя для удаления")
            return
        driver_id = self.driver_table.item(row, 0).text()
        self.cursor.execute("DELETE FROM drivers WHERE id=?", (driver_id,))
        self.conn.commit()
        self.loadDrivers()
    def initDB(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                license_number TEXT UNIQUE,
                phone TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS buses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT,
                number TEXT UNIQUE,
                year INTEGER,
                status TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE,
                description TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bus_id INTEGER,
                date TEXT,
                type TEXT,
                FOREIGN KEY(bus_id) REFERENCES buses(id)
            )
        ''')
        self.conn.commit()

    def createBusTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        form = QHBoxLayout()
        form.addWidget(QLabel("Модель:"))
        self.bus_model = QLineEdit()
        form.addWidget(self.bus_model)

        form.addWidget(QLabel("Номер:"))
        self.bus_number = QLineEdit()
        form.addWidget(self.bus_number)

        form.addWidget(QLabel("Год:"))
        self.bus_year = QLineEdit()
        form.addWidget(self.bus_year)

        form.addWidget(QLabel("Статус:"))
        self.bus_status = QLineEdit()
        form.addWidget(self.bus_status)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.bus_save_btn = QPushButton("Добавить автобус")
        self.bus_save_btn.clicked.connect(self.saveBus)
        btns.addWidget(self.bus_save_btn)

        self.bus_delete_btn = QPushButton("Удалить автобус")
        self.bus_delete_btn.clicked.connect(self.deleteBus)
        btns.addWidget(self.bus_delete_btn)
        layout.addLayout(btns)

        self.bus_table = QTableWidget()
        layout.addWidget(self.bus_table)
        tab.setLayout(layout)
        self.loadBuses()
        return tab

    def saveBus(self):
        model = self.bus_model.text()
        number = self.bus_number.text()
        year = self.bus_year.text()
        status = self.bus_status.text()
        if not all([model, number, year, status]):
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны")
            return
        try:
            self.cursor.execute("INSERT INTO buses (model, number, year, status) VALUES (?, ?, ?, ?)",
                                (model, number, year, status))
            self.conn.commit()
            self.loadBuses()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Автобус с таким номером уже есть")

    def deleteBus(self):
        row = self.bus_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите автобус для удаления")
            return
        bus_id = self.bus_table.item(row, 0).text()
        self.cursor.execute("DELETE FROM buses WHERE id=?", (bus_id,))
        self.conn.commit()
        self.loadBuses()

    def loadBuses(self):
        self.cursor.execute("SELECT * FROM buses")
        rows = self.cursor.fetchall()
        self.bus_table.setColumnCount(5)
        self.bus_table.setRowCount(len(rows))
        self.bus_table.setHorizontalHeaderLabels(["ID", "Модель", "Номер", "Год", "Статус"])
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.bus_table.setItem(i, j, QTableWidgetItem(str(val)))

    def createRouteTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        form = QHBoxLayout()
        form.addWidget(QLabel("Номер маршрута:"))
        self.route_number = QLineEdit()
        form.addWidget(self.route_number)

        form.addWidget(QLabel("Описание:"))
        self.route_description = QLineEdit()
        form.addWidget(self.route_description)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.route_save_btn = QPushButton("Добавить маршрут")
        self.route_save_btn.clicked.connect(self.saveRoute)
        btns.addWidget(self.route_save_btn)

        self.route_delete_btn = QPushButton("Удалить маршрут")
        self.route_delete_btn.clicked.connect(self.deleteRoute)
        btns.addWidget(self.route_delete_btn)
        layout.addLayout(btns)

        self.route_table = QTableWidget()
        layout.addWidget(self.route_table)
        tab.setLayout(layout)
        self.loadRoutes()
        return tab

    def saveRoute(self):
        num = self.route_number.text()
        desc = self.route_description.text()
        if not all([num, desc]):
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны")
            return
        try:
            self.cursor.execute("INSERT INTO routes (number, description) VALUES (?, ?)", (num, desc))
            self.conn.commit()
            self.loadRoutes()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Маршрут с таким номером уже есть")

    def deleteRoute(self):
        row = self.route_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите маршрут")
            return
        route_id = self.route_table.item(row, 0).text()
        self.cursor.execute("DELETE FROM routes WHERE id=?", (route_id,))
        self.conn.commit()
        self.loadRoutes()

    def loadRoutes(self):
        self.cursor.execute("SELECT * FROM routes")
        rows = self.cursor.fetchall()
        self.route_table.setColumnCount(3)
        self.route_table.setRowCount(len(rows))
        self.route_table.setHorizontalHeaderLabels(["ID", "Номер", "Описание"])
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.route_table.setItem(i, j, QTableWidgetItem(str(val)))

    def createMaintenanceTab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        form = QHBoxLayout()
        form.addWidget(QLabel("ID автобуса:"))
        self.maint_bus_id = QLineEdit()
        form.addWidget(self.maint_bus_id)

        form.addWidget(QLabel("Дата (ГГГГ-ММ-ДД):"))
        self.maint_date = QLineEdit()
        form.addWidget(self.maint_date)

        form.addWidget(QLabel("Тип ТО:"))
        self.maint_type = QLineEdit()
        form.addWidget(self.maint_type)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.maint_save_btn = QPushButton("Добавить ТО")
        self.maint_save_btn.clicked.connect(self.saveMaintenance)
        btns.addWidget(self.maint_save_btn)

        self.maint_delete_btn = QPushButton("Удалить ТО")
        self.maint_delete_btn.clicked.connect(self.deleteMaintenance)
        btns.addWidget(self.maint_delete_btn)
        layout.addLayout(btns)

        self.maint_table = QTableWidget()
        layout.addWidget(self.maint_table)
        tab.setLayout(layout)
        self.loadMaintenance()
        return tab

    def saveMaintenance(self):
        bid = self.maint_bus_id.text()
        date = self.maint_date.text()
        mtype = self.maint_type.text()
        if not all([bid, date, mtype]):
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны")
            return
        try:
            self.cursor.execute("INSERT INTO maintenance (bus_id, date, type) VALUES (?, ?, ?)",
                                (bid, date, mtype))
            self.conn.commit()
            self.loadMaintenance()
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Ошибка при добавлении ТО")

    def deleteMaintenance(self):
        row = self.maint_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите ТО")
            return
        id = self.maint_table.item(row, 0).text()
        self.cursor.execute("DELETE FROM maintenance WHERE id=?", (id,))
        self.conn.commit()
        self.loadMaintenance()

    def loadMaintenance(self):
        self.cursor.execute("SELECT * FROM maintenance")
        rows = self.cursor.fetchall()
        self.maint_table.setColumnCount(4)
        self.maint_table.setRowCount(len(rows))
        self.maint_table.setHorizontalHeaderLabels(["ID", "Автобус", "Дата", "Тип"])
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.maint_table.setItem(i, j, QTableWidgetItem(str(val)))
    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.createDriverTab(), "Водители")
        self.tabs.addTab(self.createBusTab(), "Автобусы")
        self.tabs.addTab(self.createRouteTab(), "Маршруты")
        self.tabs.addTab(self.createMaintenanceTab(), "ТО")
        layout.addWidget(self.tabs)
        self.setLayout(layout)

# --- Точка входа ---
def main():
    app = QApplication(sys.argv)

    def start_main_app(user_id, user_role):
        window = BusParkApp(user_id, user_role)
        window.show()

    login = LoginWindow(start_main_app)
    login.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
