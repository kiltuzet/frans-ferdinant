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
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
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
        self.stops_layout.addWidget(btn_update_stops)
        self.stops_layout.addWidget(btn_add_stop)
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
        self.routes_layout.addWidget(btn_update_routes)
        self.routes_layout.addWidget(btn_add_route)
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
        self.route_stops_layout.addWidget(btn_update_route_stops)
        self.route_stops_layout.addWidget(btn_add_route_stop)
        self.tabs.addTab(self.route_stops_tab, "Остановки на маршруте")

        # Вкладка назначений
        self.assignments_tab = QWidget()
        self.assignments_layout = QVBoxLayout(self.assignments_tab)
        self.assignments_table = QTableWidget()
        self.assignments_layout.addWidget(self.assignments_table)
        btn_update_assignments = QPushButton("Обновить назначения")
        btn_update_assignments.clicked.connect(self.load_assignments)
        self.assignments_layout.addWidget(btn_update_assignments)
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