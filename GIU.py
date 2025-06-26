from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QTabWidget, QDateTimeEdit,QShortcut,QDialog
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QKeySequence, QIcon
from db import Database
from admin import AdminLoginDialog,AdminPanel
from WelcomeDialog import WelcomeDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import os
from PyQt5.QtCore import QUrl
from ManagerPanel import ManagerPanel

class BusDepotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle("Автобусный парк")
        self.setGeometry(100, 100, 900, 600)
        
        self.admin_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        self.admin_shortcut.activated.connect(self.show_admin_login)

        self.manager_shortcut = QShortcut(QKeySequence("Ctrl+Shift+M"), self)
        self.manager_shortcut.activated.connect(self.show_manager_panel)

        self.init_ui()
        
        welcome = WelcomeDialog(self)
        welcome.exec_()
        
        self.load_data()
    
    def init_ui(self):
        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Табы для разных функций
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Вкладка просмотра автобусов
        self.create_buses_tab()
        
        # Вкладка маршрутов
        self.create_routes_tab()
        
        # Вкладка бронирования
        self.create_booking_tab()
        
        # Вкладка поиска
        self.create_search_tab()
    
     
    def show_admin_login(self):
        login_dialog = AdminLoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            admin_panel = AdminPanel(self.db, self)
            admin_panel.exec_()

    def show_manager_panel(self):
        manager_panel = ManagerPanel(self.db, self)
        manager_panel.exec_()

    def create_buses_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Таблица автобусов
        self.buses_table = QTableWidget()
        self.buses_table.setColumnCount(6)
        self.buses_table.setHorizontalHeaderLabels([
            "ID", "Марка", "Модель", "Год", "Вместимость", "Статус"
        ])
        self.buses_table.setAlternatingRowColors(True)
        self.buses_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.buses_table.setToolTip("Список автобусов")
        layout.addWidget(self.buses_table)
        
        # Кнопка обновления
        btn_refresh = QPushButton("Обновить данные")
        btn_refresh.setToolTip("Обновить данные автобусов")
        btn_refresh.setIcon(QIcon("icons/refresh.png"))  # если есть иконка
        btn_refresh.clicked.connect(self.load_buses)
        layout.addWidget(btn_refresh)
        
        self.tabs.addTab(tab, "Автобусы")
    
    def create_routes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Комбобокс для выбора маршрута
        self.route_combo = QComboBox()
        self.route_combo.currentIndexChanged.connect(self.load_route_details)
        layout.addWidget(QLabel("Выберите маршрут:"))
        layout.addWidget(self.route_combo)
        
        # Таблица остановок маршрута
        self.stops_table = QTableWidget()
        self.stops_table.setColumnCount(4)
        self.stops_table.setHorizontalHeaderLabels([
            "Порядок", "Название", "Адрес", "Время прибытия"
        ])
        layout.addWidget(self.stops_table)

        # Виджет для карты
        self.route_map_view = QWebEngineView()
        self.route_map_view.setMinimumHeight(350)
        layout.addWidget(self.route_map_view)
        
        self.tabs.addTab(tab, "Маршруты")
    
    def create_booking_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Форма бронирования
        form_layout = QVBoxLayout()
        
        # Выбор маршрута
        self.booking_route_combo = QComboBox()
        self.booking_route_combo.currentIndexChanged.connect(self.update_stop_combos)
        form_layout.addWidget(QLabel("Маршрут:"))
        form_layout.addWidget(self.booking_route_combo)
        
        # Выбор остановки отправления
        self.departure_stop_combo = QComboBox()
        form_layout.addWidget(QLabel("Остановка отправления:"))
        form_layout.addWidget(self.departure_stop_combo)
        
        # Выбор остановки назначения
        self.arrival_stop_combo = QComboBox()
        form_layout.addWidget(QLabel("Остановка назначения:"))
        form_layout.addWidget(self.arrival_stop_combo)
        
        # Дата и время
        self.booking_datetime = QDateTimeEdit()
        self.booking_datetime.setDateTime(QDateTime.currentDateTime())
        form_layout.addWidget(QLabel("Дата и время:"))
        form_layout.addWidget(self.booking_datetime)
        
        # Количество билетов
        self.tickets_count = QLineEdit("1")
        self.tickets_count.setPlaceholderText("Введите количество билетов")
        form_layout.addWidget(QLabel("Количество билетов:"))
        form_layout.addWidget(self.tickets_count)
        
        # Кнопка бронирования
        btn_book = QPushButton("Забронировать")
        btn_book.clicked.connect(self.book_tickets)
        form_layout.addWidget(btn_book)
        
        layout.addLayout(form_layout)

        # Виджет для карты остановок
        self.booking_map_view = QWebEngineView()
        self.booking_map_view.setMinimumHeight(300)
        layout.addWidget(self.booking_map_view)
        
        self.tabs.addTab(tab, "Бронирование")
    
    def create_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Поле поиска
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите маршрут, автобус или остановку...")
        layout.addWidget(self.search_input)
        
        # Кнопка поиска
        btn_search = QPushButton("Поиск")
        btn_search.clicked.connect(self.perform_search)
        layout.addWidget(btn_search)
        
        # Результаты поиска
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(4)
        self.search_results.setHorizontalHeaderLabels([
            "Тип", "Название", "Описание", "Детали"
        ])
        layout.addWidget(self.search_results)
        
        self.tabs.addTab(tab, "Поиск")
    
    def load_data(self):
        self.load_buses()
        self.load_routes()
        self.load_booking_routes()
    
    def load_buses(self):
        buses = self.db.fetch_all("""
            SELECT id, mark, model, year, capacity, status 
            FROM buses 
            WHERE status != 'decommissioned'
            ORDER BY mark, model
        """)
        
        self.buses_table.setRowCount(len(buses))
        for row_idx, bus in enumerate(buses):
            self.buses_table.setItem(row_idx, 0, QTableWidgetItem(str(bus['id'])))
            self.buses_table.setItem(row_idx, 1, QTableWidgetItem(bus['mark']))
            self.buses_table.setItem(row_idx, 2, QTableWidgetItem(bus['model']))
            self.buses_table.setItem(row_idx, 3, QTableWidgetItem(str(bus['year'])))
            self.buses_table.setItem(row_idx, 4, QTableWidgetItem(str(bus['capacity'])))
            self.buses_table.setItem(row_idx, 5, QTableWidgetItem(bus['status']))
        
        self.buses_table.resizeColumnsToContents()
    
    def load_routes(self):
        # Получаем все маршруты
        routes = self.db.fetch_all(
            "SELECT id, route_number, route_name, is_regular, base_fare FROM routes WHERE is_regular = 1 ORDER BY route_number"
        )

        self.route_combo.clear()
        for route in routes:
            # Если маршрут регулярный, добавляем стоимость в название
            if route.get('is_regular'):
                fare_str = f" (Стоимость: {route.get('base_fare', '—')} руб.)"
            else:
                fare_str = ""
            self.route_combo.addItem(
                f"{route['route_number']} - {route['route_name']}{fare_str}", route['id']
            )


    def load_route_details(self):
        route_id = self.route_combo.currentData()
        if not route_id:
            return

        # Получаем данные о маршруте
        route = self.db.fetch_one(
            "SELECT is_regular, base_fare FROM routes WHERE id = %s", (route_id,)
        )

        stops = self.db.fetch_all("""
            SELECT rs.stop_order, s.name, s.address, rs.arrival_time, s.latitude, s.longitude
            FROM route_stops rs
            JOIN stops s ON rs.id_stop = s.id
            WHERE rs.id_route = %s
            ORDER BY rs.stop_order
        """, (route_id,))

        self.stops_table.setRowCount(len(stops))
        for row_idx, stop in enumerate(stops):
            self.stops_table.setItem(row_idx, 0, QTableWidgetItem(str(stop['stop_order'])))
            self.stops_table.setItem(row_idx, 1, QTableWidgetItem(stop['name']))
            self.stops_table.setItem(row_idx, 2, QTableWidgetItem(stop['address']))
            self.stops_table.setItem(row_idx, 3, QTableWidgetItem(str(stop['arrival_time'])))
        self.stops_table.resizeColumnsToContents()
        points = [(stop['latitude'], stop['longitude']) for stop in stops if stop['latitude'] and stop['longitude']]
        if points:
            html = self.generate_yandex_map_html(points, '4d5eb61f-4a3e-4ddc-91e4-736be3b4fc63')
            self.route_map_view.setHtml(html)
        else:
            self.route_map_view.setHtml("<h3>Нет координат для построения маршрута</h3>")
    
        # Показываем стоимость, если маршрут регулярный
        if route and route.get('is_regular'):
            fare = route.get('base_fare', '—')
            if not hasattr(self, 'fare_label'):
                self.fare_label = QLabel()
                self.tabs.widget(1).layout().addWidget(self.fare_label)
            self.fare_label.setText(f"<b>Стоимость поездки: {fare} руб.</b>")
        elif hasattr(self, 'fare_label'):
            self.fare_label.setText("")
    
    def load_booking_routes(self):
        routes = self.db.fetch_all(
            "SELECT id, route_number, route_name FROM routes WHERE is_regular = 0 ORDER BY route_number"
        )
        self.booking_route_combo.blockSignals(True)  # Отключаем сигналы на время заполнения
        self.booking_route_combo.clear()
        for route in routes:
            self.booking_route_combo.addItem(f"{route['route_number']} - {route['route_name']}", route['id'])
        self.booking_route_combo.blockSignals(False)  # Включаем обратно

        # Можно явно вызвать обновление, если нужно:
        self.update_stop_combos()
    
    def update_stop_combos(self):
        route_id = self.booking_route_combo.currentData()
        if not route_id:
            return

        stops = self.db.fetch_all("""
            SELECT s.id, s.name, rs.stop_order, s.latitude, s.longitude
            FROM route_stops rs
            JOIN stops s ON rs.id_stop = s.id
            WHERE rs.id_route = %s
            ORDER BY rs.stop_order
        """, (route_id,))

        self.departure_stop_combo.clear()
        self.arrival_stop_combo.clear()

        points = []
        for stop in stops:
            self.departure_stop_combo.addItem(stop['name'], stop['id'])
            self.arrival_stop_combo.addItem(stop['name'], stop['id'])
            print(stop['latitude'])
            print(stop['longitude'])
            if stop['latitude'] and stop['longitude']:
                points.append((stop['latitude'], stop['longitude']))
                #print(points)
        # Карта остановок
        from dotenv import load_dotenv
        import os
        load_dotenv()
        api_key = os.getenv("YANDEX_API_KEY").replace('"', '').replace("'", "")
        if points:
            html = self.generate_yandex_map_html(points, api_key)
            self.booking_map_view.setHtml(html)
        else:
            self.booking_map_view.setHtml("<h3>Нет координат для построения карты</h3>")

        # Информация о стоимости билета
        route = self.db.fetch_one(
            "SELECT base_fare FROM routes WHERE id = %s", (route_id,)
        )
        if not hasattr(self, 'booking_fare_label'):
            self.booking_fare_label = QLabel()
            self.tabs.widget(2).layout().addWidget(self.booking_fare_label)
        if route and route.get('base_fare') is not None:
            self.booking_fare_label.setText(f"<b>Стоимость билета: {route['base_fare']} руб.</b>")
        else:
            self.booking_fare_label.setText("Стоимость билета: —")
    
    def book_tickets(self):
        route_id = self.booking_route_combo.currentData()
        departure_stop_id = self.departure_stop_combo.currentData()
        arrival_stop_id = self.arrival_stop_combo.currentData()
        booking_time = self.booking_datetime.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        try:
            tickets = int(self.tickets_count.text())
            if tickets <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректное количество билетов")
            return
        
        # Проверка, что выбраны разные остановки
        if departure_stop_id == arrival_stop_id:
            QMessageBox.warning(self, "Ошибка", "Выберите разные остановки для отправления и назначения")
            return
        
        # Получаем информацию о маршруте для расчета стоимости
        route_id = self.booking_route_combo.currentData()
        print("route_id:", route_id)
        if not route_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран маршрут")
            return

        route = self.db.fetch_one("SELECT base_fare FROM routes WHERE id = %s", (route_id,))
        print("Route:", route)
        if not route:
            QMessageBox.warning(self, "Ошибка", "Маршрут не найден")
            return
        
        # Расчет стоимости (примерный расчет)
        fare=route['base_fare']*tickets
        # / tickets
        # Добавление записи о пассажирах
        for _ in range(tickets):
            self.db.execute_query("""
                INSERT INTO passengers 
                (id_route, boarding_time, ticket_number, fare)
                VALUES (%s, %s, %s, %s)
            """, (
                route_id,
                booking_time,
                f"TKT-{route_id}-{departure_stop_id}-{arrival_stop_id}",
                fare
            ))
        
        QMessageBox.information(
            self, 
            "Успешно", 
            f"Забронировано {tickets} билет(а) на маршрут {self.booking_route_combo.currentText()}\n"
            f"Стоимость: {fare} руб.\n"
            f"Отправление: {self.departure_stop_combo.currentText()}\n"
            f"Прибытие: {self.arrival_stop_combo.currentText()}"
        )
    
    def perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        
        # Поиск по маршрутам
        routes = self.db.fetch_all("""
            SELECT 
                'Маршрут' AS type,
                route_number AS name,
                route_name AS description,
                CONCAT('Дистанция: ', distance_km, ' км') AS details
            FROM routes
            WHERE route_number LIKE %s OR route_name LIKE %s
        """, (f"%{query}%", f"%{query}%"))
        
        # Поиск по автобусам
        buses = self.db.fetch_all("""
            SELECT 
                'Автобус' AS type,
                CONCAT(mark, ' ', model) AS name,
                CONCAT('Вместимость: ', capacity) AS description,
                CONCAT('Гос. номер: ', registration_number) AS details
            FROM buses
            WHERE mark LIKE %s OR model LIKE %s OR registration_number LIKE %s
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        
        # Поиск по остановкам
        stops = self.db.fetch_all("""
            SELECT 
                'Остановка' AS type,
                name,
                address AS description,
                IF(is_terminal, 'Конечная', 'Промежуточная') AS details
            FROM stops
            WHERE name LIKE %s OR address LIKE %s
        """, (f"%{query}%", f"%{query}%"))
        
        # Объединяем результаты
        results = routes + buses + stops
        self.display_search_results(results)
    
    def display_search_results(self, results):
        self.search_results.setRowCount(len(results))
        for row_idx, item in enumerate(results):
            self.search_results.setItem(row_idx, 0, QTableWidgetItem(item['type']))
            self.search_results.setItem(row_idx, 1, QTableWidgetItem(item['name']))
            self.search_results.setItem(row_idx, 2, QTableWidgetItem(item['description']))
            self.search_results.setItem(row_idx, 3, QTableWidgetItem(item['details']))
        
        self.search_results.resizeColumnsToContents()
    
    def closeEvent(self, event):
        self.db.close()
        event.accept()

    def generate_yandex_map_html(self, points, api_key):
        # points: [(lat, lon), ...]
        points_js = ','.join(f'[{lat},{lon}]' for lat, lon in points)
        center = points[0] if points else [55.75, 37.61]  # Москва по умолчанию
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <title>Маршрут на Яндекс.Карте</title>
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
                        center: [{center[0]}, {center[1]}],
                        zoom: 12
                    }});
                    var points = [{points_js}];
                    if (points.length > 1) {{
                        var multiRoute = new ymaps.multiRouter.MultiRoute({{
                            referencePoints: points,
                            params: {{
                                routingMode: 'auto'
                            }}
                        }}, {{
                            boundsAutoApply: true
                        }});
                        map.geoObjects.add(multiRoute);
                    }} else if (points.length === 1) {{
                        map.geoObjects.add(new ymaps.Placemark(points[0]));
                    }}
                }});
            </script>
        </body>
        </html>
        """
        return html