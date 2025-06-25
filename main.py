import sys
from PyQt5.QtWidgets import QApplication
from GIU import BusDepotApp
from WelcomeDialog import WelcomeDialog

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # --- Подключение QSS из файла ---
    with open("style.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    # --- конец QSS ---

    window = BusDepotApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

