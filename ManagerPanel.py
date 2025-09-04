import requests
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QMessageBox, QFormLayout, 
    QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

from db import Database

load_dotenv()
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY").replace('"', '').replace("'", "")

class ManagerPanel(QDialog):
    def __init__(self, db, parent=None, user_id=None):
        super().__init__(parent)
        self.db = db
        self.user_id = user_id  # сохраняем user_id
        self.setWindowTitle("Панель диспетчера")
        self.setMinimumSize(1100, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Вкладка остановок
        self.stops_tab = QWidget()
        self.stops_layout = QVBoxLayout(self.stops_tab)
        self.stops_table = QTableWidget()
        self.stops_layout.addWidget(self.stops_table)
        btn_update_stops = QPushButton("Обновить остановки")
        btn_update_stops.clicked.connect(self.load_stops)
        btn_add_stop = QPushButton("Добавить остановку")
        btn_add_stop.clicked.connect(self.add_stop_dialog)
        btn_edit_stop = QPushButton("Редактировать остановку")
        btn_edit_stop.clicked.connect(self.edit_stop_dialog)
        btn_delete_stop = QPushButton("Удалить остановку")
        btn_delete_stop.clicked.connect(self.delete_stop)
        self.stops_layout.addWidget(btn_update_stops)
        self.stops_layout.addWidget(btn_add_stop)
        self.stops_layout.addWidget(btn_edit_stop)
        self.stops_layout.addWidget(btn_delete_stop)
        self.tabs.addTab(self.stops_tab, "Остановки")

        # Вкладка маршрутов
        self.routes_tab = QWidget()
        self.routes_layout = QVBoxLayout(self.routes_tab)
        self.routes_table = QTableWidget()
        self.routes_layout.addWidget(self.routes_table)
        btn_update_routes = QPushButton("Обновить маршруты")
        btn_update_routes.clicked.connect(self.load_routes)
        btn_add_route = QPushButton("Добавить маршрут")
        btn_add_route.clicked.connect(self.add_route_dialog)
        btn_edit_route = QPushButton("Редактировать маршрут")
        btn_edit_route.clicked.connect(self.edit_route_dialog)
        btn_delete_route = QPushButton("Удалить маршрут")
        btn_delete_route.clicked.connect(self.delete_route)
        self.routes_layout.addWidget(btn_update_routes)
        self.routes_layout.addWidget(btn_add_route)
        self.routes_layout.addWidget(btn_edit_route)
        self.routes_layout.addWidget(btn_delete_route)
        self.tabs.addTab(self.routes_tab, "Маршруты")

        # Вкладка остановок на маршруте
        self.route_stops_tab = QWidget()
        self.route_stops_layout = QVBoxLayout(self.route_stops_tab)
        self.route_stops_table = QTableWidget()
        self.route_stops_layout.addWidget(self.route_stops_table)
        btn_update_route_stops = QPushButton("Обновить остановки на маршруте")
        btn_update_route_stops.clicked.connect(self.load_route_stops)
        btn_add_route_stop = QPushButton("Добавить точку на маршрут")
        btn_add_route_stop.clicked.connect(self.add_route_stop_dialog)
        btn_edit_route_stop = QPushButton("Редактировать точку на маршруте")
        btn_edit_route_stop.clicked.connect(self.edit_route_stop_dialog)
        btn_delete_route_stop = QPushButton("Удалить точку на маршруте")
        btn_delete_route_stop.clicked.connect(self.delete_route_stop)
        self.route_stops_layout.addWidget(btn_update_route_stops)
        self.route_stops_layout.addWidget(btn_add_route_stop)
        self.route_stops_layout.addWidget(btn_edit_route_stop)
        self.route_stops_layout.addWidget(btn_delete_route_stop)
        self.tabs.addTab(self.route_stops_tab, "Остановки на маршруте")

        # Вкладка назначений
        self.assignments_tab = QWidget()
        self.assignments_layout = QVBoxLayout(self.assignments_tab)
        self.assignments_table = QTableWidget()
        self.assignments_layout.addWidget(self.assignments_table)
        btn_update_assignments = QPushButton("Обновить назначения")
        btn_update_assignments.clicked.connect(self.load_assignments)
        btn_add_assignment = QPushButton("Добавить назначение")
        btn_add_assignment.clicked.connect(self.add_assignment_dialog)
        btn_edit_assignment = QPushButton("Редактировать назначение")
        btn_edit_assignment.clicked.connect(self.edit_assignment_dialog)
        btn_delete_assignment = QPushButton("Удалить назначение")
        btn_delete_assignment.clicked.connect(self.delete_assignment)
        self.assignments_layout.addWidget(btn_update_assignments)
        self.assignments_layout.addWidget(btn_add_assignment)
        self.assignments_layout.addWidget(btn_edit_assignment)
        self.assignments_layout.addWidget(btn_delete_assignment)
        self.tabs.addTab(self.assignments_tab, "Назначения")

        self.load_stops()
        self.load_routes()
        self.load_route_stops()
        self.load_assignments()

    # --- CRUD для остановок ---
    def load_stops(self):
        stops = self.db.fetch_all("SELECT id, name, address, latitude, longitude FROM stops ORDER BY id")
        self.stops_table.setColumnCount(5)
        self.stops_table.setHorizontalHeaderLabels(["ID", "Название", "Адрес", "Широта", "Долгота"])
        self.stops_table.setRowCount(len(stops))
        for row, stop in enumerate(stops):
            self.stops_table.setItem(row, 0, QTableWidgetItem(str(stop['id'])))
            self.stops_table.setItem(row, 1, QTableWidgetItem(stop['name']))
            self.stops_table.setItem(row, 2, QTableWidgetItem(stop['address']))
            self.stops_table.setItem(row, 3, QTableWidgetItem(str(stop['latitude'])))
            self.stops_table.setItem(row, 4, QTableWidgetItem(str(stop['longitude'])))
        self.stops_table.resizeColumnsToContents()

    def add_stop_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить остановку")
        layout = QFormLayout(dialog)
        name_input = QLineEdit()
        address_input = QLineEdit()
        layout.addRow("Название:", name_input)
        layout.addRow("Адрес:", address_input)
        btn_geocode = QPushButton("Получить координаты")
        coords_label = QLabel("Широта: —, Долгота: —")
        lat, lon = [None], [None]

        def geocode():
            address = address_input.text().strip()
            if not address:
                QMessageBox.warning(dialog, "Ошибка", "Введите адрес")
                return
            yandex_url = "https://geocode-maps.yandex.ru/1.x/"
            params = {
                "apikey": YANDEX_API_KEY,
                "geocode": address,
                "format": "json"
            }
            try:
                resp = requests.get(yandex_url, params=params, timeout=5)
                resp.raise_for_status()
                geo = resp.json()
                pos = geo['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                lon[0], lat[0] = map(float, pos.split())
                coords_label.setText(f"Широта: {lat[0]}, Долгота: {lon[0]}")
            except Exception:
                coords_label.setText("Ошибка геокодирования")
        btn_geocode.clicked.connect(geocode)
        layout.addRow(btn_geocode, coords_label)

        btn_pick_on_map = QPushButton("Выбрать на карте")
        layout.addRow(btn_pick_on_map)
        lat, lon = [None], [None]

        def pick_on_map():
            coords = MapPointDialog.get_point(YANDEX_API_KEY, dialog)
            if coords:
                lat[0], lon[0] = coords
                coords_label.setText(f"Широта: {lat[0]}, Долгота: {lon[0]}")

        btn_pick_on_map.clicked.connect(pick_on_map)
        layout.addRow(btn_pick_on_map, coords_label)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.save_stop(dialog, name_input.text(), address_input.text(), lat[0], lon[0]))
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec_()

    def save_stop(self, dialog, name, address, lat, lon):
        if not name or not address or lat is None or lon is None:
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля и получите координаты")
            return
        try:
            self.db.execute_query(
                "INSERT INTO stops (name, address, latitude, longitude) VALUES (%s, %s, %s, %s)",
                (name, address, lat, lon)
            )
            self.load_stops()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить остановку: {str(e)}")

    def edit_stop_dialog(self):
        if not self.has_permission('stops', 'can_update'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на редактирование остановок.")
            return
        selected_row = self.stops_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите остановку для редактирования")
            return

        stop_id = self.stops_table.item(selected_row, 0).text()
        stop = self.db.fetch_one("SELECT id, name, address, latitude, longitude FROM stops WHERE id = %s", (stop_id,))

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать остановку")
        layout = QFormLayout(dialog)
        name_input = QLineEdit(stop['name'])
        address_input = QLineEdit(stop['address'])
        layout.addRow("Название:", name_input)
        layout.addRow("Адрес:", address_input)
        btn_geocode = QPushButton("Получить координаты")
        coords_label = QLabel(f"Широта: {stop['latitude']}, Долгота: {stop['longitude']}")
        lat, lon = [stop['latitude']], [stop['longitude']]

        def geocode():
            address = address_input.text().strip()
            if not address:
                QMessageBox.warning(dialog, "Ошибка", "Введите адрес")
                return
            yandex_url = "https://geocode-maps.yandex.ru/1.x/"
            params = {
                "apikey": YANDEX_API_KEY,
                "geocode": address,
                "format": "json"
            }
            try:
                resp = requests.get(yandex_url, params=params, timeout=5)
                resp.raise_for_status()
                geo = resp.json()
                pos = geo['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                lon[0], lat[0] = map(float, pos.split())
                coords_label.setText(f"Широта: {lat[0]}, Долгота: {lon[0]}")
            except Exception:
                coords_label.setText("Ошибка геокодирования")
        btn_geocode.clicked.connect(geocode)
        layout.addRow(btn_geocode, coords_label)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.update_stop(dialog, stop_id, name_input.text(), address_input.text(), lat[0], lon[0]))
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec_()

    def update_stop(self, dialog, stop_id, name, address, lat, lon):
        if not name or not address or lat is None or lon is None:
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля и получите координаты")
            return
        try:
            self.db.execute_query(
                "UPDATE stops SET name = %s, address = %s, latitude = %s, longitude = %s WHERE id = %s",
                (name, address, lat, lon, stop_id)
            )
            self.load_stops()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось обновить остановку: {str(e)}")

    def has_permission(self, table, action):
        user_id = self.user_id  # теперь берём user_id напрямую
        if not user_id:
            return False
        perm = self.db.fetch_one(
            f"SELECT {action} FROM user_permissions WHERE user_id = %s AND table_name = %s",
            (user_id, table)
        )
        return perm and perm.get(action) == 1

    def delete_stop(self):
        if not self.has_permission('stops', 'can_delete'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на удаление остановок.")
            return
        row = self.stops_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите остановку для удаления.")
            return
        stop_id = self.stops_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удалить", "Удалить выбранную остановку?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM stops WHERE id = %s", (stop_id,))
                self.load_stops()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить остановку: {str(e)}")
                
    def delete_route_stop(self):
        if not self.has_permission('route_stops', 'can_delete'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на удаление.")
            return
        row = self.route_stops_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите точку для удаления.")
            return
        route_stop_id = self.route_stops_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удалить", "Удалить выбранную точку?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM route_stops WHERE id = %s", (route_stop_id,))
                self.load_route_stops()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить точку: {str(e)}")

    # --- CRUD для маршрутов ---
    def load_routes(self):
        routes = self.db.fetch_all("SELECT id, route_number, route_name FROM routes ORDER BY id")
        self.routes_table.setColumnCount(3)
        self.routes_table.setHorizontalHeaderLabels(["ID", "Номер маршрута", "Название"])
        self.routes_table.setRowCount(len(routes))
        for row, route in enumerate(routes):
            self.routes_table.setItem(row, 0, QTableWidgetItem(str(route['id'])))
            self.routes_table.setItem(row, 1, QTableWidgetItem(str(route['route_number'])))
            self.routes_table.setItem(row, 2, QTableWidgetItem(route['route_name']))
        self.routes_table.resizeColumnsToContents()

    def add_route_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить маршрут")
        layout = QFormLayout(dialog)
        route_number_input = QLineEdit()
        # Выбор начальной и конечной остановки
        stops = self.db.fetch_all("SELECT id, name FROM stops ORDER BY name")
        start_combo = QComboBox()
        end_combo = QComboBox()
        for stop in stops:
            start_combo.addItem(stop['name'], stop['id'])
            end_combo.addItem(stop['name'], stop['id'])
        layout.addRow("Номер маршрута:", route_number_input)
        layout.addRow("Начальная точка:", start_combo)
        layout.addRow("Конечная точка:", end_combo)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.save_route(
            dialog,
            route_number_input.text(),
            start_combo.currentData(),
            end_combo.currentData(),
            start_combo.currentText(),
            end_combo.currentText()
        ))
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec_()

    def save_route(self, dialog, route_number, start_id, end_id, start_name, end_name):
        if not route_number or not start_id or not end_id or start_id == end_id:
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля и выберите разные точки")
            return
        route_name = f"{start_name} — {end_name}"
        try:
            self.db.execute_query(
                "INSERT INTO routes (route_number, route_name) VALUES (%s, %s)",
                (route_number, route_name)
            )
            self.load_routes()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить маршрут: {str(e)}")

    def edit_route_dialog(self):
        if not self.has_permission('routes', 'can_update'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на редактирование маршрутов.")
            return
        selected_row = self.routes_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите маршрут для редактирования")
            return

        route_id = self.routes_table.item(selected_row, 0).text()
        route = self.db.fetch_one("SELECT id, route_number, route_name FROM routes WHERE id = %s", (route_id,))

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать маршрут")
        layout = QFormLayout(dialog)
        route_number_input = QLineEdit(route['route_number'])
        route_name_input = QLineEdit(route['route_name'])
        layout.addRow("Номер маршрута:", route_number_input)
        layout.addRow("Название маршрута:", route_name_input)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.update_route(dialog, route_id, route_number_input.text(), route_name_input.text()))
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec_()

    def update_route(self, dialog, route_id, route_number, route_name):
        if not route_number or not route_name:
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля")
            return
        try:
            self.db.execute_query(
                "UPDATE routes SET route_number = %s, route_name = %s WHERE id = %s",
                (route_number, route_name, route_id)
            )
            self.load_routes()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось обновить маршрут: {str(e)}")

    def delete_route(self):
        if not self.has_permission('routes', 'can_delete'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на удаление маршрутов.")
            return
        row = self.routes_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите маршрут для удаления.")
            return
        route_id = self.routes_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удалить", "Удалить выбранный маршрут?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM routes WHERE id = %s", (route_id,))
                self.load_routes()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить маршрут: {str(e)}")

    # --- CRUD для остановок на маршруте ---
    def load_route_stops(self):
        route_stops = self.db.fetch_all("""
            SELECT rs.id, r.route_number, s.name, rs.stop_order
            FROM route_stops rs
            JOIN routes r ON rs.id_route = r.id
            JOIN stops s ON rs.id_stop = s.id
            ORDER BY rs.id
        """)
        self.route_stops_table.setColumnCount(4)
        self.route_stops_table.setHorizontalHeaderLabels(["ID", "Маршрут", "Остановка", "Порядок"])
        self.route_stops_table.setRowCount(len(route_stops))
        for row, rs in enumerate(route_stops):
            self.route_stops_table.setItem(row, 0, QTableWidgetItem(str(rs['id'])))
            self.route_stops_table.setItem(row, 1, QTableWidgetItem(str(rs['route_number'])))
            self.route_stops_table.setItem(row, 2, QTableWidgetItem(rs['name']))
            self.route_stops_table.setItem(row, 3, QTableWidgetItem(str(rs['stop_order'])))
        self.route_stops_table.resizeColumnsToContents()

    def add_route_stop_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить остановку на маршрут")
        layout = QFormLayout(dialog)
        # Выбор маршрута
        routes = self.db.fetch_all("SELECT id, route_number FROM routes ORDER BY route_number")
        route_combo = QComboBox()
        for route in routes:
            route_combo.addItem(str(route['route_number']), route['id'])
        # Выбор остановки
        stops = self.db.fetch_all("SELECT id, name FROM stops ORDER BY name")
        stop_combo = QComboBox()
        for stop in stops:
            stop_combo.addItem(stop['name'], stop['id'])
        stop_order_input = QLineEdit()
        layout.addRow("Маршрут:", route_combo)
        layout.addRow("Остановка:", stop_combo)
        layout.addRow("Порядок:", stop_order_input)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.save_route_stop(
            dialog,
            route_combo.currentData(),
            stop_combo.currentData(),
            stop_order_input.text()
        ))
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec_()

    def save_route_stop(self, dialog, route_id, stop_id, stop_order):
        if not route_id or not stop_id or not stop_order.isdigit():
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля корректно")
            return
        try:
            self.db.execute_query(
                "INSERT INTO route_stops (id_route, id_stop, stop_order) VALUES (%s, %s, %s)",
                (route_id, stop_id, int(stop_order))
            )
            self.load_route_stops()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить остановку на маршрут: {str(e)}")

    def edit_route_stop_dialog(self):
        if not self.has_permission('route_stops', 'can_update'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на редактирование.")
            return
        selected_row = self.route_stops_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите точку для редактирования")
            return

        route_stop_id = self.route_stops_table.item(selected_row, 0).text()
        route_stop = self.db.fetch_one("SELECT id, id_route, id_stop, stop_order FROM route_stops WHERE id = %s", (route_stop_id,))

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать точку на маршруте")
        layout = QFormLayout(dialog)

        # Выбор маршрута
        routes = self.db.fetch_all("SELECT id, route_number FROM routes ORDER BY route_number")
        route_combo = QComboBox()
        for route in routes:
            route_combo.addItem(str(route['route_number']), route['id'])
        route_combo.setCurrentIndex(next((i for i, r in enumerate(routes) if r['id'] == route_stop['id_route']), 0))

        # Выбор остановки
        stops = self.db.fetch_all("SELECT id, name FROM stops ORDER BY name")
        stop_combo = QComboBox()
        for stop in stops:
            stop_combo.addItem(stop['name'], stop['id'])
        stop_combo.setCurrentIndex(next((i for i, s in enumerate(stops) if s['id'] == route_stop['id_stop']), 0))

        stop_order_input = QLineEdit(str(route_stop['stop_order']))

        layout.addRow("Маршрут:", route_combo)
        layout.addRow("Остановка:", stop_combo)
        layout.addRow("Порядок:", stop_order_input)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.update_route_stop(
            dialog,
            route_stop_id,
            route_combo.currentData(),
            stop_combo.currentData(),
            stop_order_input.text()
        ))
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec_()

    def update_route_stop(self, dialog, route_stop_id, id_route, id_stop, stop_order):
        if not id_route or not id_stop or not stop_order.isdigit():
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля корректно")
            return
        try:
            self.db.execute_query(
                "UPDATE route_stops SET id_route = %s, id_stop = %s, stop_order = %s WHERE id = %s",
                (id_route, id_stop, int(stop_order), route_stop_id)
            )
            self.load_route_stops()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось обновить точку: {str(e)}")

    # --- CRUD для назначений ---
    def load_assignments(self):
        assignments = self.db.fetch_all("SELECT * FROM bus_assignments ORDER BY id")
        self.assignments_table.setColumnCount(len(assignments[0]) if assignments else 0)
        self.assignments_table.setHorizontalHeaderLabels(assignments[0].keys() if assignments else [])
        self.assignments_table.setRowCount(len(assignments))
        for row, assignment in enumerate(assignments):
            for col, key in enumerate(assignment):
                self.assignments_table.setItem(row, col, QTableWidgetItem(str(assignment[key])))
        self.assignments_table.resizeColumnsToContents()

    def add_assignment_dialog(self):
        if not self.has_permission('bus_assignments', 'can_insert'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на добавление назначений.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить назначение")
        layout = QFormLayout(dialog)

        routes = self.db.fetch_all("SELECT id, route_number FROM routes ORDER BY route_number")
        route_combo = QComboBox()
        for route in routes:
            route_combo.addItem(str(route['route_number']), route['id'])

        buses = self.db.fetch_all("SELECT id, mark, model, registration_number FROM buses ORDER BY id")
        bus_combo = QComboBox()
        for bus in buses:
            bus_combo.addItem(f"{bus['mark']} {bus['model']} ({bus['registration_number']})", bus['id'])

        assignment_date_input = QLineEdit()
        start_time_input = QLineEdit()
        end_time_input = QLineEdit()
        status_combo = QComboBox()
        for status in ['scheduled', 'in_progress', 'completed', 'cancelled']:
            status_combo.addItem(status)

        layout.addRow("Маршрут:", route_combo)
        layout.addRow("Автобус:", bus_combo)
        layout.addRow("Дата назначения:", assignment_date_input)
        layout.addRow("Время начала:", start_time_input)
        layout.addRow("Время окончания:", end_time_input)
        layout.addRow("Статус:", status_combo)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.save_assignment(
            dialog,
            route_combo.currentData(),
            bus_combo.currentData(),
            assignment_date_input.text(),
            start_time_input.text(),
            end_time_input.text(),
            status_combo.currentText()
        ))
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec_()

    def save_assignment(self, dialog, id_route, id_bus, assignment_date, start_time, end_time, status):
        if not id_route or not id_bus or not assignment_date or not start_time or not end_time or not status:
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля")
            return
        try:
            self.db.execute_query(
                "INSERT INTO bus_assignments (id_route, id_bus, assignment_date, start_time, end_time, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (id_route, id_bus, assignment_date, start_time, end_time, status)
            )
            self.load_assignments()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить назначение: {str(e)}")

    def edit_assignment_dialog(self):
        if not self.has_permission('bus_assignments', 'can_update'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на редактирование назначений.")
            return
        selected_row = self.assignments_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите назначение для редактирования")
            return

        assignment_id = self.assignments_table.item(selected_row, 0).text()
        assignment = self.db.fetch_one("SELECT * FROM bus_assignments WHERE id = %s", (assignment_id,))

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать назначение")
        layout = QFormLayout(dialog)

        # Маршрут
        routes = self.db.fetch_all("SELECT id, route_number FROM routes ORDER BY route_number")
        route_combo = QComboBox()
        for route in routes:
            route_combo.addItem(str(route['route_number']), route['id'])
        route_combo.setCurrentIndex(next((i for i, r in enumerate(routes) if r['id'] == assignment['id_route']), 0))

        # Автобус
        buses = self.db.fetch_all("SELECT id, mark, model, registration_number FROM buses ORDER BY id")
        bus_combo = QComboBox()
        for bus in buses:
            bus_combo.addItem(f"{bus['mark']} {bus['model']} ({bus['registration_number']})", bus['id'])
        bus_combo.setCurrentIndex(next((i for i, b in enumerate(buses) if b['id'] == assignment['id_bus']), 0))

        assignment_date_input = QLineEdit(str(assignment['assignment_date']))
        start_time_input = QLineEdit(str(assignment['start_time']))
        end_time_input = QLineEdit(str(assignment['end_time']))
        status_combo = QComboBox()
        for status in ['scheduled', 'in_progress', 'completed', 'cancelled']:
            status_combo.addItem(status)
        status_combo.setCurrentText(assignment['status'])

        layout.addRow("Маршрут:", route_combo)
        layout.addRow("Автобус:", bus_combo)
        layout.addRow("Дата назначения:", assignment_date_input)
        layout.addRow("Время начала:", start_time_input)
        layout.addRow("Время окончания:", end_time_input)
        layout.addRow("Статус:", status_combo)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(lambda: self.update_assignment(
            dialog,
            assignment_id,
            route_combo.currentData(),
            bus_combo.currentData(),
            assignment_date_input.text(),
            start_time_input.text(),
            end_time_input.text(),
            status_combo.currentText()
        ))
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)
        dialog.exec_()

    def update_assignment(self, dialog, assignment_id, id_route, id_bus, assignment_date, start_time, end_time, status):
        if not id_route or not id_bus or not assignment_date or not start_time or not end_time or not status:
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля")
            return
        try:
            self.db.execute_query(
                "UPDATE bus_assignments SET id_route = %s, id_bus = %s, assignment_date = %s, start_time = %s, end_time = %s, status = %s WHERE id = %s",
                (id_route, id_bus, assignment_date, start_time, end_time, status, assignment_id)
            )
            self.load_assignments()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось обновить назначение: {str(e)}")

    def delete_assignment(self):
        if not self.has_permission('bus_assignments', 'can_delete'):
            QMessageBox.warning(self, "Нет доступа", "У вас нет прав на удаление.")
            return
        row = self.assignments_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите назначение для удаления.")
            return
        assignment_id = self.assignments_table.item(row, 0).text()
        reply = QMessageBox.question(self, "Удалить", "Удалить выбранное назначение?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.execute_query("DELETE FROM bus_assignments WHERE id = %s", (assignment_id,))
                self.load_assignments()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить назначение: {str(e)}")

class MapPointDialog(QDialog):
    def __init__(self, api_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите точку на карте")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)
        self.view = QWebEngineView()
        layout.addWidget(self.view)
        self.coords = None

        html = get_yandex_map_html(api_key)
        self.view.setHtml(html)

        # Слушаем изменение title (там будут координаты)
        self.view.titleChanged.connect(self.on_title_changed)

    def on_title_changed(self, title):
        try:
            lat, lon = map(float, title.split(','))
            self.coords = (lat, lon)
            self.accept()
        except Exception:
            pass

    @staticmethod
    def get_point(api_key, parent=None):
        dlg = MapPointDialog(api_key, parent)
        if dlg.exec_() == QDialog.Accepted and dlg.coords:
            return dlg.coords
        return None

def get_yandex_map_html(api_key):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <title>Выбор точки на карте</title>
        <script src="https://api-maps.yandex.ru/2.1/?apikey={api_key}&lang=ru_RU"></script>
        <style>
            html, body, #map {{
                width: 100%; height: 100%; margin: 0; padding: 0;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            ymaps.ready(function () {{
                var map = new ymaps.Map('map', {{
                    center: [55.75, 37.61],
                    zoom: 10
                }});
                var marker = null;
                map.events.add('click', function (e) {{
                    var coords = e.get('coords');
                    if (marker) {{
                        marker.geometry.setCoordinates(coords);
                    }} else {{
                        marker = new ymaps.Placemark(coords, {{}}, {{preset: 'islands#redDotIcon'}});
                        map.geoObjects.add(marker);
                    }}
                    // Передаем координаты в PyQt через title документа
                    document.title = coords[0] + ',' + coords[1];
                }});
            }});
        </script>
    </body>
    </html>
    """