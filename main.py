import sys
from PyQt5.QtWidgets import QApplication
from GIU import BusDepotApp
from WelcomeDialog import WelcomeDialog

def main():
    app = QApplication(sys.argv)
    
    # Настройка стиля
    app.setStyle('Fusion')

    # --- Добавьте QSS-стиль ---
    app.setStyleSheet("""
        QMainWindow, QDialog, QWidget {
            background-color: #f6f8fa;
            font-family: Segoe UI, Arial, sans-serif;
            font-size: 13px;
        }
        QTabWidget::pane {
            border: 1px solid #6ec6d4;
            background: #e9ecef;
        }
        QTabBar::tab {
            background: #e9ecef;
            color: #333;
            padding: 8px 20px;
            border: 1px solid #57b7c1;
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
            color: #0078d7;
            font-weight: bold;
        }
        QTableWidget, QTreeWidget {
            background: #ffffff;
            alternate-background-color: #f0f4f8;
            gridline-color: #d0d7de;
            selection-background-color: #cce6ff;
            selection-color: #222;
        }
        QHeaderView::section {
            background: #e9ecef;
            color: #333;
            padding: 4px;
            border: 1px solid #57cbc4;
        }
        QPushButton {
            background-color: #0078d7;
            color: #fff;
            border-radius: 5px;
            padding: 6px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #005fa3;
        }
        QPushButton:pressed {
            background-color: #003e6b;
        }
        QLineEdit, QComboBox, QDateTimeEdit {
            background: #fff;
            border: 1px solid #6ec6d4;
            border-radius: 4px;
            padding: 4px 8px;
        }
        QLabel {
            color: #222;
        }
        QDialogButtonBox QPushButton {
            min-width: 80px;
        }
        QGroupBox {
            border: 1px solid #6ec6d4;
            border-radius: 6px;
            margin-top: 8px;
        }
        QGroupBox:title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        QMessageBox {
            background: #fff;
        }
    """)
    # --- конец QSS ---

    window = BusDepotApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

